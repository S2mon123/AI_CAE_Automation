from __future__ import annotations

import json
import socket
import struct
import threading
from contextlib import closing
from pathlib import Path
from typing import Any

import pytest

from robotstudio_mcp.bridge.client import BridgeClient
from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.settings import Settings


def _receive_exact(sock: socket.socket, size: int) -> bytes:
    value = b""
    while len(value) < size:
        value += sock.recv(size - len(value))
    return value


def _one_shot_server(token: str, response_result: dict[str, Any]) -> tuple[int, threading.Thread]:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    port = listener.getsockname()[1]

    def run() -> None:
        with closing(listener):
            client, _ = listener.accept()
            with client:
                size = struct.unpack("!I", _receive_exact(client, 4))[0]
                request = json.loads(_receive_exact(client, size).decode("utf-8"))
                ok = request["token"] == token
                response = {
                    "request_id": request["request_id"],
                    "ok": ok,
                    "result": response_result if ok else None,
                    "error": None if ok else {"code": "RS_BRIDGE_AUTH_FAILED", "message": "bad token"},
                    "warnings": [],
                    "evidence": [],
                    "elapsed_ms": 1,
                }
                payload = json.dumps(response).encode("utf-8")
                client.sendall(struct.pack("!I", len(payload)) + payload)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return port, thread


def _with_port(settings: Settings, port: int, token_file: Path | None = None) -> Settings:
    return Settings(
        workspace=settings.workspace,
        bridge_host=settings.bridge_host,
        bridge_port=port,
        token_file=token_file or settings.token_file,
        bridge_connect_timeout_seconds=settings.bridge_connect_timeout_seconds,
        bridge_request_timeout_seconds=settings.bridge_request_timeout_seconds,
        bridge_max_payload_bytes=settings.bridge_max_payload_bytes,
        controller_scope=settings.controller_scope,
        installation_override=settings.installation_override,
        shared_config_file=settings.shared_config_file,
    )


def test_authenticated_ping(settings: Settings) -> None:
    port, thread = _one_shot_server("a" * 64, {"robotstudio_version": "25.3.11371.0"})
    result = BridgeClient(_with_port(settings, port)).call("environment.ping")
    thread.join(timeout=2)
    assert result["result"]["robotstudio_version"] == "25.3.11371.0"


def test_unknown_method_is_rejected_before_network(settings: Settings) -> None:
    with pytest.raises(RobotStudioMcpError, match="allowlist"):
        BridgeClient(settings).call("system.exec")


def test_missing_token_is_structured(settings: Settings, tmp_path: Path) -> None:
    with pytest.raises(RobotStudioMcpError) as caught:
        BridgeClient(_with_port(settings, settings.bridge_port, tmp_path / "missing")).call("environment.ping")
    assert caught.value.code == "RS_BRIDGE_AUTH_FAILED"


def test_offline_bridge_is_structured(settings: Settings) -> None:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        unused = probe.getsockname()[1]
    with pytest.raises(RobotStudioMcpError) as caught:
        BridgeClient(_with_port(settings, unused)).call("environment.ping")
    assert caught.value.code == "RS_BRIDGE_OFFLINE"
