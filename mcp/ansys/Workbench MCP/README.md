# Ansys Workbench MCP Package

This package starts the shared AI CAE MCP server with the `workbench` profile.
It exposes Workbench journal execution, Ansys installation checks, and common
run/evidence tools.

## Start

```powershell
.\.venv\Scripts\python.exe "mcp\ansys\Workbench MCP\server.py"
```

Run `ai-cae-toolbox setup` first so `runwb2.exe` or equivalent Workbench command
is discovered into `private/ai-cae.local.json`.

