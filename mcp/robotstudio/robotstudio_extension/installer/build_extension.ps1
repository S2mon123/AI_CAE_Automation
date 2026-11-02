[CmdletBinding()]
param(
    [string]$RobotStudioInstallDir = "",
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",
    [switch]$SkipContractTests
)

$ErrorActionPreference = "Stop"

function Find-RobotStudio2025 {
    $registryPaths = @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )
    $entry = Get-ItemProperty $registryPaths -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -like "ABB RobotStudio 2025*" } |
        Sort-Object DisplayVersion -Descending |
        Select-Object -First 1
    if (-not $entry -or -not $entry.InstallLocation) { throw "ABB RobotStudio 2025 was not found in the registry." }
    return [IO.Path]::GetFullPath($entry.InstallLocation)
}

function Find-MSBuild {
    $vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
    if (-not (Test-Path -LiteralPath $vswhere)) { throw "Visual Studio 2022 vswhere.exe was not found." }
    $path = & $vswhere -latest -products * -requires Microsoft.Component.MSBuild -find "MSBuild\**\Bin\MSBuild.exe" |
        Select-Object -First 1
    if (-not $path) { throw "Visual Studio 2022 MSBuild was not found." }
    return $path
}

function Get-Net48ReferencePath {
    $systemPath = "${env:ProgramFiles(x86)}\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.8"
    if (Test-Path -LiteralPath (Join-Path $systemPath "mscorlib.dll")) { return $systemPath }

    $packageVersion = "1.0.3"
    $cache = Join-Path $env:LOCALAPPDATA "RobotStudioMCP\build-cache\net48-reference-assemblies-$packageVersion"
    $found = Get-ChildItem -LiteralPath $cache -Recurse -Filter mscorlib.dll -ErrorAction SilentlyContinue |
        Where-Object { $_.DirectoryName -match '[\\/]v4\.8$' } |
        Select-Object -First 1
    if ($found) { return $found.DirectoryName }

    New-Item -ItemType Directory -Path $cache -Force | Out-Null
    $temporary = Join-Path ([IO.Path]::GetTempPath()) ("net48-reference-" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $temporary | Out-Null
    try {
        $nupkg = Join-Path $temporary "reference.nupkg"
        $zip = Join-Path $temporary "reference.zip"
        $url = "https://api.nuget.org/v3-flatcontainer/microsoft.netframework.referenceassemblies.net48/$packageVersion/microsoft.netframework.referenceassemblies.net48.$packageVersion.nupkg"
        Invoke-WebRequest -Uri $url -OutFile $nupkg -UseBasicParsing
        Copy-Item -LiteralPath $nupkg -Destination $zip
        Expand-Archive -LiteralPath $zip -DestinationPath $cache -Force
    } finally {
        if (Test-Path -LiteralPath $temporary) {
            $resolvedTemp = [IO.Path]::GetFullPath($temporary)
            $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
            if ($resolvedTemp.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase)) {
                Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
            }
        }
    }
    $found = Get-ChildItem -LiteralPath $cache -Recurse -Filter mscorlib.dll |
        Where-Object { $_.DirectoryName -match '[\\/]v4\.8$' } |
        Select-Object -First 1
    if (-not $found) { throw ".NET Framework 4.8 reference assemblies could not be prepared." }
    return $found.DirectoryName
}

if (-not $RobotStudioInstallDir) { $RobotStudioInstallDir = Find-RobotStudio2025 }
$RobotStudioInstallDir = [IO.Path]::GetFullPath($RobotStudioInstallDir)
$bin = Join-Path $RobotStudioInstallDir "Bin"
$required = @(
    "RobotStudio.exe",
    "ABB.Robotics.RobotStudio.dll",
    "ABB.Robotics.RobotStudio.Stations.dll",
    "ABB.Robotics.Controllers.PC.dll",
    "ABB.Robotics.Math.dll"
)
foreach ($file in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $bin $file))) { throw "Missing matching RobotStudio SDK file: $file" }
}
$versions = $required | ForEach-Object { [Diagnostics.FileVersionInfo]::GetVersionInfo((Join-Path $bin $_)).FileVersion }
$prefixes = @($versions | ForEach-Object { ($_ -split '\.')[0..1] -join '.' } | Select-Object -Unique)
if ($prefixes.Count -ne 1 -or $prefixes[0] -ne "25.3") {
    throw "RobotStudio and SDK assemblies must all match the audited 25.3 release. Found: $($versions -join ', ')"
}

$msbuild = Find-MSBuild
$frameworkPath = Get-Net48ReferencePath
$solution = Join-Path (Split-Path -Parent $PSScriptRoot) "RobotStudioMcpExtension.sln"
& $msbuild $solution /nologo /m /t:Rebuild "/p:Configuration=$Configuration" "/p:Platform=x64" `
    "/p:RobotStudioInstallDir=$RobotStudioInstallDir" "/p:FrameworkPathOverride=$frameworkPath"
if ($LASTEXITCODE -ne 0) { throw "RobotStudio MCP extension build failed." }

if (-not $SkipContractTests) {
    $testExe = Join-Path (Split-Path -Parent $PSScriptRoot) "tests\BridgeContractTests\bin\$Configuration\BridgeContractTests.exe"
    & $testExe
    if ($LASTEXITCODE -ne 0) { throw "C# bridge contract tests failed." }
}
Write-Output "Extension build succeeded for RobotStudio $($versions[0])."
