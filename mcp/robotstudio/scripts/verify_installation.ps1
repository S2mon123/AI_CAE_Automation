$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) { throw "Python virtual environment is missing." }

& $python (Join-Path $PSScriptRoot "probe_environment.py")
$environmentExit = $LASTEXITCODE
& $python (Join-Path $PSScriptRoot "stdio_smoke.py")
if ($LASTEXITCODE -ne 0) { throw "MCP stdio smoke test failed." }
& codex mcp get robotstudio
if ($LASTEXITCODE -ne 0) { throw "Codex robotstudio registration is missing." }

if ($environmentExit -ne 0) {
    Write-Warning "RobotStudio 2025 installation was not detected, but the MCP protocol surface passed."
}
Write-Output "Static installation verification completed. Run probe_bridge.py while RobotStudio and the Add-In are active."
