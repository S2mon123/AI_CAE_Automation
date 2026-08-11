[CmdletBinding()]
param(
    [string]$Python = "",
    [switch]$SkipDevDependencies
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $projectRoot ".venv"

if (-not $Python) {
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        & $launcher.Source -3.12 -c "import sys; print(sys.executable)" | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $Python = $launcher.Source
        }
    }
}
if (-not $Python) {
    $candidate = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($candidate) { $Python = $candidate.Source }
}
if (-not $Python) { throw "Python 3.11 or 3.12 was not found." }

if (-not (Test-Path -LiteralPath $venv)) {
    if ([IO.Path]::GetFileName($Python) -ieq "py.exe") {
        & $Python -3.12 -m venv $venv
    } else {
        & $Python -m venv $venv
    }
    if ($LASTEXITCODE -ne 0) { throw "Failed to create Python virtual environment." }
}

$venvPython = Join-Path $venv "Scripts\python.exe"
& $venvPython -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) { throw "Failed to prepare the Python build toolchain." }
if ($SkipDevDependencies) {
    & $venvPython -m pip install --editable $projectRoot
} else {
    & $venvPython -m pip install --requirement (Join-Path $projectRoot "requirements.lock")
    if ($LASTEXITCODE -eq 0) {
        & $venvPython -m pip install --editable $projectRoot --no-deps
    }
}
if ($LASTEXITCODE -ne 0) { throw "Failed to install RobotStudio MCP Python dependencies." }

Write-Output "Python server installed: $venvPython"
Write-Output "Undo: remove $venv and unregister the robotstudio MCP entry."
