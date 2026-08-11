from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from robotstudio_mcp.errors import RobotStudioMcpError


def _default_local_app_data() -> Path:
    value = os.environ.get("LOCALAPPDATA")
    if value:
        return Path(value)
    return Path.home() / "AppData" / "Local"


def _read_shared_config(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RobotStudioMcpError(
            "RS_CONFIG_INVALID",
            "The shared RobotStudio MCP bridge configuration is invalid.",
            {"path": str(path), "reason": str(exc)},
        ) from exc
    if not isinstance(value, dict):
        raise RobotStudioMcpError("RS_CONFIG_INVALID", "Bridge configuration must be a JSON object.")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    workspace: Path
    bridge_host: str
    bridge_port: int
    token_file: Path
    bridge_connect_timeout_seconds: float
    bridge_request_timeout_seconds: float
    bridge_max_payload_bytes: int
    controller_scope: str
    installation_override: Path | None
    shared_config_file: Path

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> Settings:
        env = os.environ if environ is None else environ
        local_root = Path(env.get("LOCALAPPDATA") or _default_local_app_data()) / "RobotStudioMCP"
        shared_config_file = Path(env.get("ROBOTSTUDIO_MCP_CONFIG_FILE") or local_root / "bridge-settings.json")
        shared = _read_shared_config(shared_config_file)

        workspace = Path(
            env.get("ROBOTSTUDIO_MCP_WORKSPACE")
            or shared.get("workspace")
            or (Path.home() / "Documents" / "RobotStudioMCP" / "workspace")
        ).expanduser()
        host = str(env.get("ROBOTSTUDIO_MCP_BRIDGE_HOST") or shared.get("host") or "127.0.0.1")
        if host != "127.0.0.1":
            raise RobotStudioMcpError(
                "RS_CONFIG_INVALID",
                "The Add-In bridge must bind to and be reached through 127.0.0.1.",
                {"host": host},
            )

        try:
            port = int(env.get("ROBOTSTUDIO_MCP_BRIDGE_PORT") or shared.get("port") or 47625)
            connect_timeout = float(env.get("ROBOTSTUDIO_MCP_CONNECT_TIMEOUT") or 2.0)
            request_timeout = float(env.get("ROBOTSTUDIO_MCP_REQUEST_TIMEOUT") or 30.0)
            max_payload = int(env.get("ROBOTSTUDIO_MCP_MAX_PAYLOAD") or shared.get("max_payload_bytes") or 4_194_304)
        except (TypeError, ValueError) as exc:
            raise RobotStudioMcpError("RS_CONFIG_INVALID", "A numeric bridge setting is invalid.") from exc
        if not 1024 <= port <= 65535:
            raise RobotStudioMcpError("RS_CONFIG_INVALID", "Bridge port must be between 1024 and 65535.")
        if not 0.1 <= connect_timeout <= 30:
            raise RobotStudioMcpError("RS_CONFIG_INVALID", "Connect timeout must be between 0.1 and 30 seconds.")
        if not 1 <= request_timeout <= 300:
            raise RobotStudioMcpError("RS_CONFIG_INVALID", "Request timeout must be between 1 and 300 seconds.")
        if not 1024 <= max_payload <= 16_777_216:
            raise RobotStudioMcpError("RS_CONFIG_INVALID", "Maximum payload must be between 1 KiB and 16 MiB.")

        controller_scope = str(
            env.get("ROBOTSTUDIO_MCP_CONTROLLER_SCOPE") or shared.get("controller_scope") or "virtual_only"
        )
        if controller_scope != "virtual_only":
            raise RobotStudioMcpError(
                "RS_CONFIG_INVALID",
                "Phase 0/1 supports only controller_scope=virtual_only.",
                {"controller_scope": controller_scope},
            )

        token_file = Path(
            env.get("ROBOTSTUDIO_MCP_TOKEN_FILE") or shared.get("token_file") or (local_root / "bridge-token")
        ).expanduser()
        install_value = env.get("ROBOTSTUDIO_INSTALL_DIR") or shared.get("robotstudio_install_dir")
        install_override = Path(str(install_value)).expanduser() if install_value else None

        if not workspace.is_absolute() or not token_file.is_absolute():
            raise RobotStudioMcpError("RS_CONFIG_INVALID", "Workspace and token file paths must be absolute.")
        if install_override is not None and not install_override.is_absolute():
            raise RobotStudioMcpError("RS_CONFIG_INVALID", "RobotStudio installation override must be absolute.")

        return cls(
            workspace=workspace.resolve(strict=False),
            bridge_host=host,
            bridge_port=port,
            token_file=token_file.resolve(strict=False),
            bridge_connect_timeout_seconds=connect_timeout,
            bridge_request_timeout_seconds=request_timeout,
            bridge_max_payload_bytes=max_payload,
            controller_scope=controller_scope,
            installation_override=install_override.resolve(strict=False) if install_override else None,
            shared_config_file=shared_config_file.resolve(strict=False),
        )

    def ensure_workspace(self) -> None:
        self.workspace.mkdir(parents=True, exist_ok=True)
        (self.workspace / "projects").mkdir(exist_ok=True)
        (self.workspace / "logs").mkdir(exist_ok=True)
