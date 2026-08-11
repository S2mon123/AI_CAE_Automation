[CmdletBinding()]
param(
    [string]$RobotStudioInstallDir = "",
    [int]$BridgePort = 47625,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
if (Get-Process RobotStudio -ErrorAction SilentlyContinue) {
    throw "Close RobotStudio before installing or updating the MCP Add-In."
}
if (-not $RobotStudioInstallDir) {
    $entry = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*", `
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -like "ABB RobotStudio 2025*" } |
        Select-Object -First 1
    if (-not $entry) { throw "ABB RobotStudio 2025 was not found." }
    $RobotStudioInstallDir = $entry.InstallLocation
}
$RobotStudioInstallDir = [IO.Path]::GetFullPath($RobotStudioInstallDir)
if (-not $SkipBuild) {
    & (Join-Path $PSScriptRoot "build_extension.ps1") -RobotStudioInstallDir $RobotStudioInstallDir -Configuration Release
    if ($LASTEXITCODE -ne 0) { throw "Build failed." }
}

$extensionRoot = Split-Path -Parent $PSScriptRoot
$assembly = Join-Path $extensionRoot "src\RobotStudioMcpExtension\bin\Release\RobotStudioMcpExtension.dll"
if (-not (Test-Path -LiteralPath $assembly)) { throw "Built extension assembly is missing." }
$legacyAddinsRoot = Join-Path $RobotStudioInstallDir "Bin\Addins"
$legacyDestination = Join-Path $legacyAddinsRoot "RobotStudioMcpBridge"
if (Test-Path -LiteralPath $legacyDestination) {
    if ([IO.Path]::GetFileName($legacyDestination) -ne "RobotStudioMcpBridge") {
        throw "Unexpected legacy Add-In target path."
    }
    Remove-Item -LiteralPath $legacyDestination -Recurse -Force
}
$legacyArtifacts = @(
    (Join-Path $legacyAddinsRoot "RobotStudioMcpExtension.dll"),
    (Join-Path $legacyAddinsRoot "RobotStudioMcpExtension.pdb"),
    (Join-Path $legacyAddinsRoot "RobotStudioMcpExtension.rsaddin")
)
foreach ($path in $legacyArtifacts) {
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
}

$distributionPackagesRoot = [IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA "ABB\DistributionPackages")).TrimEnd('\')
$packageName = "AICAEAutomationLab.RobotStudioMcpBridge-0.1.0"
$invalidLegacyPackage = Join-Path $distributionPackagesRoot "AI-CAE-Automation-Lab.RobotStudioMcpBridge-0.1.0"
if (Test-Path -LiteralPath $invalidLegacyPackage) {
    if ([IO.Path]::GetFileName($invalidLegacyPackage) -ne "AI-CAE-Automation-Lab.RobotStudioMcpBridge-0.1.0") {
        throw "Unexpected legacy distribution package path."
    }
    Remove-Item -LiteralPath $invalidLegacyPackage -Recurse -Force
}
$packageRoot = [IO.Path]::GetFullPath((Join-Path $distributionPackagesRoot $packageName))
$expectedPrefix = $distributionPackagesRoot + '\'
if (-not $packageRoot.StartsWith($expectedPrefix, [StringComparison]::OrdinalIgnoreCase) -or
    [IO.Path]::GetFileName($packageRoot) -ne $packageName) {
    throw "Resolved distribution package path is unsafe."
}
if (Test-Path -LiteralPath $packageRoot) {
    Remove-Item -LiteralPath $packageRoot -Recurse -Force
}
$addinsRoot = Join-Path $packageRoot "RobotStudio\Add-In"
New-Item -ItemType Directory -Path $addinsRoot -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $extensionRoot "package\Manifest.xml") `
    -Destination (Join-Path $packageRoot "Manifest.xml") -Force
Copy-Item -LiteralPath $assembly -Destination (Join-Path $addinsRoot "RobotStudioMcpExtension.dll") -Force
$pdb = [IO.Path]::ChangeExtension($assembly, ".pdb")
if (Test-Path -LiteralPath $pdb) {
    Copy-Item -LiteralPath $pdb -Destination (Join-Path $addinsRoot "RobotStudioMcpExtension.pdb") -Force
}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "RobotStudioMcpExtension.rsaddin") `
    -Destination (Join-Path $addinsRoot "RobotStudioMcpExtension.rsaddin") -Force

$localRoot = Join-Path $env:LOCALAPPDATA "RobotStudioMCP"
New-Item -ItemType Directory -Path $localRoot -Force | Out-Null
$tokenFile = Join-Path $localRoot "bridge-token"
if (-not (Test-Path -LiteralPath $tokenFile)) {
    $bytes = New-Object byte[] 32
    $random = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $random.GetBytes($bytes) } finally { $random.Dispose() }
    [IO.File]::WriteAllText($tokenFile, [Convert]::ToBase64String($bytes), [Text.UTF8Encoding]::new($false))
}
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent().User
$security = New-Object Security.AccessControl.FileSecurity
$security.SetAccessRuleProtection($true, $false)
$security.AddAccessRule((New-Object Security.AccessControl.FileSystemAccessRule(
    $currentUser, [Security.AccessControl.FileSystemRights]::FullControl, [Security.AccessControl.AccessControlType]::Allow)))
[IO.File]::SetAccessControl($tokenFile, $security)

$workspace = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "RobotStudioMCP\workspace"
New-Item -ItemType Directory -Path $workspace -Force | Out-Null
$config = [ordered]@{
    host = "127.0.0.1"
    port = $BridgePort
    token_file = $tokenFile
    max_payload_bytes = 4194304
    max_request_timeout_ms = 300000
    controller_scope = "virtual_only"
    workspace = $workspace
    robotstudio_install_dir = $RobotStudioInstallDir
}
$configPath = Join-Path $localRoot "bridge-settings.json"
[IO.File]::WriteAllText($configPath, ($config | ConvertTo-Json -Depth 4), [Text.UTF8Encoding]::new($false))

Write-Output "Installed per-user distribution package: $packageRoot"
Write-Output "Installed Add-In files: $addinsRoot\RobotStudioMcpExtension.*"
Write-Output "Shared config: $configPath"
Write-Output "Start RobotStudio 2025.3 and open/create a Station to auto-load the bridge."
Write-Warning "ABB requires a RobotStudio Premium runtime license for Add-Ins that reference ABB.Robotics.RobotStudio.dll."
Write-Output "Undo: robotstudio_extension\installer\uninstall_extension.ps1"
