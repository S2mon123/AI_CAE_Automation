# Deep Solver Bridge MCP

This document describes the deeper bridge layer for AI CAE Automation Lab. The
goal is to let a tool-using agent work through auditable local actions instead
of loose prompts.

## Design Position

This project does not copy third-party CAE agent repositories. Its own position
is:

- evidence-first run folders
- small solver adapters
- local configuration owned by the user
- public-safe smoke templates
- explicit failure reporting
- no bundled commercial manuals, binaries, solver outputs, or paid material

## Bridge Layers

| Layer | Purpose | Public Artifact |
| --- | --- | --- |
| Config | Store local executable paths outside code | `configs/*.template.json` |
| Run manager | Create repeatable folders and metadata | `src/ai_cae_lab/runs.py` |
| Template writer | Generate tiny solver-native smoke files | `src/ai_cae_lab/templates.py` |
| Adapter | Call local commands and capture logs | `src/ai_cae_lab/adapters/` |
| MCP server | Expose structured agent tools | `src/ai_cae_lab/mcp_server.py` |
| Evidence scanner | Classify outputs and grade credibility | `src/ai_cae_lab/evidence.py` |
| Report writer | Summarize what actually happened | `src/ai_cae_lab/report.py` |

## Core MCP Tools

| Tool | Use |
| --- | --- |
| `env_check` | Check common local CAE path candidates. |
| `list_codex_skills` | List included skill packs. |
| `list_solver_adapters` | Show available solver adapters and maturity. |
| `create_run_record` | Create `run.json`, `run.log`, and evidence folders. |
| `solver_bridge_plan` | Return a solver-specific bridge plan without launching software. |
| `write_solver_smoke_template` | Write a tiny solver-native smoke template. |
| `scan_run_evidence` | Inventory logs, scripts, models, tables, images, and reports. |
| `generate_run_report` | Write a reviewable `report.md`. |

## Solver Tools

| Solver | Tools |
| --- | --- |
| Abaqus | `abaqus_run_no_gui_script`, `abaqus_submit_input_deck` |
| Fluent | `fluent_run_journal_file` |
| Ansys Workbench | `ansys_check_installation`, `ansys_run_workbench_journal_file` |
| COMSOL | `comsol_check_installation`, `comsol_compile_java_file`, `comsol_run_compiled_java_class`, `comsol_run_batch_file` |
| MATLAB | `matlab_check_installation`, `matlab_run_script_file` |
| OpenFOAM | `openfoam_check_installation`, `openfoam_run_case_command` |
| ParaView | `paraview_check_installation`, `paraview_run_pvpython_script` |
| PCSCHEMATIC | `pcschematic_check_installation` |

## Local Setup Pattern

1. Clone the repository.
2. Create a Python virtual environment.
3. Install the package with MCP extras.
4. Copy `configs/local.toolchain.template.json` to a private local file.
5. Fill local executable paths.
6. Register `ai-cae-mcp-server` in the Codex MCP config.
7. Start with `solver_bridge_plan`.
8. Create a run folder.
9. Generate a smoke template.
10. Run the smallest possible connection test.
11. Scan evidence and write a report.

## CLI Example

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
.\.venv\Scripts\ai-cae-toolbox.exe bridge-plan --solver comsol --objective "COMSOL Java API smoke test"
.\.venv\Scripts\ai-cae-toolbox.exe create-run --solver comsol --case comsol-smoke --objective "Validate COMSOL bridge"
.\.venv\Scripts\ai-cae-toolbox.exe write-smoke-template --solver comsol --run-dir runs\<run-id> --case comsol-smoke
.\.venv\Scripts\ai-cae-toolbox.exe scan-evidence runs\<run-id>
.\.venv\Scripts\ai-cae-toolbox.exe generate-report runs\<run-id>
```

## Maturity Rules

An adapter is not marked production-ready until it has:

- documented install variables
- a smoke template
- a log-capturing run tool
- evidence scan coverage
- a passing local smoke run with artifacts
- clear failure modes

## Difference From Prompt Collections

A prompt collection tells the agent what to do. This bridge layer gives the agent
small, inspectable tools that create records, call software, read artifacts, and
fail visibly. That is the central difference between an idea library and a local
engineering automation toolkit.
