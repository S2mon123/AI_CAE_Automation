# Codex MCP And Skill Setup

This guide turns a clone of this repository into a Codex-ready local automation
toolkit.

## 1. Clone And Install

```powershell
git clone <your-repo-url>
cd AI-CAE-Automation-Lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
```

## 2. First-Run Local Setup

```powershell
.\.venv\Scripts\ai-cae-toolbox.exe setup
. .\private\activate-ai-cae.ps1
.\.venv\Scripts\ai-cae-toolbox.exe doctor
```

`setup` discovers local Abaqus, COMSOL, MATLAB, Ansys, Fluent, Workbench, and
PCSCHEMATIC paths from environment variables, PATH, the Windows registry, and
common vendor install roots. It writes ignored local files under `private/`:

- `private/ai-cae.local.json` for machine-specific solver paths
- `private/activate-ai-cae.ps1` for environment-variable activation
- `private/codex-mcp.local.toml` for Codex MCP registration

If discovery is incomplete, edit `private/ai-cae.local.json` or set environment
variables. Do not commit private configs.

## 3. Install Skills

```powershell
.\.venv\Scripts\python.exe scripts\install_codex_assets.py --install-skills --force
```

This copies the folders under `codex-skills/` into `~/.codex/skills` or
`%CODEX_HOME%\skills`.

## 4. Register MCP

Copy the generated block from `private/codex-mcp.local.toml` into the local Codex
`config.toml`. The generated block points `AI_CAE_TOOLBOX_CONFIG` at
`private/ai-cae.local.json`, so solver paths stay local to each machine.

Template: [`../mcp/codex-config.example.toml`](../mcp/codex-config.example.toml)

For a solver-specific server, register one of the package entry scripts under
`mcp/` instead of the full toolbox. Example COMSOL block:

```toml
[mcp_servers.ai_cae_comsol]
command = "python"
args = ["mcp/comsol/server.py"]
env = { AI_CAE_TOOLBOX_CONFIG = "private/ai-cae.local.json" }
```

Examples are provided in each solver package, such as
[`../mcp/comsol/examples/codex-config.example.toml`](../mcp/comsol/examples/codex-config.example.toml).

## 5. Smoke Test

```powershell
.\.venv\Scripts\ai-cae-toolbox.exe discover --json
.\.venv\Scripts\ai-cae-toolbox.exe env-check --json
.\.venv\Scripts\ai-cae-toolbox.exe create-run --solver abaqus --case smoke-test --objective "Validate installed toolbox"
.\.venv\Scripts\ai-cae-toolbox.exe bridge-plan --solver comsol --objective "Validate COMSOL bridge"
.\.venv\Scripts\ai-cae-toolbox.exe write-smoke-template --solver comsol --run-dir runs\<run-id> --case comsol-smoke
```

Start a new Codex thread and ask:

```text
Use ai-cae-run-manager and abaqus-evidence-simulation. Check the environment,
create a run folder, prepare a minimal Abaqus input-deck smoke test, and report
what evidence is available without claiming an unrun solve.
```

## Current Skills

| Skill | Use |
|---|---|
| `ai-cae-run-manager` | Evidence-first run folder, scanning, and report workflow |
| `abaqus-evidence-simulation` | Abaqus modeling, input decks, jobs, ODB evidence |
| `fluent-evidence-cfd` | Fluent journals, PyFluent, residuals, CFD exports |
| `comsol-evidence-multiphysics` | COMSOL Java API, batch runs, MPH exports |
| `pcschematic-evidence-cad` | PCSCHEMATIC COM/OLE, symbols, components, exports |

## Important Limits

- Skills are instructions and workflow assets; they do not include commercial
  solvers, licenses, proprietary manuals, private databases, or generated
  customer projects.
- MCP tools manage environment checks, bridge plans, run records, smoke
  templates, controlled solver calls, evidence scans, and reports.
- Solver-specific execution tools are conservative. They return logs and status
  objects; they do not convert an unverified run into an engineering claim.
