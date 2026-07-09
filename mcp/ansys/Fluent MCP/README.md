# Ansys Fluent MCP Package

This package starts the shared AI CAE MCP server with the `fluent` profile. It
exposes Fluent journal execution, Ansys installation checks, and common evidence
tools.

## Start

```powershell
.\.venv\Scripts\python.exe "mcp\ansys\Fluent MCP\server.py"
```

Run `ai-cae-toolbox setup` first. A root Ansys folder alone is not treated as a
working Fluent bridge; `fluent.exe` must be discovered or configured.

