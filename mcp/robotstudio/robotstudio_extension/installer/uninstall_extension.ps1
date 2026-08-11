[CmdletBinding()]
param([string]$RobotStudioInstallDir = "")

$ErrorActionPreference = "Stop"
if (Get-Process RobotStudio -ErrorAction SilentlyContinue) { throw "Close RobotStudio before uninstalling the MCP Add-In." }
if (-not $RobotStudioInstallDir) {
    $entry = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*", `
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -like "ABB RobotStudio 2025*" } |
        Select-Object -First 1
    if (-not $entry) { throw "ABB RobotStudio 2025 was not found." }
    $RobotStudioInstallDir = $entry.InstallLocation
}
$installRoot = [IO.Path]::GetFullPath($RobotStudioInstallDir).TrimEnd('\') + '\'
$legacyAddinsRoot = [IO.Path]::GetFullPath((Join-Path $installRoot "Bin\Addins"))
$destination = [IO.Path]::GetFullPath((Join-Path $legacyAddinsRoot "RobotStudioMcpBridge"))
if (-not $destination.StartsWith($installRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Resolved Add-In path is outside the RobotStudio installation."
}
if ([IO.Path]::GetFileName($destination) -ne "RobotStudioMcpBridge") { throw "Unexpected Add-In target path." }
if (Test-Path -LiteralPath $destination) {
    Remove-Item -LiteralPath $destination -Recurse -Force
    Write-Output "Removed Add-In directory: $destination"
}
$artifacts = @(
    (Join-Path $legacyAddinsRoot "RobotStudioMcpExtension.rsaddin"),
    (Join-Path $legacyAddinsRoot "RobotStudioMcpExtension.dll"),
    (Join-Path $legacyAddinsRoot "RobotStudioMcpExtension.pdb")
)
foreach ($path in $artifacts) {
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Force
        Write-Output "Removed Add-In artifact: $path"
    }
}
$packageName = "AICAEAutomationLab.RobotStudioMcpBridge-0.1.0"
$packageRoots = @(
    (Join-Path $env:LOCALAPPDATA "ABB\DistributionPackages"),
    (Join-Path $env:ProgramData "ABB\DistributionPackages"),
    (Join-Path $env:ProgramData "ABB\DistributionPackages2"),
    # Cleanup for 0.1.0 installers that used a location not scanned by RobotStudio 25.3.
    (Join-Path $env:LOCALAPPDATA "ABB\DistributionPackages2")
)
foreach ($distributionPackagesRoot in $packageRoots) {
    $distributionPackagesRoot = [IO.Path]::GetFullPath($distributionPackagesRoot).TrimEnd('\')
    foreach ($leafName in @($packageName, "AI-CAE-Automation-Lab.RobotStudioMcpBridge-0.1.0")) {
        $packageRoot = [IO.Path]::GetFullPath((Join-Path $distributionPackagesRoot $leafName))
        if (-not $packageRoot.StartsWith(($distributionPackagesRoot + '\'), [StringComparison]::OrdinalIgnoreCase) -or
            [IO.Path]::GetFileName($packageRoot) -ne $leafName) {
            throw "Resolved distribution package path is unsafe."
        }
        if (Test-Path -LiteralPath $packageRoot) {
            Remove-Item -LiteralPath $packageRoot -Recurse -Force
            Write-Output "Removed distribution package: $packageRoot"
        }
    }
}
Write-Output "The shared token/config were retained so MCP registration remains recoverable."
