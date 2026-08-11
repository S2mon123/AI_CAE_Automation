[CmdletBinding()]
param([string]$RobotStudioInstallDir = "")

$ErrorActionPreference = "Stop"
if (-not $RobotStudioInstallDir) {
    $entry = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*", `
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -like "ABB RobotStudio 2025*" } |
        Select-Object -First 1
    if (-not $entry) { throw "ABB RobotStudio 2025 was not found." }
    $RobotStudioInstallDir = $entry.InstallLocation
}
$packageName = "AICAEAutomationLab.RobotStudioMcpBridge-0.1.0"
$packageCandidates = @(
    (Join-Path $env:LOCALAPPDATA "ABB\DistributionPackages\$packageName"),
    (Join-Path $env:ProgramData "ABB\DistributionPackages\$packageName"),
    (Join-Path $env:ProgramData "ABB\DistributionPackages2\$packageName")
)
$packageRoot = $packageCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $packageRoot) {
    throw "RobotStudio package was not found in a RobotStudio 25.3 search location: $($packageCandidates -join ', ')"
}
$addinsRoot = Join-Path $packageRoot "RobotStudio\Add-In"
$assembly = Join-Path $addinsRoot "RobotStudioMcpExtension.dll"
$manifest = Join-Path $addinsRoot "RobotStudioMcpExtension.rsaddin"
$packageManifest = Join-Path $packageRoot "Manifest.xml"
$config = Join-Path $env:LOCALAPPDATA "RobotStudioMCP\bridge-settings.json"
$token = Join-Path $env:LOCALAPPDATA "RobotStudioMCP\bridge-token"
foreach ($path in @($assembly, $manifest, $packageManifest, $config, $token)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing installation artifact: $path" }
}
$xsd = Join-Path $RobotStudioInstallDir "Schemas\RobotStudioAddin.xsd"
$schemas = New-Object Xml.Schema.XmlSchemaSet
$schemas.Add("urn:abb-robotics-robotstudio-addin", $xsd) | Out-Null
$readerSettings = New-Object Xml.XmlReaderSettings
$readerSettings.Schemas = $schemas
$readerSettings.ValidationType = [Xml.ValidationType]::Schema
$reader = [Xml.XmlReader]::Create($manifest, $readerSettings)
try { while ($reader.Read()) { } } finally { $reader.Dispose() }
$packageXml = [xml](Get-Content -LiteralPath $packageManifest -Raw)
if ($packageXml.DistributionPackage.Title -ne "RobotStudio MCP Read-Only Bridge" -or
    $packageXml.DistributionPackage.Tags.Tag -notcontains "RobotStudio-AddIn") {
    throw "The distribution package manifest is incomplete."
}
$settings = Get-Content -LiteralPath $config -Raw | ConvertFrom-Json
if ($settings.host -ne "127.0.0.1" -or $settings.controller_scope -ne "virtual_only") {
    throw "Installed bridge configuration violates the safety policy."
}
Write-Output "Extension installation verified: $([Diagnostics.FileVersionInfo]::GetVersionInfo($assembly).FileVersion)"
Write-Output "RobotStudio distribution package: $packageRoot"
Write-Warning "A RobotStudio Premium runtime license is required before this Add-In can load and open its bridge."
