# MCP Solver Packages

This directory provides solver-facing MCP package entry points. The layout is
inspired by public CAE MCP repositories such as `Cai-aa/CAE-Agent-Hub`, while
the implementation remains project-owned and delegates to the shared core under
`src/ai_cae_lab`.

## Why This Directory Exists

The top of this folder keeps shared manifests, notices, and client examples.
The solver subfolders provide package-style MCP entry points for people who want
to enable one solver at a time in Codex or another MCP client.

Each solver package follows the same shape:

```text
mcp/<solver>/
  README.md
  .env.example
  pyproject.toml
  server.py
  examples/
    codex-config.example.toml
```

The package `server.py` sets `AI_CAE_MCP_SOLVERS` before starting the shared MCP
server. That limits the tools exposed to the selected solver plus common run,
discovery, evidence, and setup tools.

## Available Packages

| Package | MCP profile | Purpose |
|---|---|---|
| `mcp/abaqus` | `abaqus` | Abaqus noGUI scripts and input-deck submission |
| `mcp/ansys/Fluent MCP` | `fluent` | Fluent journal execution and CFD evidence capture |
| `mcp/ansys/Workbench MCP` | `workbench` | Workbench journal execution and Ansys install checks |
| `mcp/comsol` | `comsol` | COMSOL Java API compile, batch, MPH smoke, and validation |
| `mcp/matlab` | `matlab` | MATLAB batch script execution |
| `mcp/openfoam` | `openfoam` | OpenFOAM command execution for local or WSL cases |
| `mcp/paraview` | `paraview` | ParaView `pvpython` postprocessing |
| `mcp/pcschematic` | `pcschematic` | PCSCHEMATIC installation and COM/OLE evidence checks |

## First-Run Flow

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
.\.venv\Scripts\ai-cae-toolbox.exe setup
```

Then register the solver package you need. For COMSOL, the command is:

```powershell
.\.venv\Scripts\python.exe mcp\comsol\server.py
```

For a full toolbox server that exposes every solver, use:

```powershell
.\.venv\Scripts\ai-cae-mcp-server.exe
```

## MIT Compliance

The architecture here is intentionally compatible with the style of MIT-licensed
CAE/MCP projects. This repository does not vendor upstream source code. If a
future contribution copies MIT-licensed files, keep the original copyright and
license notice with the copied files and record the attribution in
`mcp/THIRD_PARTY_NOTICES.md`.
