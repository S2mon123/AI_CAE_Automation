"""Phase 0/1 prompt registration."""

from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    @mcp.prompt(name="inspect_station")
    def inspect_station(detail: str = "summary") -> str:
        """Build a safe workflow for inspecting the active RobotStudio Station."""
        return (
            "Inspect the actual RobotStudio Station without modifying it. Call get_environment, "
            "get_bridge_status, and get_live_capabilities first. If the bridge is online, read "
            "get_active_station and get_station_summary, then list robots, tools, workobjects, "
            f"targets, and paths at detail level '{detail}'. Cite returned evidence and report "
            "unavailable data explicitly; never infer live state."
        )

    @mcp.prompt(name="inspect_virtual_controller")
    def inspect_virtual_controller(include_io: str = "false") -> str:
        """Build a read-only virtual-controller inspection workflow."""
        return (
            "Verify the bridge and safety policy, call scan_controllers, and connect only through "
            "get_controller_status to the active controller after confirming is_virtual=true. Then "
            "list RAPID tasks/modules, read program pointers and Event Log. "
            f"Include paged I/O reads: {include_io}. Do not call or propose any write or execution action."
        )

    @mcp.prompt(name="analyze_event_log")
    def analyze_event_log(start_sequence: str = "0") -> str:
        """Build an evidence-based Event Log analysis workflow."""
        return (
            f"Read Event Log entries starting at sequence {start_sequence}. Group by type, category, "
            "and time; distinguish direct message text from interpretation. Correlate with controller "
            "status and RAPID tasks. Do not fabricate ABB error meanings not present in evidence."
        )

    @mcp.prompt(name="verify_phase_0_1")
    def verify_phase_0_1() -> str:
        """Build the Phase 0/1 acceptance sequence."""
        return (
            "Verify Codex to MCP to authenticated Add-In to RobotStudio end-to-end: inspect the local "
            "2025.3 SDK match, ping the live bridge, read the active Station, read one virtual "
            "controller, RAPID tasks/modules, and Event Log, and preserve returned version/state "
            "evidence. Mark live tests not run when RobotStudio or a Virtual Controller is absent."
        )
