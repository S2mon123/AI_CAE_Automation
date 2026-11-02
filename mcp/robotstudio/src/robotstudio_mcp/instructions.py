SERVER_INSTRUCTIONS = """
Operate ABB RobotStudio through typed, workspace-scoped, evidence-returning tools.
This release implements Phase 0 and Phase 1 only: environment inspection, isolated
project files, and read-only Station/Virtual Controller inspection. Call
get_environment first, then get_bridge_status, then get_live_capabilities. Treat
bridge-offline responses as unavailable data and never invent Station or controller
state. The controller scope is virtual_only. Real-controller connections and every
Station, RAPID, I/O, program-pointer, and execution write are intentionally absent.
Do not infer RAPID load or simulation success from source text or file presence.
For the 200 mm Physical AI cube scenario, inspect_cube_task_context compares the
expected VC entry and collects I/O snapshots. This does not compile or simulate
the path, verify a waiting contract, or authorize motion. PLC/real ABB read-only
commissioning and offline task drafts belong to the separate abb-physical-ai MCP.
""".strip()
