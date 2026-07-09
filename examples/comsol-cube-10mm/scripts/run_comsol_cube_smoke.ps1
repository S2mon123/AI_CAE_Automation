param(
  [string]$ComsolCompile = $env:COMSOL_COMPILE,
  [string]$ComsolBatch = $env:COMSOL_BATCH,
  [string]$OutputFile = "outputs\comsol_cube_10mm.mph"
)

$ErrorActionPreference = "Stop"
$ExampleRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ScriptsDir = Join-Path $ExampleRoot "scripts"
$LogsDir = Join-Path $ExampleRoot "logs"
$OutputsDir = Join-Path $ExampleRoot "outputs"
New-Item -ItemType Directory -Force -Path $LogsDir, $OutputsDir | Out-Null

if (-not $ComsolCompile) { throw "Set COMSOL_COMPILE or pass -ComsolCompile." }
if (-not $ComsolBatch) { throw "Set COMSOL_BATCH or pass -ComsolBatch." }
if (-not (Test-Path -LiteralPath $ComsolCompile)) { throw "COMSOL_COMPILE not found: $ComsolCompile" }
if (-not (Test-Path -LiteralPath $ComsolBatch)) { throw "COMSOL_BATCH not found: $ComsolBatch" }

$JavaFile = Join-Path $ScriptsDir "ComsolCube10mm.java"
$ClassFile = Join-Path $ScriptsDir "ComsolCube10mm.class"
$CompileLog = Join-Path $LogsDir "comsol_compile.log"
$BatchLog = Join-Path $LogsDir "comsol_batch.log"

Push-Location $ScriptsDir
try {
  & $ComsolCompile $JavaFile *> $CompileLog
  if (-not (Test-Path -LiteralPath $ClassFile)) { throw "Compiled class not found: $ClassFile" }
  & $ComsolBatch -inputfile $ClassFile -outputfile (Join-Path $ExampleRoot $OutputFile) *> $BatchLog
}
finally {
  Pop-Location
}

Write-Host "COMSOL cube smoke output: $(Join-Path $ExampleRoot $OutputFile)"
