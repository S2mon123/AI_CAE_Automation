# MATLAB MCP Package

This package starts the shared AI CAE MCP server with the `matlab` profile. It
exposes MATLAB installation checks, batch script execution, and common
run/evidence tools.

## Start

```powershell
.\.venv\Scripts\python.exe mcp\matlab\server.py
```

Run `ai-cae-toolbox setup` first so the local MATLAB command is discovered into
`private/ai-cae.local.json`.
