from __future__ import annotations

import json
import socket
import struct
import uuid
from typing import Any

from robotstudio_mcp.audit import AuditLogger
from robotstudio_mcp.bridge.contracts import METHOD_NAMES
from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.settings import Settings


class BridgeClient:
    """One-request-per-connection client for the local length-prefixed bridge."""

    def __init__(self, settings: Settings, audit: AuditLogger | None = None) -> None:
        self.settings = settings
        self.audit = audit

    def _load_token(self) -> str:
        path = self.settings.token_file
        try:
            token = path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RobotStudioMcpError(
                "RS_BRIDGE_AUTH_FAILED",
                "Bridge token is unavailable. Run the extension installer first.",
                {"token_file": str(path)},
                retryable=True,
            ) from exc
        if len(token) < 32:
            raise RobotStudioMcpError("RS_BRIDGE_AUTH_FAILED", "Bridge token is invalid or too short.", retryable=True)
        return token

    @staticmethod
    def _receive_exact(sock: socket.socket, size: int) -> bytes:
        chunks: list[bytes] = []
        remaining = size
        while remaining:
            chunk = sock.recv(remaining)
            if not chunk:
                raise RobotStudioMcpError(
                    "RS_BRIDGE_PROTOCOL_ERROR",
                    "Bridge closed the connection before returning a complete frame.",
                    retryable=True,
                )
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    def call(
        self, method: str, params: dict[str, Any] | None = None, timeout_seconds: float | None = None
    ) -> dict[str, Any]:
        if method not in METHOD_NAMES:
            raise RobotStudioMcpError(
                "RS_CAPABILITY_NOT_AVAILABLE",
                "The requested bridge method is not in the Phase 0/1 allowlist.",
                {"method": method},
            )
        timeout = timeout_seconds or self.settings.bridge_request_timeout_seconds
        request_id = uuid.uuid4().hex
        request = {
            "request_id": request_id,
            "token": self._load_token(),
            "method": method,
            "params": params or {},
            "timeout_ms": min(300_000, max(1_000, round(timeout * 1000))),
            "client": "robotstudio-mcp/0.1.0",
        }
        payload = json.dumps(request, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(payload) > self.settings.bridge_max_payload_bytes:
            raise RobotStudioMcpError(
                "RS_PAYLOAD_TOO_LARGE",
                "Bridge request exceeds the configured maximum payload.",
                {"size": len(payload), "maximum": self.settings.bridge_max_payload_bytes},
            )
        try:
            with socket.create_connection(
                (self.settings.bridge_host, self.settings.bridge_port),
                timeout=self.settings.bridge_connect_timeout_seconds,
            ) as sock:
                sock.settimeout(timeout)
                sock.sendall(struct.pack("!I", len(payload)) + payload)
                response_size = struct.unpack("!I", self._receive_exact(sock, 4))[0]
                if response_size <= 0 or response_size > self.settings.bridge_max_payload_bytes:
                    raise RobotStudioMcpError(
                        "RS_BRIDGE_PROTOCOL_ERROR",
                        "Bridge response frame length is invalid.",
                        {"size": response_size},
                    )
                response = json.loads(self._receive_exact(sock, response_size).decode("utf-8"))
        except RobotStudioMcpError:
            raise
        except (ConnectionError, TimeoutError, OSError) as exc:
            raise RobotStudioMcpError(
                "RS_BRIDGE_OFFLINE",
                "RobotStudio Add-In bridge is offline or did not respond in time.",
                {"host": self.settings.bridge_host, "port": self.settings.bridge_port},
                retryable=True,
            ) from exc
        except (UnicodeDecodeError, json.JSONDecodeError, struct.error) as exc:
            raise RobotStudioMcpError(
                "RS_BRIDGE_PROTOCOL_ERROR", "Bridge returned an invalid response frame.", retryable=True
            ) from exc

        if not isinstance(response, dict) or response.get("request_id") != request_id:
            raise RobotStudioMcpError(
                "RS_BRIDGE_PROTOCOL_ERROR", "Bridge response request ID does not match the request.", retryable=True
            )
        if self.audit:
            self.audit.write(
                "bridge_call",
                operation=method,
                request_id=request_id,
                ok=bool(response.get("ok")),
                summary={"params": params or {}, "elapsed_ms": response.get("elapsed_ms")},
            )
        if not response.get("ok"):
            error = response.get("error") if isinstance(response.get("error"), dict) else {}
            raise RobotStudioMcpError(
                str(error.get("code") or "RS_BRIDGE_ERROR"),
                str(error.get("message") or "RobotStudio bridge operation failed."),
                error.get("details") if isinstance(error.get("details"), dict) else {},
                bool(error.get("retryable", False)),
            )
        return response

    def status(self) -> dict[str, Any]:
        try:
            response = self.call(
                "environment.ping", timeout_seconds=min(3.0, self.settings.bridge_request_timeout_seconds)
            )
        except RobotStudioMcpError as exc:
            return {
                "online": False,
                "host": self.settings.bridge_host,
                "port": self.settings.bridge_port,
                "error": exc.as_dict(),
            }
        return {
            "online": True,
            "host": self.settings.bridge_host,
            "port": self.settings.bridge_port,
            "bridge": response.get("result"),
            "elapsed_ms": response.get("elapsed_ms"),
        }
