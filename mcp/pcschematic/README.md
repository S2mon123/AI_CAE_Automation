# PCSCHEMATIC MCP Package

This package starts the shared AI CAE MCP server with the `pcschematic` profile.
It exposes PCSCHEMATIC installation and COM/OLE evidence checks. Deeper drawing
automation should be added only against user-owned installations and official
local API documentation.

## Start

```powershell
.\.venv\Scripts\python.exe mcp\pcschematic\server.py
```

Run `ai-cae-toolbox setup` first so executable, root, TLB, database, and symbol
paths remain in ignored private config.
