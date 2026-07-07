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

## 2. Install Skills

```powershell
.\.venv\Scripts\python.exe scripts\install_codex_assets.py --install-skills --force
```

This copies the folders under `codex-skills/` into `~/.codex/skills` or
`%CODEX_HOME%\skills`.

## 3. Register MCP

Generate a local Codex TOML snippet:

```powershell
.\.venv\Scripts\python.exe scripts\install_codex_assets.py --write-mcp-toml .\private\codex-mcp.local.toml
```

Then copy the generated block into the local Codex `config.toml` and replace the
optional solver environment variables with real local paths. Keep that local
config out of git.

Template: [`../mcp/codex-config.example.toml`](../mcp/codex-config.example.toml)

## 4. Smoke Test

```powershell
.\.venv\Scripts\ai-cae-toolbox.exe env-check --json
.\.venv\Scripts\ai-cae-toolbox.exe create-run --solver abaqus --case smoke-test --objective "Validate installed toolbox"
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
| `pcschematic-evidence-cad` | PCSCHEMATIC COM/OLE, symbols, components, exports |

## Important Limits

- Skills are instructions and workflow assets; they do not include commercial
  solvers, licenses, proprietary manuals, private databases, or generated
  customer projects.
- MCP tools in the first public milestone manage environment checks, run
  records, evidence scans, and reports. Solver-specific submit/export tools are
  added through adapters after smoke tests exist.
