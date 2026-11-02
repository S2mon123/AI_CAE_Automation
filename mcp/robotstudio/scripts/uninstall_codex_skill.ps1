[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$robotstudioRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent (Split-Path -Parent $robotstudioRoot)
$expectedSource = Join-Path $repoRoot "codex-skills\robotstudio-core"
$target = Join-Path $env:USERPROFILE ".codex\skills\robotstudio-core"

if (-not (Test-Path -LiteralPath $target)) {
    Write-Output "Codex skill junction is not installed."
    exit 0
}

$item = Get-Item -LiteralPath $target -Force
if ($item.LinkType -ne "Junction" -or $item.Target -notcontains $expectedSource) {
    throw "Refusing to remove a skill path that is not this repository's junction: $target"
}

Remove-Item -LiteralPath $target -Force
Write-Output "Removed Codex skill junction: $target"
