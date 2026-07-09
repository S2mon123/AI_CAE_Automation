# MCP Smoke Workflows

This example shows the smallest workflow a new user should run after cloning the
repository. It validates the AI CAE Automation Lab bridge layer before any real
commercial solver task.

## 1. Install

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
```

## 2. Inspect The Toolbox

```powershell
.\.venv\Scripts\ai-cae-toolbox.exe env-check --json
.\.venv\Scripts\ai-cae-toolbox.exe list-adapters --json
.\.venv\Scripts\ai-cae-toolbox.exe list-skills --json
```

## 3. Create A Run And Write A Smoke Template

```powershell
.\.venv\Scripts\ai-cae-toolbox.exe bridge-plan --solver comsol --objective "COMSOL bridge smoke"
.\.venv\Scripts\ai-cae-toolbox.exe create-run --solver comsol --case comsol-smoke --objective "Validate bridge layer"
.\.venv\Scripts\ai-cae-toolbox.exe write-smoke-template --solver comsol --run-dir runs\<run-id> --case comsol-smoke
.\.venv\Scripts\ai-cae-toolbox.exe scan-evidence runs\<run-id>
.\.venv\Scripts\ai-cae-toolbox.exe generate-report runs\<run-id>
```

At this point the credibility grade should remain `dry-run` unless a real solver
or automation command produced logs and outputs. That is intentional.

## 4. Register MCP

Use [`../../mcp/codex-config.example.toml`](../../mcp/codex-config.example.toml)
or generate a local snippet:

```powershell
.\.venv\Scripts\python.exe scripts\install_codex_assets.py --write-mcp-toml .\private\codex-mcp.local.toml
```

Fill paths using your own local solver installations. Do not commit the private
TOML file.

## 5. Real Solver Boundary

The MCP server can prepare run folders, create smoke templates, invoke configured
solver commands, and scan evidence. It cannot provide commercial solver licenses
or guarantee that a user's local CAE installation is available.
