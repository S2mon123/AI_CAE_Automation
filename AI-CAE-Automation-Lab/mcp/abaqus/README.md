# Abaqus MCP Adapter

This folder documents the public-safe Abaqus MCP surface provided by the shared
`ai-cae-mcp-server` entry point. It does not bundle Abaqus, Dassault files,
licensed documentation, private models, or generated ODB outputs.

## Tools

| Tool | Purpose |
|---|---|
| `abaqus_run_no_gui_script` | Run an Abaqus/CAE Python script with `cae noGUI=<script>` and capture logs. |
| `abaqus_submit_input_deck` | Submit an Abaqus `.inp` input deck and capture logs. |

## Environment Variables

| Variable | Meaning |
|---|---|
| `ABAQUS_COMMAND` | Path to `abaqus`, `abaqus.bat`, or a versioned Abaqus launcher. |

## Recommended Skill

Use `abaqus-evidence-simulation` together with `ai-cae-run-manager`.

## Minimal Workflow

```text
env_check
create_run_record(solver="abaqus", case_name="beam-modal-smoke")
abaqus_run_no_gui_script(script_path="runs/<run>/scripts/model.py", run_dir="runs/<run>")
scan_run_evidence(run_dir="runs/<run>")
generate_run_report(run_dir="runs/<run>")
```

## Public Release Rule

Do not commit `.odb`, private CAD, solver logs containing private paths, vendor
manual excerpts, or customer model files.
