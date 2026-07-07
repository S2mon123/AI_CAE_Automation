# AI CAE Automation Lab

An open, reproducible knowledge and tooling repo for AI-assisted CAE automation.

The goal is simple: turn simulation work from "prompt and hope" into a traceable loop:

```text
task intent -> environment check -> model setup -> real solver run -> evidence export -> review note
```

This repository is being built as a public-facing companion to a private Obsidian knowledge base. It contains only rewritten workflows, checklists, prompt patterns, and lightweight utilities. Private notes, licensed course materials, proprietary models, credentials, and raw solver outputs are intentionally excluded.

## Scope

- AI-assisted CAE and engineering documentation workflows for Abaqus, Ansys Fluent, Ansys Mechanical/Workbench, COMSOL, MATLAB/Simulink, OpenFOAM, ParaView, and PCSCHEMATIC Automation.
- MCP and desktop bridge patterns for connecting agents to local engineering software.
- Prompt templates that force path checks, real execution, evidence export, and credibility grading.
- Smoke tests and evidence-chain checklists for simulation automation.
- Example project layouts for drilling, external flow, heat-transfer simulations, and electrical CAD documentation.

## Repository Map

| Path | Purpose |
|---|---|
| `docs/` | Architecture, workflow, software matrix, publishing plan |
| `prompts/` | Copy-ready prompt patterns for CAE automation |
| `checklists/` | Smoke test and evidence-chain checklists |
| `mcp/` | MCP integration notes and local bridge design |
| `codex-skills/` | Installable Codex skill packs for evidence-first CAE tasks |
| `examples/` | Public example layouts, without private solver assets |
| `configs/` | Public-safe configuration examples |
| `scripts/` | Small command-line helpers |
| `src/ai_cae_lab/` | Python package for reusable utilities |

## Quick Start

```powershell
git clone <your-repo-url>
cd AI-CAE-Automation-Lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe scripts\env_check.py --json
```

The environment checker does not start commercial software. It only reports what can be found on the machine, so it is safe to run before a real task.

## Codex-Ready Install

Install the MCP toolbox and copy the skill packs into Codex:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
.\.venv\Scripts\python.exe scripts\install_codex_assets.py --install-skills --force
.\.venv\Scripts\python.exe scripts\install_codex_assets.py --write-mcp-toml .\private\codex-mcp.local.toml
```

Then add the generated TOML block to the local Codex `config.toml`, replacing optional solver paths with real local paths. See [`docs/codex-mcp-skill-setup.md`](docs/codex-mcp-skill-setup.md).

The installable skills are:

- `ai-cae-run-manager`
- `abaqus-evidence-simulation`
- `fluent-evidence-cfd`
- `comsol-evidence-multiphysics`
- `pcschematic-evidence-cad`

## MCP Toolbox Preview

The first implementation milestone adds a local toolbox that can be used from the command line or exposed as an MCP server.

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
.\.venv\Scripts\ai-cae-toolbox.exe env-check --json
.\.venv\Scripts\ai-cae-toolbox.exe list-skills --json
.\.venv\Scripts\ai-cae-toolbox.exe list-adapters --json
.\.venv\Scripts\ai-cae-toolbox.exe create-run --solver fluent --case sinusoidal-welding-smoke --objective "Validate the bridge workflow"
.\.venv\Scripts\ai-cae-toolbox.exe scan-evidence runs\<run-id>
.\.venv\Scripts\ai-cae-toolbox.exe generate-report runs\<run-id>
.\.venv\Scripts\ai-cae-mcp-server.exe
```

The MCP server currently exposes environment checks, skill listings, adapter listings, run record creation, evidence scanning, report generation, and minimal solver adapters for Abaqus, Ansys Fluent, Ansys Workbench, COMSOL, and PCSCHEMATIC checks. Solver adapters write logs and return status objects; they do not claim engineering success without evidence.

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
9. [`docs/codex-mcp-skill-setup.md`](docs/codex-mcp-skill-setup.md)
10. [`docs/local-mcp-source-audit.md`](docs/local-mcp-source-audit.md)

## Status

This repository is in early public-structure setup. The first stable milestone is a clean documentation and local-toolbox release with environment checks, prompt patterns, traceable run records, evidence scanning, and example project folders.

## License

MIT. See [`LICENSE`](LICENSE).
