---
name: comsol-evidence-multiphysics
description: COMSOL Multiphysics evidence-first automation workflow for Codex. Use when the user asks to inspect COMSOL installations, Java API docs, Model Builder scripts, batch runs, MPH files, heat transfer, CFD, photonics, multiphysics simulation, result exports, or AI CAE Automation Lab run records.
---

# COMSOL Evidence Multiphysics

Use this skill for COMSOL tasks that must be scripted, run, and audited. Prefer Java API or COMSOL batch workflows when available. Do not claim a COMSOL model solved unless logs and exported artifacts exist.

## Required Start

1. Check environment:

```powershell
ai-cae-toolbox env-check --json
```

2. Create a run:

```powershell
ai-cae-toolbox create-run --solver comsol --case <case-name> --objective "<objective>"
```

3. Generate a bridge plan and smoke template when useful:

```powershell
ai-cae-toolbox bridge-plan --solver comsol --objective "<objective>"
ai-cae-toolbox write-smoke-template --solver comsol --run-dir <run-dir> --case <case-name>
```

4. If MCP is available, call:

- `solver_bridge_plan`
- `write_solver_smoke_template`
- `comsol_check_installation`
- `comsol_compile_java_file` when a Java API source file is ready
- `comsol_run_compiled_java_class` when a `.class` file is ready
- `comsol_run_batch_file` when a batch-compatible model or script is ready

## Run Folder Layout

Use the AI CAE run folder:

- `scripts/` for Java API, MPH batch, or helper scripts
- `inputs/` for public-safe parameters and placeholder geometry
- `logs/` for COMSOL batch logs and Java/API errors
- `outputs/` for `.mph` files, kept out of public git when proprietary
- `exports/` for PNG, CSV, JSON, DOCX/PDF, and `report.md`

## COMSOL Checks

Before building a model, verify:

- COMSOL root or batch command exists
- COMSOL compile command exists if using Java API
- COMSOL Java runtime exists if using Java API
- local Application Programming Guide and Programming Reference docs exist, if available
- local Java API index exists, if available
- output directory is new and will not overwrite an old model

## Modeling Rules

- Parameterize geometry, materials, loads, mesh, and study settings.
- Prefer built-in materials only when the exact material is available; otherwise mark values as engineering estimates.
- For conjugate heat transfer, clearly separate solid domains, fluid domains, inlets, outlets, walls, and multiphysics couplings.
- For photonics, record wavelength, mode, polarization, material indices, boundary conditions, mesh size, and power-balance evidence.
- If an API name is uncertain across versions, write the uncertainty in the log and stop before claiming success.

## Evidence Checklist

Collect:

- Java/API script or batch input
- COMSOL command line and log
- `.mph` output path, if created
- exported figures and tables
- key scalar results in CSV/JSON
- `report.md` with credibility grade

Then run:

```powershell
ai-cae-toolbox scan-evidence <run-dir>
ai-cae-toolbox generate-report <run-dir>
```

## Failure Handling

If COMSOL is missing, the Java API fails, a study does not converge, or no `.mph`/export is produced, report the exact failure and classify the run as setup, dry-run, or functional validation.
