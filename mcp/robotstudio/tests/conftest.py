from __future__ import annotations

from pathlib import Path

import pytest

from robotstudio_mcp.settings import Settings


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    token = tmp_path / "bridge-token"
    token.write_text("a" * 64, encoding="utf-8")
    return Settings(
        workspace=tmp_path / "workspace",
        bridge_host="127.0.0.1",
        bridge_port=47625,
        token_file=token,
        bridge_connect_timeout_seconds=0.2,
        bridge_request_timeout_seconds=2.0,
        bridge_max_payload_bytes=1024 * 1024,
        controller_scope="virtual_only",
        installation_override=None,
        shared_config_file=tmp_path / "bridge-settings.json",
    )
