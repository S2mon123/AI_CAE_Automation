# Architecture

The lab is organized around a small, repeatable loop:

```text
Obsidian knowledge -> prompt template -> local environment check -> solver bridge -> evidence export -> review note
```

## Layers

| Layer | Role |
|---|---|
| Knowledge layer | Concepts, examples, prompt patterns, checklists |
| Agent layer | Codex, Claude Code, or another tool-using assistant |
| Bridge layer | MCP server, Python API, desktop plugin, socket bridge, journal file, or file queue |
| Solver layer | Abaqus, Fluent, Workbench, COMSOL, MATLAB/Simulink, OpenFOAM |
| Evidence layer | Logs, solver files, images, CSV/JSON, report notes |

## Bridge Patterns

### Python API

Use a Python package to control the solver or prepare files. This is usually the cleanest path when the vendor API is stable.

### Journal or batch script

Generate a solver-native script, run it in batch mode, and inspect logs. This is useful for Workbench, Abaqus noGUI, and repeatable workflows.

### GUI plugin or socket bridge

Run a small plugin inside the desktop software and talk to it from the agent. This helps when the active GUI session has the model state.

### File queue IPC

Write command JSON files to a queue and let the software-side bridge return result JSON files. This is easy to audit and recover.

## Evidence Contract

A task is not complete until it records:

- software path and version,
- input files,
- command or API entry point,
- run status,
- output artifacts,
- known limitations,
- credibility level.
