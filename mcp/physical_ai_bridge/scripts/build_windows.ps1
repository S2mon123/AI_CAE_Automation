[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$OutputDirectory,
    [string]$RobotStudioBin = "",
    [switch]$BridgeOnly
)
$ErrorActionPreference = 'Stop'
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDirectory
$csc = Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
if (-not (Test-Path -LiteralPath $csc)) { throw '.NET Framework 4 compiler required.' }
$out = [IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $out -Force | Out-Null
& $csc /nologo /target:exe /platform:x86 /optimize+ /r:System.Web.Extensions.dll "/out:$out\PhysicalAI.ReadOnlyBridge.exe" "$root\win7\ReadOnlyBridge.cs"
if ($LASTEXITCODE -ne 0) { throw 'Win7 x86 bridge build failed.' }
if (-not $BridgeOnly) {
    if (-not $RobotStudioBin -or -not [IO.Path]::IsPathRooted($RobotStudioBin)) { throw 'Explicit installed RobotStudio 2025.3 Bin path required.' }
    $sdk = Join-Path $RobotStudioBin 'ABB.Robotics.Controllers.PC.dll'
    $version = [Diagnostics.FileVersionInfo]::GetVersionInfo($sdk).FileVersion
    if (-not $version.StartsWith('25.3.')) { throw 'Expected installed 25.3 SDK.' }
    & $csc /nologo /target:exe /platform:x64 /optimize+ /r:System.Web.Extensions.dll "/r:$sdk" "/out:$out\PhysicalAI.AbbReadOnly.exe" "$root\windows_abb_proxy\ReadOnlyProxy.cs"
    if ($LASTEXITCODE -ne 0) { throw 'ABB proxy build failed.' }
    '<configuration><startup><supportedRuntime version="v4.0" sku=".NETFramework,Version=v4.8" /></startup></configuration>' | Set-Content -LiteralPath "$out\PhysicalAI.AbbReadOnly.exe.config" -Encoding UTF8
}
Write-Output "Built local executables in $out. No vendor DLLs copied; no deployment or device connection performed."
