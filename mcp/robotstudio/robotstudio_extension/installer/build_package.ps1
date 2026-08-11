[CmdletBinding()]
param(
    [string]$RobotStudioInstallDir = "",
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",
    [string]$OutputDirectory = "",
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$extensionRoot = Split-Path -Parent $PSScriptRoot
$packageName = "AICAEAutomationLab.RobotStudioMcpBridge-0.1.0"

if (-not $SkipBuild) {
    $buildArguments = @("-Configuration", $Configuration)
    if ($RobotStudioInstallDir) { $buildArguments += @("-RobotStudioInstallDir", $RobotStudioInstallDir) }
    & (Join-Path $PSScriptRoot "build_extension.ps1") @buildArguments
    if ($LASTEXITCODE -ne 0) { throw "Extension build failed." }
}

if (-not $OutputDirectory) { $OutputDirectory = Join-Path $extensionRoot "dist" }
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$outputPath = Join-Path $OutputDirectory "$packageName.rspak"

$assembly = Join-Path $extensionRoot "src\RobotStudioMcpExtension\bin\$Configuration\RobotStudioMcpExtension.dll"
$addinManifest = Join-Path $PSScriptRoot "RobotStudioMcpExtension.rsaddin"
$packageManifest = Join-Path $extensionRoot "package\Manifest.xml"
foreach ($path in @($assembly, $addinManifest, $packageManifest)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing package input: $path" }
}

$temporaryRoot = Join-Path ([IO.Path]::GetTempPath()) ("robotstudio-mcp-rspak-" + [Guid]::NewGuid().ToString("N"))
$packageRoot = Join-Path $temporaryRoot $packageName
$addinRoot = Join-Path $packageRoot "RobotStudio\Add-In"
New-Item -ItemType Directory -Path $addinRoot -Force | Out-Null
try {
    Copy-Item -LiteralPath $packageManifest -Destination (Join-Path $packageRoot "manifest.xml")
    Copy-Item -LiteralPath $addinManifest -Destination (Join-Path $addinRoot "RobotStudioMcpExtension.rsaddin")
    Copy-Item -LiteralPath $assembly -Destination (Join-Path $addinRoot "RobotStudioMcpExtension.dll")
    $pdb = [IO.Path]::ChangeExtension($assembly, ".pdb")
    if (Test-Path -LiteralPath $pdb) {
        Copy-Item -LiteralPath $pdb -Destination (Join-Path $addinRoot "RobotStudioMcpExtension.pdb")
    }

    if (Test-Path -LiteralPath $outputPath) { Remove-Item -LiteralPath $outputPath -Force }
    Add-Type -AssemblyName System.IO.Compression
    $fileStream = [IO.File]::Open($outputPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::ReadWrite)
    try {
        $archive = New-Object IO.Compression.ZipArchive(
            $fileStream,
            [IO.Compression.ZipArchiveMode]::Create,
            $false
        )
        try {
            foreach ($file in Get-ChildItem -LiteralPath $temporaryRoot -Recurse -File) {
                $entryName = $file.FullName.Substring($temporaryRoot.Length + 1).Replace('\', '/')
                $entry = $archive.CreateEntry($entryName, [IO.Compression.CompressionLevel]::Optimal)
                $sourceStream = [IO.File]::OpenRead($file.FullName)
                $entryStream = $entry.Open()
                try { $sourceStream.CopyTo($entryStream) } finally {
                    $entryStream.Dispose()
                    $sourceStream.Dispose()
                }
            }
        } finally {
            $archive.Dispose()
        }
    } finally {
        $fileStream.Dispose()
    }
} finally {
    $resolvedTemporaryRoot = [IO.Path]::GetFullPath($temporaryRoot)
    $systemTemporaryRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if ($resolvedTemporaryRoot.StartsWith($systemTemporaryRoot, [StringComparison]::OrdinalIgnoreCase) -and
        [IO.Path]::GetFileName($resolvedTemporaryRoot).StartsWith("robotstudio-mcp-rspak-")) {
        Remove-Item -LiteralPath $resolvedTemporaryRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Output "Created RobotStudio distribution package: $outputPath"
Write-Warning "RobotStudio Premium is required at runtime because the Add-In references ABB.Robotics.RobotStudio.dll."
