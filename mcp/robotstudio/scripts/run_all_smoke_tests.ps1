[CmdletBinding()]
param([switch]$IncludeLive)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) { throw "Run scripts\install_python_server.ps1 first." }

& $python -m ruff check src tests scripts
if ($LASTEXITCODE -ne 0) { throw "Ruff failed." }
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Pytest failed." }
& $python (Join-Path $PSScriptRoot "stdio_smoke.py")
if ($LASTEXITCODE -ne 0) { throw "stdio smoke failed." }
& (Join-Path $projectRoot "robotstudio_extension\installer\build_extension.ps1")
if ($LASTEXITCODE -ne 0) { throw "C# extension build failed." }
if ($IncludeLive) {
    & $python (Join-Path $PSScriptRoot "probe_bridge.py")
    if ($LASTEXITCODE -ne 0) { throw "Live bridge probe failed." }
}
Write-Output "All requested smoke tests passed."
