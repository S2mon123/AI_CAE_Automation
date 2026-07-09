# Simulation Automation Smoke Test

Run this before trusting any MCP, plugin, script, or agent workflow.

## Minimum Checks

- Input files exist.
- Output directory exists and is empty or versioned.
- Python environment exists.
- Solver executable exists.
- License status is known or failure is captured.
- MCP server or bridge can start.
- Tool list or status command works.
- A tiny model can be created, opened, or read.
- A dry-run or minimal solve produces logs.
- Evidence files are exported.

## Pass Criteria

A smoke test passes only when it produces at least one auditable artifact:

- log file,
- status JSON,
- solver transcript,
- exported image,
- exported table,
- saved project file.

## Fail Criteria

Mark the test failed when:

- the solver path is missing,
- the bridge starts but cannot call tools,
- the software opens but no model context is available,
- the result is only a screenshot with no log,
- an agent reports success without files.
