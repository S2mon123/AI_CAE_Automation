# MCP Notes

MCP is useful when the agent needs structured tools instead of loose instructions. For CAE, the server should expose small, auditable actions.

## Useful Tool Types

- `status`: report software, bridge, active model, and working directory.
- `list_projects`: list open or available projects.
- `run_script`: execute a controlled solver script.
- `submit_job`: run a solve with a named job.
- `read_log`: return the latest solver log.
- `export_result`: export a plot, table, image, or JSON summary.
- `export_document`: export a schematic PDF, component list, terminal list, or cable list for electrical CAD tools.

## Design Rules

- Tools should return file paths and status objects, not vague success text.
- Long solves should create job handles or progress files.
- Every tool should fail loudly when the solver is not connected.
- The bridge should avoid deleting or overwriting user files.

## Electrical CAD Note

For tools such as PCSCHEMATIC Automation, MCP should focus on project evidence rather than solver evidence: real project files, database-backed components, symbol references, terminal/cable/component lists, generated PDFs, and a run log that explains which API, script, or UI path was used.

## First Smoke Test

```text
1. start server
2. list tools
3. call status
4. run a no-op or hello command
5. export a small status JSON
```
