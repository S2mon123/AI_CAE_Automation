from __future__ import annotations

from typing import Any

import pytest
from fastmcp import Client

from robotstudio_mcp.server import create_server
from robotstudio_mcp.settings import Settings


class FakeBridge:
    def call(
        self, method: str, params: dict[str, Any] | None = None, timeout_seconds: float | None = None
    ) -> dict[str, Any]:
        return {
            "request_id": "bridge-request",
            "ok": True,
            "result": {"method": method, "params": params or {}, "robotstudio_version": "25.3.11371.0"},
            "warnings": [],
            "evidence": [{"kind": "test", "source": "fake-bridge"}],
            "elapsed_ms": 1,
        }

    def status(self) -> dict[str, Any]:
        return {"online": True, "bridge": {"robotstudio_version": "25.3.11371.0"}}


@pytest.mark.asyncio
async def test_tools_resources_prompts_and_tool_call(settings: Settings) -> None:
    server = create_server(settings, FakeBridge())  # type: ignore[arg-type]
    async with Client(server) as client:
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()
        tool_names = {tool.name for tool in tools}
        resource_uris = {str(resource.uri) for resource in resources}
        prompt_names = {prompt.name for prompt in prompts}
        assert {"get_environment", "get_bridge_status", "get_station_summary", "get_controller_status"} <= tool_names
        assert (
            not {
                "connect_real_controller",
                "modify_station",
                "reset_program_pointer",
                "set_io_signal",
                "start_rapid",
                "stop_rapid",
                "write_rapid_module",
            }
            & tool_names
        )
        assert "robotstudio://environment" in resource_uris
        assert {"inspect_station", "inspect_virtual_controller", "verify_phase_0_1"} <= prompt_names
        result = await client.call_tool("get_station_summary", {})
        assert result.data["ok"] is True
        assert result.data["result"]["method"] == "station.summary"
