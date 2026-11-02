[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$robotstudioRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent (Split-Path -Parent $robotstudioRoot)
$source = Join-Path $repoRoot "codex-skills\robotstudio-core"
$skillsRoot = Join-Path $env:USERPROFILE ".codex\skills"
$target = Join-Path $skillsRoot "robotstudio-core"

if (-not (Test-Path -LiteralPath (Join-Path $source "SKILL.md"))) {
    throw "The repository robotstudio-core skill is missing: $source"
}
New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null

if (Test-Path -LiteralPath $target) {
    $item = Get-Item -LiteralPath $target -Force
    if ($item.LinkType -eq "Junction" -and $item.Target -contains $source) {
        Write-Output "Codex skill junction is already installed: $target"
        exit 0
    }
    throw "Codex skill target already exists and was not replaced: $target"
}

New-Item -ItemType Junction -Path $target -Target $source | Out-Null
Write-Output "Installed Codex skill junction: $target"
Write-Output "Restart Codex or start a new task to discover robotstudio-core."
