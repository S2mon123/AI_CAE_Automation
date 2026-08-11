"""FastMCP tool registration."""

from fastmcp import FastMCP

from robotstudio_mcp.app import AppContext
from robotstudio_mcp.tools.controller_tools import register_controller_tools
from robotstudio_mcp.tools.environment_tools import register_environment_tools
from robotstudio_mcp.tools.project_tools import register_project_tools
from robotstudio_mcp.tools.station_tools import register_station_tools


def register_tools(mcp: FastMCP, app: AppContext) -> None:
    register_environment_tools(mcp, app)
    register_project_tools(mcp, app)
    register_station_tools(mcp, app)
    register_controller_tools(mcp, app)
