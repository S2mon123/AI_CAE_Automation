from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from robotstudio_mcp.app import AppContext
from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.result_models import OperationTimer
from robotstudio_mcp.tools.common import bridge_operation, finish_failure, pagination


def register_controller_tools(mcp: FastMCP, app: AppContext) -> None:
    def read_event_log(start_sequence: int, limit: int, category_id: int | None) -> dict[str, Any]:
        timer = OperationTimer()
        try:
            if start_sequence < 0:
                raise RobotStudioMcpError("RS_INVALID_ARGUMENT", "start_sequence must be non-negative.")
            _, limit = pagination(0, limit)
        except RobotStudioMcpError as exc:
            return finish_failure(
                app,
                "get_event_log",
                exc,
                timer=timer,
                scope="controller",
                side_effect="controller_read",
            )
        return bridge_operation(
            app,
            "get_event_log",
            "controller.eventlog",
            {"start_sequence": start_sequence, "limit": limit, "category_id": category_id},
            scope="controller",
            side_effect="controller_read",
        )

    @mcp.tool(name="scan_controllers")
    def scan_controllers() -> dict[str, Any]:
        """Discover and classify controllers; this does not connect to real controllers."""
        return bridge_operation(
            app,
            "scan_controllers",
            "controller.scan",
            scope="controller",
            side_effect="controller_read",
        )

    @mcp.tool(name="get_controller_status")
    def get_controller_status() -> dict[str, Any]:
        """Connect through RobotStudio to the active virtual controller and read its state."""
        return bridge_operation(
            app,
            "get_controller_status",
            "controller.status",
            scope="controller",
            side_effect="controller_read",
        )

    @mcp.tool(name="get_program_pointer")
    def get_program_pointer() -> dict[str, Any]:
        """Read program and motion pointers for tasks on the active virtual controller."""
        return bridge_operation(
            app,
            "get_program_pointer",
            "controller.program_pointer",
            scope="controller",
            side_effect="controller_read",
        )

    @mcp.tool(name="list_rapid_tasks")
    def list_rapid_tasks() -> dict[str, Any]:
        """List RAPID tasks from the active virtual controller using PC SDK."""
        return bridge_operation(
            app,
            "list_rapid_tasks",
            "rapid.tasks",
            scope="rapid",
            side_effect="controller_read",
        )

    @mcp.tool(name="list_rapid_modules")
    def list_rapid_modules(task_name: str | None = None) -> dict[str, Any]:
        """List RAPID module metadata for all tasks or one named task; module text is not exported in Phase 1."""
        return bridge_operation(
            app,
            "list_rapid_modules",
            "rapid.modules",
            {"task_name": task_name},
            scope="rapid",
            side_effect="controller_read",
        )

    @mcp.tool(name="get_event_log")
    def get_event_log(start_sequence: int = 0, limit: int = 100, category_id: int | None = None) -> dict[str, Any]:
        """Read actual Event Log entries from the active virtual controller."""
        return read_event_log(start_sequence, limit, category_id)

    @mcp.tool(name="get_event_log_since")
    def get_event_log_since(sequence_number: int, limit: int = 1000) -> dict[str, Any]:
        """Read Event Log entries at or after a known sequence number for evidence deltas."""
        return read_event_log(sequence_number, limit, None)

    @mcp.tool(name="list_io_signals")
    def list_io_signals(offset: int = 0, limit: int = 200) -> dict[str, Any]:
        """Page through I/O signals on the active virtual controller without subscribing or writing."""
        timer = OperationTimer()
        try:
            offset, limit = pagination(offset, limit)
        except RobotStudioMcpError as exc:
            return finish_failure(
                app,
                "list_io_signals",
                exc,
                timer=timer,
                scope="controller",
                side_effect="controller_read",
            )
        return bridge_operation(
            app,
            "list_io_signals",
            "controller.io",
            {"offset": offset, "limit": limit},
            scope="controller",
            side_effect="controller_read",
        )

    @mcp.tool(name="read_io_signal")
    def read_io_signal(name: str) -> dict[str, Any]:
        """Read one named I/O signal from the active virtual controller."""
        return bridge_operation(
            app,
            "read_io_signal",
            "controller.io_signal",
            {"name": name},
            scope="controller",
            side_effect="controller_read",
        )
