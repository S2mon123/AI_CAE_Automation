---
name: robotstudio-core
description: Safely inspect ABB RobotStudio 2025 stations and Virtual Controllers through the local robotstudio MCP server. Use when Codex needs to audit the RobotStudio/SDK environment, verify the Add-In bridge, inventory robots/tools/workobjects/targets/paths, read RAPID task or module metadata, inspect Event Log or I/O state, or collect Phase 0/1 acceptance evidence without modifying RobotStudio or a controller.
---

# RobotStudio Core

Use only the installed `robotstudio` MCP surface. Treat returned values as live only when the response has `ok=true` and the Add-In reports an actual RobotStudio version.

## Workflow

1. Call `get_environment`.
2. Require a compatible RobotStudio 2025.3 installation and matching SDK assemblies.
3. Call `get_bridge_status`; stop live inspection if `online=false`.
4. Call `get_live_capabilities` and `get_safety_policy`.
5. For Station work, call `get_active_station` and `get_station_summary` before narrower list/get tools.
6. For controller work, call `scan_controllers`, then `get_controller_status`; continue only when the active controller is virtual.
7. Read RAPID tasks/modules, program pointers, Event Log, or I/O as requested.
8. Report request IDs, versions, controller identity/state, warnings, and returned evidence. Clearly mark any live test not run.

## Hard gates

- Never treat source code, a Station file, or a generated report as proof of live RobotStudio execution.
- Never connect to a real controller. `scan_controllers` is classification only.
- Never propose hidden write alternatives. Station writes, RAPID transfer/load/write, Reset PP, Start/Stop, and I/O writes are absent in Phase 0/1.
- Never bypass an unavailable tool with shell, UI automation, reflection, or arbitrary code injection.
- Keep project files below the configured workspace. Import only explicit files into a named project.
- If `RS_BRIDGE_OFFLINE`, ask the user to start RobotStudio 2025.3, open a Station, and confirm the Add-In is loaded.
- If `RS_CONTROLLER_NOT_VIRTUAL`, stop controller work.

## Evidence expectations

Separate three categories in the answer:

- verified live facts returned by RobotStudio/PC SDK;
- static installation or build evidence;
- unverified or unavailable checks.

Read [references/tool-reference.md](references/tool-reference.md) when choosing tools or interpreting stable error codes.
