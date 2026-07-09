# Ansys MCP Adapters

This folder documents the public-safe Ansys MCP surface provided by the shared
`ai-cae-mcp-server` entry point. It covers the first minimal adapters for Fluent
and Workbench-style batch workflows.

## Tools

| Tool | Purpose |
|---|---|
| `ansys_check_installation` | Check configured Ansys root, Fluent path, and Workbench path without launching products. |
| `fluent_run_journal_file` | Run a Fluent journal in batch mode and capture logs. |
| `ansys_run_workbench_journal_file` | Run an Ansys Workbench journal with `RunWB2.exe -B -R <journal>`. |

## Environment Variables

| Variable | Meaning |
|---|---|
| `ANSYS_ROOT` | Root folder that contains version folders such as `v252`. |
| `FLUENT_EXE` | Path to `fluent.exe` or `fluent`. |
| `FLUENT_ROOT` | Ansys root used to discover Fluent. |
| `WORKBENCH_EXE` | Path to `RunWB2.exe`. |
| `ANSYS_WORKBENCH_EXE` | Alternative path variable for `RunWB2.exe`. |

## Recommended Skills

Use `fluent-evidence-cfd` for Fluent tasks and `ai-cae-run-manager` for evidence
management.

## Minimal Fluent Workflow

```text
env_check
create_run_record(solver="fluent", case_name="external-flow-smoke")
fluent_run_journal_file(journal_path="runs/<run>/scripts/run.jou", run_dir="runs/<run>")
scan_run_evidence(run_dir="runs/<run>")
generate_run_report(run_dir="runs/<run>")
```

## Minimal Workbench Workflow

```text
env_check
create_run_record(solver="ansys-workbench", case_name="mechanical-smoke")
ansys_run_workbench_journal_file(journal_path="runs/<run>/scripts/run.wbjn", run_dir="runs/<run>")
scan_run_evidence(run_dir="runs/<run>")
generate_run_report(run_dir="runs/<run>")
```

## Public Release Rule

Do not copy third-party MCP server code into this repository unless license and
attribution are handled deliberately. Keep Workbench projects, Fluent `.cas/.dat`
files, private geometry, and large screenshots out of git.
