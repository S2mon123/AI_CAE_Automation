---
name: fluent-evidence-cfd
description: Ansys Fluent evidence-first CFD workflow for Codex. Use when the user asks to prepare, run, journal, automate, validate, postprocess, or report Fluent CFD simulations using batch journals, PyFluent, TUI commands, residual logs, case/data files, exported plots, CSV reports, and AI CAE Automation Lab run records.
---

# Fluent Evidence CFD

Use this skill for Fluent tasks that need real execution traces. Prefer batch journals for repeatability; use PyFluent only when the local installation and license support it.

## Required Start

1. Check environment:

```powershell
ai-cae-toolbox env-check --json
```

2. Create a run:

```powershell
ai-cae-toolbox create-run --solver fluent --case <case-name> --objective "<objective>"
```

3. Store files in the run folder:

- `scripts/run.jou` for Fluent journal commands
- `inputs/` for mesh, case seeds, and parameter files
- `logs/transcript.log` for Fluent output
- `outputs/` for `.cas`, `.dat`, and result files
- `exports/` for residual CSV, force reports, contours, pathlines, and summaries

## Execution Pattern

If the MCP server is available, prefer `fluent_run_journal_file`.

For batch work, use a command shaped like:

```powershell
fluent 3ddp -g -i <run-dir>\scripts\run.jou
```

If the executable is not on PATH, find it from `FLUENT_EXE` or under `FLUENT_ROOT`. Record the exact command in `run.log`.

## Journal Requirements

A useful journal should:

- read or create the case/mesh
- set models, materials, zones, boundary conditions, methods, monitors, and initialization
- run a controlled number of iterations or time steps
- write case/data outputs
- export residuals, reports, and at least one visual artifact when possible
- avoid absolute private paths in committed examples

## CFD Validation Checklist

- Confirm dimensions and unit system.
- Confirm boundary condition names match the mesh.
- Monitor residuals and at least one engineering quantity.
- Separate mesh/geometry preview from solver results.
- For transient tasks, record time step size, total steps, and save interval.

## Evidence Collection

After running:

```powershell
ai-cae-toolbox scan-evidence <run-dir>
ai-cae-toolbox generate-report <run-dir>
```

Treat a run as `engineering-draft` only when logs, solver outputs, and exported numeric or visual evidence agree. Treat setup-only or failed runs as dry runs or functional validation.

<!-- AI-CAE:weld-pool:START -->
## Welding Melt-Pool Tasks

For welding, laser/arc heat-source, or melt-pool requests:

- Start with Stage A: thermal + Solidification/Melting; keep VOF off.
- Require a coordinate audit: X travel, Y weave, Z thickness, top heat-flux face.
- Verify the UDF trajectory before interpreting results.
- Save dense transient data if the user requests MP4/video evidence.
- Export temperature cloud, liquid fraction, melt-depth time series, and a
  credibility note.
- Treat coarse melt depth as diagnostic until mesh/time-step/material studies are
  complete.
<!-- AI-CAE:weld-pool:END -->
