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
| `scan_run_evidence` | Inventory a run folder and grade evidence strength. |
| `generate_run_report` | Generate `report.md` from run metadata and evidence. |
| `abaqus_run_no_gui_script` | Run an Abaqus/CAE Python script with noGUI and capture logs. |
| `abaqus_submit_input_deck` | Submit an Abaqus input deck and capture logs. |
| `fluent_run_journal_file` | Run a Fluent journal in batch mode and capture logs. |
| `pcschematic_check_installation` | Check PCSCHEMATIC configured paths without launching the application. |

## Example Flow

```text
env_check
list_codex_skills
list_solver_adapters
create_run_record(solver="fluent", case_name="sinusoidal-welding-smoke")
scan_run_evidence(run_dir="runs/<run-id>")
generate_run_report(run_dir="runs/<run-id>")
```

The first solver execution tools are minimal adapters: they call local commands
when available, write logs, and return status objects. Treat their output as
engineering evidence only after the evidence scanner and report confirm the
expected logs and artifacts.
