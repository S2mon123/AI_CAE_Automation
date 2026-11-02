from __future__ import annotations

import re
from typing import Any

from fastmcp import FastMCP

from robotstudio_mcp.app import AppContext
from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.result_models import OperationTimer
from robotstudio_mcp.tools.common import finish_failure, finish_success


def collect_cube_context(
    app: AppContext,
    expected_module: str,
    expected_routine: str,
    task_name: str = "T_ROB1",
    start_signal: str = "diPN_Test",
    done_signal: str = "doPN_Test",
) -> dict[str, Any]:
    for value in (expected_module, expected_routine, task_name, start_signal, done_signal):
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,79}", value):
            raise RobotStudioMcpError("RS_INVALID_ARGUMENT", "Explicit RAPID/I/O identifiers are required.")
    status = app.bridge.call("controller.status")["result"]
    identity = status.get("identity", {}).get("system_id")
    if status.get("is_virtual") is not True or not identity:
        raise RobotStudioMcpError("RS_CONTROLLER_NOT_VIRTUAL", "A verified virtual controller identity is required.")
    snapshots = {
        "pointers": app.bridge.call("controller.program_pointer")["result"],
        "modules": app.bridge.call("rapid.modules", {"task_name": task_name})["result"],
        "start": app.bridge.call("controller.io_signal", {"name": start_signal})["result"],
        "done": app.bridge.call("controller.io_signal", {"name": done_signal})["result"],
    }
    if any(snapshot.get("system_id") != identity for snapshot in snapshots.values()):
        raise RobotStudioMcpError("RS_CONTROLLER_CONTEXT_CHANGED", "Controller changed between read snapshots.")
    tasks = [task for task in snapshots["pointers"].get("tasks", []) if task.get("name") == task_name]
    pointer = tasks[0].get("program_pointer") if len(tasks) == 1 else None
    matches = bool(pointer and pointer.get("module") == expected_module
                   and pointer.get("routine") == expected_routine)
    return {
        "source": "ROBOTSTUDIO_VC", "controller_identity": identity, "snapshots": snapshots,
        "expected_entry": {"task": task_name, "module": expected_module, "routine": expected_routine},
        "entry_pointer_matches": matches, "snapshot_atomic": False,
        "waiting_for_start_proven": False, "loaded_source_hash": None,
        "scenario": {"kind": "cube_edges", "side_length_mm": 200, "segments": 16,
                     "unique_edges": 12, "nominal_duration_s_at_v50_override30": 3200 / 15},
        "real_motion_authorized": False, "simulation_passed": False,
        "blockers": ([] if matches else ["EXPECTED_ENTRY_NOT_SELECTED"]) + [
            "RAPID_SOURCE_AND_HANDSHAKE_NOT_VERIFIED", "TOOL_LOAD_WOBJ_AND_ANCHOR_NOT_VERIFIED",
            "FULL_PATH_SIMULATION_NOT_IMPLEMENTED", "STOP_NOT_COMMISSIONED"],
        "note": "Start FALSE is not Stop; a high Done snapshot is not proof of a new cycle completing.",
    }


def register_scenario_tools(mcp: FastMCP, app: AppContext) -> None:
    @mcp.tool(name="inspect_cube_task_context")
    def inspect_cube_task_context(
        expected_module: str,
        expected_routine: str,
        task_name: str = "T_ROB1",
        start_signal: str = "diPN_Test",
        done_signal: str = "doPN_Test",
    ) -> dict[str, Any]:
        """Collect virtual-controller entry and I/O evidence for the Physical AI cube scenario; never runs it."""
        timer = OperationTimer()
        try:
            result = collect_cube_context(app, expected_module, expected_routine, task_name, start_signal, done_signal)
            return finish_success(app, "inspect_cube_task_context", result, timer=timer,
                                  scope="controller", side_effect="controller_read")
        except RobotStudioMcpError as exc:
            return finish_failure(app, "inspect_cube_task_context", exc, timer=timer,
                                  scope="controller", side_effect="controller_read")
