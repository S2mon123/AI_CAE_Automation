---
name: ai-cae-run-manager
description: Evidence-first run management for AI-assisted CAE and engineering automation. Use when Codex needs to plan, execute, audit, or report a simulation/CAD automation task with AI CAE Automation Lab, MCP tools, run folders, evidence scans, credibility grading, or report generation.
---

# AI CAE Run Manager

Use this skill to make every engineering automation task traceable. Treat a task as incomplete until it has a run folder, input source, execution log, exported evidence, and a report.

## Core Workflow

1. Check the environment before modeling:

```powershell
ai-cae-toolbox env-check --json
```

If the command is not installed, run from the cloned repository:

```powershell
python -m ai_cae_lab.toolbox env-check --json
```

2. Create a run directory before generating solver files:

```powershell
ai-cae-toolbox create-run --solver <solver> --case <case-name> --objective "<objective>"
```

Use the generated run folder structure:

```text
runs/<run-id>/
  run.json
  run.log
  inputs/
  scripts/
  outputs/
  exports/
  logs/
```

3. Put source artifacts in the run folder:

- modeling scripts and journals in `scripts/`
- input decks, geometry placeholders, and small public-safe examples in `inputs/`
- solver logs in `logs/`
- exported plots, CSV/JSON tables, reports, and screenshots in `exports/`
- native solver outputs in `outputs/`, while keeping large/private files out of git

4. After execution, scan evidence:

```powershell
ai-cae-toolbox scan-evidence <run-dir>
```

5. Generate the report:

```powershell
ai-cae-toolbox generate-report <run-dir>
```

## MCP Tool Usage

If the `ai-cae-automation-lab` MCP server is available, prefer structured tools:

- `env_check`
- `create_run_record`
- `scan_run_evidence`
- `generate_run_report`
- `abaqus_run_no_gui_script`
- `abaqus_submit_input_deck`
- `fluent_run_journal_file`
- `pcschematic_check_installation`

Use CLI commands when MCP is unavailable.

## Validation Rules

- Never claim solver success without logs and exported evidence.
- Mark dry runs, failed runs, and visual previews honestly.
- Record exact commands, executable paths, and error messages in `run.log`.
- Do not publish private paths, licensed manuals, raw customer models, credentials, or large generated solver outputs.
- If a commercial solver is missing or unlicensed, produce a reproducible setup package and stop before claiming results.
