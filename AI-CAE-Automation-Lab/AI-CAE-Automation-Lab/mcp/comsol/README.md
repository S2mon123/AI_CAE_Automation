# COMSOL MCP Adapter

This folder documents the public-safe COMSOL MCP surface provided by the shared
`ai-cae-mcp-server` entry point. It does not bundle COMSOL, licensed manuals,
private `.mph` files, or local API documentation.

## Tools

| Tool | Purpose |
|---|---|
| `comsol_check_installation` | Check COMSOL root, batch command, Java runtime, and local API docs. |
| `comsol_run_batch_file` | Run a configured COMSOL batch command and capture logs. |

## Environment Variables

| Variable | Meaning |
|---|---|
| `COMSOL_ROOT` | COMSOL installation root that contains `Multiphysics/`. |
| `COMSOL_BATCH` | Path to `comsolbatch.exe` or equivalent batch command. |
| `COMSOL_EXE` | Path to COMSOL command when batch command is not separately configured. |
| `COMSOL_JAVA` | Path to COMSOL bundled Java runtime. |

## Recommended Skill

Use `comsol-evidence-multiphysics` together with `ai-cae-run-manager`.

## Minimal Workflow

```text
env_check
create_run_record(solver="comsol", case_name="heat-sink-smoke")
comsol_check_installation
comsol_run_batch_file(run_dir="runs/<run>", input_file="runs/<run>/inputs/model.mph", output_file="runs/<run>/outputs/model_solved.mph")
scan_run_evidence(run_dir="runs/<run>")
generate_run_report(run_dir="runs/<run>")
```

## Public Release Rule

Do not commit `.mph`, licensed documentation, local API HTML dumps, private
customer geometry, or screenshots that expose private project names.
