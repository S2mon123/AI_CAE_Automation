# MCP Automation Toolbox Roadmap

This project is moving from a prompt library into a small solver bridge and
evidence toolkit. The goal is not to replace commercial CAE software. The goal
is to let an AI agent create traceable runs, call controlled tools, inspect
evidence, and refuse to claim success without logs and exported artifacts.

## Positioning

The toolbox is centered on this loop:

```text
prompt -> env check -> run record -> controlled execution -> evidence scan -> credibility grade -> report
```

This keeps the public project distinct from implementation-heavy CAE agent hubs.
It focuses on reproducibility, evidence contracts, and local solver bridge
patterns.

## Milestone 1: Local Evidence Toolkit

- `ai-cae-toolbox env-check`: detect local automation paths without launching
  commercial tools.
- `ai-cae-toolbox create-run`: create a run folder with `run.json`, `run.log`,
  and standard subfolders.
- `ai-cae-toolbox scan-evidence`: inventory logs, solver outputs, scripts,
  exported data, and visual evidence.
- `ai-cae-toolbox generate-report`: write a reviewable `report.md` with a
  credibility grade.

## Milestone 2: MCP Server

Expose the same functions as MCP tools:

- `env_check`
- `create_run_record`
- `scan_run_evidence`
- `generate_run_report`

This server is intentionally small. It should be easy to inspect, easy to
disable, and hard to misuse.

## Milestone 3: Solver Adapters

Add adapter modules one solver at a time. The first public adapters are minimal
execution/check wrappers that write logs and return status objects.

| Adapter | First useful tool | Evidence target |
|---|---|---|
| Abaqus | noGUI script or `.inp` job | `.sta`, `.msg`, `.dat`, `.odb` presence |
| Fluent | run a journal file | transcript, `.cas`, `.dat`, images, CSV |
| COMSOL | run batch model or Java API script | log, `.mph`, exported tables |
| MATLAB/Simulink | run script or model test | diary log, figures, MAT/CSV |
| PCSCHEMATIC | verify install paths first, then COM/OLE and export lists | project file, PDF, terminal/component lists |

## Credibility Levels

| Grade | Meaning |
|---|---|
| `dry-run` | Run folder exists, but evidence is incomplete. |
| `functional-validation` | There is a log and an input/script or solver output. |
| `visual-validation` | There is a log and visual export. |
| `engineering-draft` | Logs, outputs, and numeric or visual evidence exist. |
| `report-grade` | Logs, outputs, numeric data, visual evidence, and a report exist. |

## Public Release Rules

- Keep local paths in environment variables or private configs.
- Do not commit paid course material, vendor manuals, symbol libraries, or
  proprietary databases.
- Do not commit raw heavy solver outputs unless they are tiny, synthetic, and
  clearly licensed for publication.
- Do not claim that an adapter works until a smoke test has logs and exported
  artifacts.
