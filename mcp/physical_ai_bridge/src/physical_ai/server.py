from __future__ import annotations

import functools
import json
import os
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from physical_ai.service import Service


def create_server(service: Service) -> FastMCP:
    server = FastMCP(
        "abb-physical-ai",
        instructions=(
            "Physical AI v4: host/PLC/ABB read-only commissioning and offline cube task development. "
            "Generated files and structural evidence checks never authorize motion. "
            "No device writes, activation, deployment, Start, Resume, or approval issuer is exposed. "
            "Stop is unavailable in this development release; never equate Start FALSE with Stop."
        ),
    )

    def expose(name, function, description, readonly=True):
        @functools.wraps(function)
        def guarded(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as exc:
                # Only allow our short constant codes; SDK/OS/validation messages can carry private input.
                code = (
                    str(exc)
                    if type(exc) is ValueError and re.fullmatch(r"[A-Z][A-Z0-9_:]{0,119}", str(exc))
                    else "OPERATION_FAILED"
                )
                return {
                    "ok": False,
                    "code": code,
                    "error_type": type(exc).__name__,
                    "quality": "UNKNOWN",
                    "real_motion_authorized": False,
                }

        server.add_tool(
            guarded,
            name=name,
            description=description,
            annotations={
                "readOnlyHint": readonly,
                "destructiveHint": False,
                "idempotentHint": readonly,
                "openWorldHint": False,
            },
        )

    expose("system_get_capabilities", service.capabilities, "Implementation inventory, not live commissioning proof.")
    expose("system_discover", service.discover, "Read host information; no network scan.")
    expose(
        "system_get_status", service.bridge_status, "Read configured PLC ADS Runtime state through signed v4 Bridge."
    )
    expose("plc_read_alias", service.plc_read, "Read allowlisted start/done BOOL; neither value can be written.")
    expose("abb_read", service.abb_read, "Read status, inventory or a named I/O through a target-locked PC SDK proxy.")
    expose("task_create", service.task_create, "Register A/B/C with explicit frozen context; saves local draft.", False)
    expose(
        "task_render", service.task_render, "Generate an additive cube RAPID draft and manifest; never upload.", False
    )
    expose(
        "task_validate", service.task_validate, "Check geometry and supplied evidence; never grants credentials.", False
    )
    expose("task_get_validation", service.task_get_validation, "Recheck evidence expiry and bindings now.", False)
    expose("task_prepare_execute", service.prepare_execute, "Explain execution blockers; cannot authorize or execute.")
    expose("tc2_inspect", service.tc2_inspect, "Inspect workspace TSM XML. Disk mappings are not Runtime evidence.")
    expose("tc2_stage_link_proposal", service.tc2_stage, "Save exact TSM snapshot and unapplied link proposal.", False)
    expose("report_export", service.export_report, "Save host and capability report, without credentials.", False)

    @server.tool()
    def task_simulate(task_id: str) -> dict:
        """Report unavailable automatic simulation without manufacturing a PASS."""
        service._load(task_id)
        return {
            "ok": False,
            "code": "SIMULATION_AUTOMATION_NOT_IMPLEMENTED",
            "status": "INCOMPLETE",
            "real_motion_authorized": False,
        }

    @server.tool()
    def robot_request_process_stop() -> dict:
        """Unavailable in P0-P2. No request is sent, and standstill is never inferred."""
        return {
            "ok": False,
            "code": "STOP_UNAVAILABLE",
            "request_delivered": False,
            "standstill_observed": False,
            "action": "Use the verified on-site pendant/hardware procedure.",
        }

    return server


def main():
    workspace = Path(os.environ.get("PHYSICAL_AI_WORKSPACE", str(Path.home() / "PhysicalAI" / "workspace")))
    config_path = os.environ.get("PHYSICAL_AI_CONFIG")
    config = json.loads(Path(config_path).read_text(encoding="utf-8-sig")) if config_path else {}
    create_server(Service(workspace, config)).run(transport="stdio")


if __name__ == "__main__":
    main()
