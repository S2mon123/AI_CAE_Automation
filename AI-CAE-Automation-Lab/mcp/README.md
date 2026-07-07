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

## Current Toolbox

The repository now includes a small MCP-ready toolbox:

- `env_check`: local Python/Git/solver-path inspection without launching commercial software.
- `list_codex_skills`: list installable Codex skill packs in this repository.
- `list_solver_adapters`: list planned and implemented solver adapter capabilities.
- `create_run_record`: create a traceable run directory with `run.json`, `run.log`, and standard subfolders.
- `scan_run_evidence`: scan logs, scripts, solver outputs, images, tables, and reports.
- `generate_run_report`: write `report.md` with a credibility grade.
- `abaqus_run_no_gui_script`: run Abaqus/CAE noGUI scripts with captured logs.
- `abaqus_submit_input_deck`: submit Abaqus input decks with captured logs.
- `fluent_run_journal_file`: run Fluent journal files in batch mode.
- `ansys_check_installation`: check configured Ansys paths without launching products.
- `ansys_run_workbench_journal_file`: run Workbench journals in batch mode.
- `comsol_check_installation`: check COMSOL batch, Java, and API documentation paths.
- `comsol_run_batch_file`: run configured COMSOL batch commands.
- `pcschematic_check_installation`: check PCSCHEMATIC configured paths without launching the application.

See [`solver-bridge-toolbox.md`](solver-bridge-toolbox.md) and
[`../docs/mcp-toolbox-roadmap.md`](../docs/mcp-toolbox-roadmap.md). A public-safe
client template is available at [`client-config.example.json`](client-config.example.json).
