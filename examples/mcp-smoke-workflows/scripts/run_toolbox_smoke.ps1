param(
  [string]$Solver = "comsol",
  [string]$Case = "toolbox-smoke"
)

$ErrorActionPreference = "Stop"

python -m ai_cae_lab.toolbox env-check --json
python -m ai_cae_lab.toolbox list-adapters --json
python -m ai_cae_lab.toolbox bridge-plan --solver $Solver --objective "Local MCP bridge smoke"

$runJson = python -m ai_cae_lab.toolbox create-run --solver $Solver --case $Case --objective "Local MCP bridge smoke" --json | ConvertFrom-Json
python -m ai_cae_lab.toolbox write-smoke-template --solver $Solver --run-dir $runJson.run_dir --case $Case
python -m ai_cae_lab.toolbox scan-evidence $runJson.run_dir
python -m ai_cae_lab.toolbox generate-report $runJson.run_dir

Write-Host "Smoke workflow created:" $runJson.run_dir
