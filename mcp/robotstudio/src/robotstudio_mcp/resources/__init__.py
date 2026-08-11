"""Read-only MCP resource registration."""

from typing import Any

from fastmcp import FastMCP

from robotstudio_mcp.app import AppContext
from robotstudio_mcp.bridge.contracts import capability_document
from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.policies.safety import safety_policy
from robotstudio_mcp.result_models import OperationTimer
from robotstudio_mcp.tools.common import bridge_operation, finish_failure, finish_success


def register_resources(mcp: FastMCP, app: AppContext) -> None:
    @mcp.resource("robotstudio://environment", mime_type="application/json")
    def environment_resource() -> dict[str, Any]:
        value = app.environment.inspect()
        value["workspace"] = str(app.settings.workspace)
        value["controller_scope"] = app.settings.controller_scope
        return value

    @mcp.resource("robotstudio://capabilities", mime_type="application/json")
    def capabilities_resource() -> dict[str, Any]:
        value = capability_document()
        try:
            value["live"] = app.bridge.call("capabilities.get").get("result")
            value["bridge_online"] = True
        except RobotStudioMcpError as exc:
            value["live"] = None
            value["bridge_online"] = False
            value["bridge_error"] = exc.as_dict()
        return value

    @mcp.resource("robotstudio://bridge/status", mime_type="application/json")
    def bridge_status_resource() -> dict[str, Any]:
        return app.bridge.status()

    @mcp.resource("robotstudio://policy/safety", mime_type="application/json")
    def safety_resource() -> dict[str, Any]:
        return safety_policy()

    @mcp.resource("robotstudio://project/{project_id}", mime_type="application/json")
    def project_resource(project_id: str) -> dict[str, Any]:
        timer = OperationTimer()
        try:
            return finish_success(
                app,
                "read_project_resource",
                app.projects.summary(project_id),
                timer=timer,
                scope="project",
                project_id=project_id,
            )
        except RobotStudioMcpError as exc:
            return finish_failure(
                app, "read_project_resource", exc, timer=timer, scope="project", project_id=project_id
            )

    mappings = {
        "robotstudio://station/summary": ("resource_station_summary", "station.summary", "station", "none", {}),
        "robotstudio://station/robots": (
            "resource_station_robots",
            "station.robots",
            "station",
            "none",
            {"offset": 0, "limit": 1000},
        ),
        "robotstudio://station/tools": (
            "resource_station_tools",
            "station.tools",
            "station",
            "none",
            {"offset": 0, "limit": 1000},
        ),
        "robotstudio://station/workobjects": (
            "resource_station_workobjects",
            "station.workobjects",
            "station",
            "none",
            {"offset": 0, "limit": 1000},
        ),
        "robotstudio://station/targets": (
            "resource_station_targets",
            "station.targets",
            "station",
            "none",
            {"offset": 0, "limit": 1000},
        ),
        "robotstudio://station/paths": (
            "resource_station_paths",
            "station.paths",
            "station",
            "none",
            {"offset": 0, "limit": 1000},
        ),
        "robotstudio://controller/status": (
            "resource_controller_status",
            "controller.status",
            "controller",
            "controller_read",
            {},
        ),
        "robotstudio://controller/eventlog": (
            "resource_controller_eventlog",
            "controller.eventlog",
            "controller",
            "controller_read",
            {"start_sequence": 0, "limit": 100, "category_id": None},
        ),
        "robotstudio://controller/io": (
            "resource_controller_io",
            "controller.io",
            "controller",
            "controller_read",
            {"offset": 0, "limit": 1000},
        ),
        "robotstudio://rapid/tasks": (
            "resource_rapid_tasks",
            "rapid.tasks",
            "rapid",
            "controller_read",
            {},
        ),
    }

    def make_bridge_resource(
        operation: str,
        method: str,
        scope: str,
        side_effect: str,
        params: dict[str, Any],
    ) -> Any:
        def read_bridge_resource() -> dict[str, Any]:
            return bridge_operation(
                app,
                operation,
                method,
                params,
                scope=scope,
                side_effect=side_effect,
            )

        read_bridge_resource.__name__ = operation
        return read_bridge_resource

    for uri, (operation, method, scope, side_effect, params) in mappings.items():
        mcp.resource(uri, mime_type="application/json")(
            make_bridge_resource(operation, method, scope, side_effect, params)
        )
