# MIT Reference And MCP Restructure

This note documents how this repository references public MIT-licensed CAE/MCP
work without disguising copied code as original work.

## Reference Point

`Cai-aa/CAE-Agent-Hub` is used as a public architecture reference for organizing
CAE automation assets into solver-specific MCP packages and skill packages.

The adopted structural ideas are:

- per-solver MCP folders with `README.md`, `.env.example`, `pyproject.toml`,
  `server.py`, and `examples/`;
- clear separation between shared core code and solver package entry points;
- local environment discovery instead of committed author-specific paths;
- explicit examples and smoke workflows;
- MIT-compatible attribution and third-party notices.

## What Is Not Copied

This repository does not vendor upstream source files from `Cai-aa/CAE-Agent-Hub`.
The solver package entry points call this project's own shared core under
`src/ai_cae_lab`.

If source code from an MIT-licensed project is imported later, the contribution
must preserve the original copyright notice, preserve the MIT license text, and
record the copied file paths in `mcp/THIRD_PARTY_NOTICES.md`.

## Current Implementation

The solver-specific packages under `mcp/` set `AI_CAE_MCP_SOLVERS` before
starting `ai_cae_lab.mcp_server`. This means users can register only the solver
they need:

```powershell
.\.venv\Scripts\python.exe mcp\comsol\server.py
.\.venv\Scripts\python.exe mcp\abaqus\server.py
.\.venv\Scripts\python.exe "mcp\ansys\Fluent MCP\server.py"
```

The full toolbox server remains available through:

```powershell
.\.venv\Scripts\ai-cae-mcp-server.exe
```

## Practical Rule

Architecture imitation is acceptable when the implementation is original and
the reference is acknowledged. Direct code copying is also allowed by MIT only
when the original copyright and license notice are retained.
