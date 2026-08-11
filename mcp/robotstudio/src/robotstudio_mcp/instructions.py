SERVER_INSTRUCTIONS = """
Operate ABB RobotStudio through typed, workspace-scoped, evidence-returning tools.
This release implements Phase 0 and Phase 1 only: environment inspection, isolated
project files, and read-only Station/Virtual Controller inspection. Call
get_environment first, then get_bridge_status, then get_live_capabilities. Treat
bridge-offline responses as unavailable data and never invent Station or controller
state. The controller scope is virtual_only. Real-controller connections and every
Station, RAPID, I/O, program-pointer, and execution write are intentionally absent.
Do not infer RAPID load or simulation success from source text or file presence.
""".strip()
