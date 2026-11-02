from __future__ import annotations

from pathlib import Path

import pytest

from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.settings import Settings


def test_settings_reject_non_loopback(tmp_path: Path) -> None:
    with pytest.raises(RobotStudioMcpError, match="127.0.0.1"):
        Settings.from_env(
            {
                "LOCALAPPDATA": str(tmp_path),
                "ROBOTSTUDIO_MCP_WORKSPACE": str(tmp_path / "workspace"),
                "ROBOTSTUDIO_MCP_TOKEN_FILE": str(tmp_path / "token"),
                "ROBOTSTUDIO_MCP_BRIDGE_HOST": "0.0.0.0",
            }
        )


def test_settings_reject_real_controller_scope(tmp_path: Path) -> None:
    with pytest.raises(RobotStudioMcpError, match="virtual_only"):
        Settings.from_env(
            {
                "LOCALAPPDATA": str(tmp_path),
                "ROBOTSTUDIO_MCP_WORKSPACE": str(tmp_path / "workspace"),
                "ROBOTSTUDIO_MCP_TOKEN_FILE": str(tmp_path / "token"),
                "ROBOTSTUDIO_MCP_CONTROLLER_SCOPE": "all",
            }
        )
