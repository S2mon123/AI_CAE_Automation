[CmdletBinding()]
param(
    [string]$Workspace = (Join-Path ([Environment]::GetFolderPath("MyDocuments")) "RobotStudioMCP\workspace"),
    [int]$BridgePort = 47625
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$localRoot = Join-Path $env:LOCALAPPDATA "RobotStudioMCP"
$tokenFile = Join-Path $localRoot "bridge-token"
if (-not (Test-Path -LiteralPath $python)) { throw "Install the Python server first: scripts\install_python_server.ps1" }
if (-not (Test-Path -LiteralPath $tokenFile)) { throw "Install the RobotStudio extension first to create its private token." }

$existing = (& codex mcp list 2>$null | Out-String)
if ($existing -match "(?m)^robotstudio\s") {
    & codex mcp remove robotstudio
    if ($LASTEXITCODE -ne 0) { throw "Failed to remove the previous robotstudio MCP entry." }
}

& codex mcp add robotstudio `
    --env "ROBOTSTUDIO_MCP_WORKSPACE=$Workspace" `
    --env "ROBOTSTUDIO_MCP_BRIDGE_HOST=127.0.0.1" `
    --env "ROBOTSTUDIO_MCP_BRIDGE_PORT=$BridgePort" `
    --env "ROBOTSTUDIO_MCP_CONTROLLER_SCOPE=virtual_only" `
    --env "ROBOTSTUDIO_MCP_TOKEN_FILE=$tokenFile" `
    -- $python -m robotstudio_mcp
if ($LASTEXITCODE -ne 0) { throw "Codex MCP registration failed." }

& codex mcp get robotstudio
Write-Output "Registered Codex MCP server 'robotstudio'. Restart Codex or start a new task to load it."
Write-Output "Undo: codex mcp remove robotstudio"
