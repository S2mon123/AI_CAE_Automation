# Solver Bridge MCP Toolbox

The MCP server wraps the local toolbox in structured tools that an agent can
call safely.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
```

## Run

```powershell
.\.venv\Scripts\ai-cae-mcp-server.exe
```

For a local MCP client, point the command to the same executable. Keep private
solver paths in environment variables, not in this repository.

See [`client-config.example.json`](client-config.example.json) for a public-safe
client configuration template.

## Tools

| Tool | Purpose |
|---|---|
| `env_check` | Check local Python, Git, and known solver path candidates. |
| `list_codex_skills` | List public Codex skill packs shipped by this repository. |
| `list_solver_adapters` | List planned and implemented solver adapter capabilities. |
| `create_run_record` | Create a run directory with metadata and standard folders. |
| `solver_bridge_plan` | Return a solver-specific bridge plan without launching software. |
| `write_solver_smoke_template` | Write a tiny solver-native smoke template into a run directory. |
| `scan_run_evidence` | Inventory a run folder and grade evidence strength. |
| `generate_run_report` | Generate `report.md` from run metadata and evidence. |
| `abaqus_run_no_gui_script` | Run an Abaqus/CAE Python script with noGUI and capture logs. |
| `abaqus_submit_input_deck` | Submit an Abaqus input deck and capture logs. |
| `fluent_run_journal_file` | Run a Fluent journal in batch mode and capture logs. |
| `ansys_check_installation` | Check Ansys root, Fluent, and Workbench configured paths. |
| `ansys_run_workbench_journal_file` | Run a Workbench journal in batch mode and capture logs. |
| `comsol_check_installation` | Check COMSOL batch, Java, and API documentation paths. |
| `comsol_compile_java_file` | Compile a COMSOL Java API model script with `comsolcompile`. |
| `comsol_run_compiled_java_class` | Run a compiled COMSOL Java class through COMSOL batch. |
| `comsol_run_batch_file` | Run a configured COMSOL batch command and capture logs. |
| `matlab_check_installation` | Check MATLAB paths without launching MATLAB. |
| `matlab_run_script_file` | Run a MATLAB script in batch mode and capture logs. |
| `openfoam_check_installation` | Check OpenFOAM command paths or WSL availability. |
| `openfoam_run_case_command` | Run a selected OpenFOAM command against a case directory. |
| `paraview_check_installation` | Check pvpython or ParaView paths without launching the GUI. |
| `paraview_run_pvpython_script` | Run a ParaView pvpython postprocessing script. |
| `pcschematic_check_installation` | Check PCSCHEMATIC configured paths without launching the application. |

## Example Flow

```text
env_check
list_codex_skills
list_solver_adapters
solver_bridge_plan(solver="comsol", objective="COMSOL Java API smoke model")
create_run_record(solver="fluent", case_name="sinusoidal-welding-smoke")
write_solver_smoke_template(solver="fluent", run_dir="runs/<run-id>")
scan_run_evidence(run_dir="runs/<run-id>")
generate_run_report(run_dir="runs/<run-id>")
```

The first solver execution tools are minimal adapters: they call local commands
when available, write logs, and return status objects. Treat their output as
engineering evidence only after the evidence scanner and report confirm the
expected logs and artifacts.
