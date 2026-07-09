# OpenFOAM MCP Package

This package starts the shared AI CAE MCP server with the `openfoam` profile. It
exposes selected OpenFOAM command execution and common run/evidence tools.

## Start

```powershell
.\.venv\Scripts\python.exe mcp\openfoam\server.py
```

OpenFOAM may run locally or through WSL depending on the user's installation.
The bridge records commands and logs but does not bundle OpenFOAM.
