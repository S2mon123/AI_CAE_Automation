# COMSOL PM Motor NVH Workflow

This public-safe example describes how to start a checkpointed two-dimensional permanent-magnet motor NVH run. It does not include a proprietary/reference MPH model, compiled classes, solver logs, generated fields, or videos.

Use:

- [COMSOL motor NVH skill](../../codex-skills/comsol-motor-nvh-evidence/SKILL.md)
- [Chinese execution prompt](../../prompts/comsol-pm-motor-nvh.zh-CN.md)
- [Evidence checklist](../../checklists/comsol-pm-motor-nvh-evidence-chain.md)

## Create a run scaffold

```powershell
pwsh -File codex-skills/comsol-motor-nvh-evidence/scripts/New-ComsolMotorNvhRun.ps1 `
  -RunRoot runs `
  -CaseName pm-motor-nvh `
  -Objective "Build and validate a 2D PM motor NVH model" `
  -Mode SMOKE_MODE
```

Place project-specific Java API sources under the generated `scripts/` directory. Resolve COMSOL executables through environment variables or ignored private configuration.

## Recommended execution

```text
create_run_record(solver="comsol", case_name="pm-motor-nvh")
comsol_check_installation()
comsol_compile_java_file(java_file="runs/<run>/scripts/BuildPMMotorNVH.java", run_dir="runs/<run>")
comsol_run_compiled_java_class(class_file="runs/<run>/scripts/BuildPMMotorNVH.class", run_dir="runs/<run>")
comsol_run_batch_file(input_file="runs/<run>/models/01_built.mph", output_file="runs/<run>/models/02_modes_solved.mph", extra_args=["-study", "std1"])
```

Continue through electromagnetic, smoke, and full NVH checkpoints only after the preceding evidence gate passes. Exact Java features, selection names, and expressions must come from the current COMSOL version and the model contract, not from guessed API calls.

## Validate CSV exports

```powershell
python codex-skills/comsol-motor-nvh-evidence/scripts/validate_nvh_exports.py `
  --eigenfrequencies runs/<run>/exports/modes/eigenfrequencies.csv `
  --campbell runs/<run>/exports/campbell/campbell_long.csv `
  --pole-count 10 `
  --output runs/<run>/validation/nvh_export_validation.json
```

Passing the CSV validator proves table consistency only. Solver logs, loadable checkpoints, topology, physics, and mesh evidence are still required.
