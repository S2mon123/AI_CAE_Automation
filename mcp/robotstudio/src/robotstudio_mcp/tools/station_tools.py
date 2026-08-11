from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from robotstudio_mcp.app import AppContext
from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.result_models import OperationTimer
from robotstudio_mcp.tools.common import bridge_operation, finish_failure, pagination


def _paged_operation(
    app: AppContext,
    operation: str,
    method: str,
    offset: int,
    limit: int,
) -> dict[str, Any]:
    timer = OperationTimer()
    try:
        offset, limit = pagination(offset, limit)
    except RobotStudioMcpError as exc:
        return finish_failure(app, operation, exc, timer=timer, scope="station")
    return bridge_operation(app, operation, method, {"offset": offset, "limit": limit}, scope="station")


def register_station_tools(mcp: FastMCP, app: AppContext) -> None:
    @mcp.tool(name="get_active_station")
    def get_active_station() -> dict[str, Any]:
        """Read the identity, source file, dirty state, and active task of the actual active Station."""
        return bridge_operation(app, "get_active_station", "station.active", scope="station")

    @mcp.tool(name="get_station_summary")
    def get_station_summary() -> dict[str, Any]:
        """Read counts and identities from the actual active Station object model."""
        return bridge_operation(app, "get_station_summary", "station.summary", scope="station")

    @mcp.tool(name="list_station_components")
    def list_station_components(offset: int = 0, limit: int = 200) -> dict[str, Any]:
        """Page through actual Station ProjectObjects without mutating selection or visibility."""
        return _paged_operation(app, "list_station_components", "station.components", offset, limit)

    @mcp.tool(name="list_robots")
    def list_robots(offset: int = 0, limit: int = 200) -> dict[str, Any]:
        """List mechanical units and Mechanism objects in the active Station."""
        return _paged_operation(app, "list_robots", "station.robots", offset, limit)

    @mcp.tool(name="get_robot_info")
    def get_robot_info(name: str) -> dict[str, Any]:
        """Read model, joint, transform, and controller association for one Station robot."""
        return bridge_operation(app, "get_robot_info", "station.robot", {"name": name}, scope="station")

    @mcp.tool(name="list_tools")
    def list_tools(offset: int = 0, limit: int = 200) -> dict[str, Any]:
        """List actual RsToolData declarations and frames from the active Station."""
        return _paged_operation(app, "list_tools", "station.tools", offset, limit)

    @mcp.tool(name="list_workobjects")
    def list_workobjects(offset: int = 0, limit: int = 200) -> dict[str, Any]:
        """List actual RsWorkObject declarations and frames from the active Station."""
        return _paged_operation(app, "list_workobjects", "station.workobjects", offset, limit)

    @mcp.tool(name="list_targets")
    def list_targets(offset: int = 0, limit: int = 200) -> dict[str, Any]:
        """List actual Station targets, RobTarget declarations, and JointTarget declarations."""
        return _paged_operation(app, "list_targets", "station.targets", offset, limit)

    @mcp.tool(name="get_target")
    def get_target(name: str, module_name: str | None = None) -> dict[str, Any]:
        """Read one target's pose, configuration, external axes, workobject, and declaration scope."""
        return bridge_operation(
            app,
            "get_target",
            "station.target",
            {"name": name, "module_name": module_name},
            scope="station",
        )

    @mcp.tool(name="list_paths")
    def list_paths(offset: int = 0, limit: int = 200) -> dict[str, Any]:
        """List actual RsPathProcedure objects and instruction counts."""
        return _paged_operation(app, "list_paths", "station.paths", offset, limit)

    @mcp.tool(name="get_path")
    def get_path(name: str, module_name: str | None = None) -> dict[str, Any]:
        """Read one path's actual instructions and target/tool/workobject references."""
        return bridge_operation(
            app,
            "get_path",
            "station.path",
            {"name": name, "module_name": module_name},
            scope="station",
        )
