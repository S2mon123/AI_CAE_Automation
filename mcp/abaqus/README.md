# Abaqus MCP Package

This package starts the shared AI CAE MCP server with the `abaqus` profile. It
exposes Abaqus-focused tools plus common setup, discovery, run-record, evidence,
and report tools.

## Tools

- `abaqus_run_no_gui_script`
- `abaqus_submit_input_deck`
- `env_check`
- `discover_toolchains`
- `setup_local_toolchain`
- `create_run_record`
- `scan_run_evidence`
- `generate_run_report`

## Start

From the repository root:

```powershell
.\.venv\Scripts\python.exe mcp\abaqus\server.py
```

Run `ai-cae-toolbox setup` first so local Abaqus paths are stored in
`private/ai-cae.local.json` instead of committed files.
