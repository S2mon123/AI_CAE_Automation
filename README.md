# AI CAE Automation Lab

An open, reproducible knowledge and tooling repo for AI-assisted CAE automation.

The goal is simple: turn simulation work from "prompt and hope" into a traceable loop:

```text
task intent -> environment check -> model setup -> real solver run -> evidence export -> review note
```

This repository is being built as a public-facing companion to a private Obsidian knowledge base. It contains only rewritten workflows, checklists, prompt patterns, and lightweight utilities. Private notes, licensed course materials, proprietary models, credentials, and raw solver outputs are intentionally excluded.

## Scope

- [Adams MCP](mcp/adams/README.md): standalone Windows Adams/View bridge with
  16 tools, configuration templates, tests and an
  [evidence-first skill](codex-skills/adams-evidence-mbd/SKILL.md).
  Install and register it separately from the shared toolbox.

- AI-assisted workflows for AEDT, Abaqus, Ansys Fluent, Ansys Mechanical/Workbench, HyperMesh, LAMMPS, OVITO, COMSOL, MATLAB/Simulink, OpenFOAM, ParaView, and PCSCHEMATIC Automation.
- MCP and desktop bridge patterns for connecting agents to local engineering software.
- Prompt templates that force path checks, real execution, evidence export, and credibility grading.
- Smoke tests and evidence-chain checklists for simulation automation.
- Example project layouts for drilling, external flow, weld-pool workflows, COMSOL 10 mm cube smoke, COMSOL EHD drying, heat-transfer simulations, and electrical CAD documentation.

## Repository Map

| Path | Purpose |
|---|---|
| `docs/` | Architecture, workflow, software matrix, publishing plan |
| `prompts/` | Copy-ready prompt patterns for CAE automation |
| `checklists/` | Smoke test and evidence-chain checklists |
| `mcp/` | MCP manifests, integration notes, shared server package, and solver-specific entry packages |
| `Skill/` | Public index for the Codex skill packs |
| `codex-skills/` | Installable Codex skill packs for evidence-first CAE tasks |
| `examples/` | Public example layouts, without private solver assets |
| `configs/` | Public-safe configuration examples |
| `tests/` | Unit tests for bridge plans, smoke templates, and evidence grading |
| `scripts/` | Small command-line helpers |
| `src/ai_cae_lab/` | Python package for reusable utilities |

## Quick Start

```powershell
git clone <your-repo-url>
cd AI-CAE-Automation-Lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
.\.venv\Scripts\ai-cae-toolbox.exe setup
.\.venv\Scripts\ai-cae-toolbox.exe doctor
```

`setup` performs first-run local discovery for AEDT, Abaqus, Ansys Fluent,
Workbench/Mechanical, HyperMesh, LAMMPS, OVITO, COMSOL, MATLAB, and
PCSCHEMATIC. It checks executable paths, writes `private/ai-cae.local.json`,
`private/activate-ai-cae.ps1`, and a local Codex MCP TOML snippet. Files under
`private/` are ignored by git. Discovery does not prove a solver license or a
completed engineering run.

## Codex-Ready Install

Install the MCP toolbox, run first-time discovery, and copy the skill packs into Codex:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
.\.venv\Scripts\ai-cae-toolbox.exe setup
. .\private\activate-ai-cae.ps1
.\.venv\Scripts\python.exe scripts\install_codex_assets.py --install-skills --force
```

Then add the generated `private/codex-mcp.local.toml` block to the local Codex `config.toml`. The generated MCP env points at `private/ai-cae.local.json`, so users do not need to edit committed files or inherit the repository author's paths. See [`docs/codex-mcp-skill-setup.md`](docs/codex-mcp-skill-setup.md).

For solver-scoped MCP startup, use the package entries under [`mcp/`](mcp/README.md). For example:

```powershell
.\.venv\Scripts\python.exe mcp\comsol\server.py
.\.venv\Scripts\python.exe mcp\abaqus\server.py
.\.venv\Scripts\python.exe "mcp\ansys\Fluent MCP\server.py"
```

These entry points set `AI_CAE_MCP_SOLVERS` so Codex sees the selected solver
tools plus the shared setup, run-record, evidence, and report tools.

The installable skills are:

- `ai-cae-run-manager`
- `aedt-evidence-electromagnetics`
- `abaqus-evidence-simulation`
- `fluent-evidence-cfd`
- `ansys-mechanical-evidence-structural`
- `hypermesh-evidence-meshing`
- `lammps-evidence-md`
- `ovito-evidence-postprocessing`
- `comsol-evidence-multiphysics`
- `comsol-motor-nvh-evidence`
- `open-toolchain-evidence`
- `pcschematic-evidence-cad`

## Scoped Solver Context

Agents should not scan the full repository for routine modeling tasks. Start with:

```powershell
.\.venv\Scripts\ai-cae-toolbox.exe context-scope --solver comsol
.\.venv\Scripts\ai-cae-toolbox.exe toolchain-paths --solver comsol
```

The MCP equivalents are `solver_context_scope` and `solver_toolchain_paths`.
They tell an agent which files to read and how to resolve local executable paths
without assuming the repository author's installation folders. For first-run path discovery, use `ai-cae-toolbox setup` or the MCP tool `setup_local_toolchain` before asking an agent to run solver-specific tasks.
## MCP Toolbox Preview

The first implementation milestone adds a local toolbox that can be used from the command line or exposed as an MCP server.

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
.\.venv\Scripts\ai-cae-toolbox.exe setup
.\.venv\Scripts\ai-cae-toolbox.exe discover --json
.\.venv\Scripts\ai-cae-toolbox.exe doctor
.\.venv\Scripts\ai-cae-toolbox.exe env-check --json
.\.venv\Scripts\ai-cae-toolbox.exe list-skills --json
.\.venv\Scripts\ai-cae-toolbox.exe list-adapters --json
.\.venv\Scripts\ai-cae-toolbox.exe bridge-plan --solver comsol --objective "Validate a COMSOL Java bridge"
.\.venv\Scripts\ai-cae-toolbox.exe create-run --solver fluent --case sinusoidal-welding-smoke --objective "Validate the bridge workflow"
.\.venv\Scripts\ai-cae-toolbox.exe write-smoke-template --solver fluent --run-dir runs\<run-id> --case sinusoidal-welding-smoke
.\.venv\Scripts\ai-cae-toolbox.exe scan-evidence runs\<run-id>
.\.venv\Scripts\ai-cae-toolbox.exe generate-report runs\<run-id>
.\.venv\Scripts\ai-cae-mcp-server.exe
```

The MCP server exposes discovery/setup, private config generation, scoped
context, path guidance, run records, bridge plans, smoke templates, evidence
scans, reports, and solver adapters. Solver-specific bridges now include AEDT,
Abaqus, Fluent, Workbench, Mechanical, HyperMesh, LAMMPS, OVITO, COMSOL,
MATLAB, OpenFOAM, ParaView, and PCSCHEMATIC. Mechanical has independent solve
gates; OVITO distinguishes GUI availability from batch Python; AEDT records the
actual design/solution type; LAMMPS potential files remain user-supplied.

The full toolbox command `ai-cae-mcp-server` exposes every solver. The package
entries in `mcp/<solver>/server.py` expose only that solver profile by setting
`AI_CAE_MCP_SOLVERS`.

## Core Principles

1. Never claim a simulation succeeded without solver evidence.
2. Separate preview, dry-run, functional validation, engineering draft, and report-grade results.
3. Record executable paths, software versions, license status, input files, commands, logs, and exported artifacts.
4. Treat solver failures as useful data, not embarrassment.
5. Keep public examples free of private files and licensed training materials.
6. For electrical CAD tasks, verify components, symbols, databases, and exported lists against real local project evidence.

## Recommended Reading Order

1. [`docs/architecture.md`](docs/architecture.md)
2. [`docs/workflow.md`](docs/workflow.md)
3. [`docs/software-matrix.md`](docs/software-matrix.md)
4. [`docs/electrical-cad-automation.md`](docs/electrical-cad-automation.md)
5. [`checklists/smoke-test.md`](checklists/smoke-test.md)
6. [`prompts/ai-cae-general.md`](prompts/ai-cae-general.md)
7. [`prompts/pcschematic-direct-motor-starter.md`](prompts/pcschematic-direct-motor-starter.md)
8. [`docs/mcp-toolbox-roadmap.md`](docs/mcp-toolbox-roadmap.md)
9. [`docs/deep-solver-bridge-mcp.md`](docs/deep-solver-bridge-mcp.md)
10. [`docs/codex-mcp-skill-setup.md`](docs/codex-mcp-skill-setup.md)
11. [`docs/local-mcp-source-audit.md`](docs/local-mcp-source-audit.md)

<!-- AI-CAE:fluent-weld-pool-example:START -->
## Highlighted Fluent Welding Example

- [`examples/fluent-sinusoidal-weld-pool`](examples/fluent-sinusoidal-weld-pool/README.md):
  a public-safe Stage A Ansys Fluent weld-pool validation workflow with a
  sinusoidal moving heat-source UDF, PyFluent runner, MP4 postprocessing scripts,
  melt-depth CSV/curve outputs, and credibility notes.
<!-- AI-CAE:fluent-weld-pool-example:END -->

## COMSOL Cube Smoke Test

- [`examples/comsol-cube-10mm`](examples/comsol-cube-10mm/README.md):
  the first solver-native smoke case for the COMSOL bridge. It builds a real
  10 mm cube through the COMSOL Java API, meshes it, and saves an `.mph` model
  when a licensed local COMSOL installation is available.
## Highlighted COMSOL EHD Drying Example

- [`examples/comsol-ehd-soybean-drying`](examples/comsol-ehd-soybean-drying/README.md):
  a staged, public-safe COMSOL workflow for equivalent EHD ion-wind-assisted
  soybean drying, with a prompt, evidence checklist, bridge-plan workflow, and
  COMSOL Java API smoke-template path.

- [`examples/comsol-pm-motor-nvh`](examples/comsol-pm-motor-nvh/README.md):
  a checkpointed, public-safe COMSOL Java API workflow for permanent-magnet
  motor electromagnetic, structural, acoustic, and Campbell evidence.

## MCP Smoke Workflow

- [`examples/mcp-smoke-workflows`](examples/mcp-smoke-workflows/README.md):
  the smallest clone-and-run workflow for validating the toolbox layer before
  connecting real commercial solvers.

## Additional Bridge Examples

- [`examples/aedt-wireless-power`](examples/aedt-wireless-power/README.md):
  Maxwell-oriented project, matrix, polarity, reciprocity, and field-evidence gates.
- [`examples/ansys-mechanical-static`](examples/ansys-mechanical-static/README.md):
  structural result-summary contract for Solved state, MAPDL, reactions, mesh,
  RST, numeric exports, and images.
- [`examples/hypermesh-meshing`](examples/hypermesh-meshing/README.md):
  CAD import, nonzero mesh, quality, and solver-deck acceptance flow.
- [`examples/lammps-tension`](examples/lammps-tension/README.md):
  potential-free parser smoke plus separate LAMMPS and OVITO evidence layout.

## Tests

```powershell
python -m unittest discover -s tests
```

The tests validate aliases, solver-scoped tools, smoke-template generation,
Mechanical evidence gates, GUI-versus-scripting capability checks, log signals,
and evidence classification. They do not require commercial CAE software.

## Status

This repository is in bridge-preview status. It includes public documentation,
local discovery/configuration, solver-scoped MCP packages, 11 Codex skills,
traceable runs, evidence grading, and smoke templates for the supported bridge
profiles. Real solver validation still depends on each user's installed
software, API packages, license state, and model inputs.

## License

MIT. See [`LICENSE`](LICENSE).
