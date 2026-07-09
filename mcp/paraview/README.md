# ParaView MCP Package

This package starts the shared AI CAE MCP server with the `paraview` profile. It
exposes ParaView `pvpython` checks, postprocessing script execution, and common
run/evidence tools.

## Start

```powershell
.\.venv\Scripts\python.exe mcp\paraview\server.py
```

Use this bridge for reproducible postprocessing and screenshots after solver
runs.
