# AI CAE Automation Lab

An open, reproducible knowledge and tooling repo for AI-assisted CAE automation.

The goal is simple: turn simulation work from "prompt and hope" into a traceable loop:

```text
task intent -> environment check -> model setup -> real solver run -> evidence export -> review note
```

This repository is being built as a public-facing companion to a private Obsidian knowledge base. It contains only rewritten workflows, checklists, prompt patterns, and lightweight utilities. Private notes, licensed course materials, proprietary models, credentials, and raw solver outputs are intentionally excluded.

## Scope

- AI-assisted CAE workflows for Abaqus, Ansys Fluent, Ansys Mechanical/Workbench, COMSOL, MATLAB/Simulink, OpenFOAM, and ParaView.
- MCP and desktop bridge patterns for connecting agents to local engineering software.
- Prompt templates that force path checks, real execution, evidence export, and credibility grading.
- Smoke tests and evidence-chain checklists for simulation automation.
- Example project layouts for drilling, external flow, and heat-transfer simulations.

## Repository Map

| Path | Purpose |
|---|---|
| `docs/` | Architecture, workflow, software matrix, publishing plan |
| `prompts/` | Copy-ready prompt patterns for CAE automation |
| `checklists/` | Smoke test and evidence-chain checklists |
| `mcp/` | MCP integration notes and local bridge design |
| `examples/` | Public example layouts, without private solver assets |
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

## Core Principles

1. Never claim a simulation succeeded without solver evidence.
2. Separate preview, dry-run, functional validation, engineering draft, and report-grade results.
3. Record executable paths, software versions, license status, input files, commands, logs, and exported artifacts.
4. Treat solver failures as useful data, not embarrassment.
5. Keep public examples free of private files and licensed training materials.

## Recommended Reading Order

1. [`docs/architecture.md`](docs/architecture.md)
2. [`docs/workflow.md`](docs/workflow.md)
3. [`docs/software-matrix.md`](docs/software-matrix.md)
4. [`checklists/smoke-test.md`](checklists/smoke-test.md)
5. [`prompts/ai-cae-general.md`](prompts/ai-cae-general.md)

## Status

This repository is in early public-structure setup. The first stable milestone is a clean documentation release with environment checks, prompt patterns, and example project folders.

## License

MIT. See [`LICENSE`](LICENSE).

