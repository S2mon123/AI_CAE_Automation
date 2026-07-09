---
name: open-toolchain-evidence
description: Evidence-first workflow for MATLAB/Simulink, OpenFOAM, and ParaView automation. Use when the user asks Codex to run MATLAB scripts, Simulink smoke checks, OpenFOAM cases, ParaView postprocessing, or public-safe AI CAE Automation Lab run records.
---

# Open Toolchain Evidence

Use this skill for MATLAB/Simulink, OpenFOAM, and ParaView tasks that need
traceable execution. Do not claim a model, case, or visualization succeeded
unless logs and exported artifacts exist.

## Required Start

```powershell
ai-cae-toolbox env-check --json
ai-cae-toolbox bridge-plan --solver <matlab|openfoam|paraview> --objective "<objective>"
ai-cae-toolbox create-run --solver <solver> --case <case-name> --objective "<objective>"
ai-cae-toolbox write-smoke-template --solver <solver> --run-dir <run-dir> --case <case-name>
```

## MCP Tools

If the MCP server is available, prefer:

- `solver_bridge_plan`
- `write_solver_smoke_template`
- `matlab_check_installation`
- `matlab_run_script_file`
- `openfoam_check_installation`
- `openfoam_run_case_command`
- `paraview_check_installation`
- `paraview_run_pvpython_script`
- `scan_run_evidence`
- `generate_run_report`

## Evidence Rules

- MATLAB: collect batch log, `.m` source, `.mat` or CSV outputs, figures, and diagnostics.
- Simulink: collect model file evidence, simulation logs, exported results, and block/model version notes.
- OpenFOAM: collect case files, `log.*`, `blockMesh`/`checkMesh` output, residual data, and result folders.
- ParaView: collect pvpython script, screenshots, state file, CSV exports, and rendering logs.

## Public Safety

Do not commit proprietary Simulink models, private geometry, large OpenFOAM time
directories, or screenshots that expose private project names. Keep heavy result
folders in local run directories or private releases.

## Finish

```powershell
ai-cae-toolbox scan-evidence <run-dir>
ai-cae-toolbox generate-report <run-dir>
```

Report missing software, failed imports, missing case directories, and rendering
errors honestly.
