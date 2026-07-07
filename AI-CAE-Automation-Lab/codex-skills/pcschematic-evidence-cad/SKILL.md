---
name: pcschematic-evidence-cad
description: PCSCHEMATIC Automation evidence-first electrical CAD workflow for Codex. Use when the user asks to inspect PCSCHEMATIC installations, COM/OLE automation, scripts, component databases, symbol libraries, electrical schematic generation, terminal lists, component lists, cable lists, exports, or AI CAE Automation Lab run records.
---

# PCSCHEMATIC Evidence CAD

Use this skill for PCSCHEMATIC Automation tasks where every drawing, component, symbol, and export must be traceable to real local files. Do not fabricate components, terminals, symbols, manufacturer data, or COM/OLE success.

## Required Start

1. Check the environment:

```powershell
ai-cae-toolbox env-check --json
```

2. Create a run:

```powershell
ai-cae-toolbox create-run --solver pcschematic --case <case-name> --objective "<objective>"
```

If the MCP server is available, call `pcschematic_check_installation` before any COM/OLE or UI automation attempt.

3. Store task artifacts in:

- `scripts/` for COM/OLE, Pascal, Basic, or UI automation scripts
- `inputs/` for public-safe task specs and placeholders
- `logs/` for install checks, COM checks, and execution logs
- `outputs/` for generated project files kept out of public git when proprietary
- `exports/` for PDFs, component lists, terminal lists, cable lists, CSV/JSON summaries

## Safety Rules

- Check the executable, installation root, TLB, manuals, database folder, symbol folder, example scripts, and example projects before automation.
- Check COM/OLE registration before trying to drive the application.
- Do not modify vendor installation files, original databases, symbol libraries, manuals, or example projects.
- Work in a separate output directory and avoid overwriting old projects or exports.
- If a component is not found in the local database, say so and choose a traceable fallback only when justified.

## Automation Path

Prefer this order:

1. Official COM/OLE API or documented scripts.
2. PCSCHEMATIC built-in Pascal/Basic examples.
3. Controlled UI automation only when APIs are insufficient.

Record which path was used in `run.log`.

## Evidence Checklist

Collect:

- installation and COM/OLE check log
- selected component database records or traceable identifiers
- selected symbol file references
- project file path and page list
- exported PDF, component list, terminal list, and cable list when available
- known limitations and unverified fields

Then run:

```powershell
ai-cae-toolbox scan-evidence <run-dir>
ai-cae-toolbox generate-report <run-dir>
```

## Reporting Rule

The final answer must distinguish between a generated project, a script prepared for execution, a successful export, and an unverified or failed automation step.
