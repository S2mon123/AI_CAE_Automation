from __future__ import annotations

from fastmcp import FastMCP

from robotstudio_mcp.app import AppContext
from robotstudio_mcp.bridge.client import BridgeClient
from robotstudio_mcp.instructions import SERVER_INSTRUCTIONS
from robotstudio_mcp.prompts import register_prompts
from robotstudio_mcp.resources import register_resources
from robotstudio_mcp.settings import Settings
from robotstudio_mcp.tools import register_tools


def create_server(settings: Settings | None = None, bridge: BridgeClient | None = None) -> FastMCP:
    resolved = settings or Settings.from_env()
    app = AppContext(resolved, bridge)
    mcp = FastMCP(name="robotstudio", instructions=SERVER_INSTRUCTIONS)
    register_tools(mcp, app)
    register_resources(mcp, app)
    register_prompts(mcp)
    return mcp


mcp = create_server()


def main() -> None:
    mcp.run(transport="stdio", show_banner=False)
