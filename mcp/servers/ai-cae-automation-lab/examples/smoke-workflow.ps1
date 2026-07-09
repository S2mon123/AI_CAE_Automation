$ErrorActionPreference = "Stop"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
.\.venv\Scripts\ai-cae-toolbox.exe setup
. .\private\activate-ai-cae.ps1
.\.venv\Scripts\ai-cae-toolbox.exe discover --json
.\.venv\Scripts\ai-cae-toolbox.exe create-run --solver comsol --case comsol-cube-smoke --objective "Validate MCP bridge"
