# COMSOL 10 mm Cube Smoke Test

This example is the first solver-native smoke test for the COMSOL bridge. It
creates a real 10 mm cube with the COMSOL Java API, assigns a simple material,
generates a mesh, and saves an `.mph` model.

It is intentionally small. Passing this test only proves that the local COMSOL
Java/batch chain can create geometry and write a model file; it is not an
engineering validation case.

## Required Local Tools

Set these variables or pass explicit paths to the MCP tools:

- `COMSOL_ROOT`: COMSOL installation root that contains `Multiphysics/`.
- `COMSOL_COMPILE`: path to `comsolcompile.exe`.
- `COMSOL_BATCH`: path to `comsolbatch.exe` or the COMSOL command that supports batch input.

## Run Through MCP

```text
create_run_record(solver="comsol", case_name="comsol-cube-10mm")
comsol_write_cube_smoke_java(target_path="runs/<run>/scripts/ComsolCube10mm.java")
comsol_run_java_model_to_mph_file(
  java_file="runs/<run>/scripts/ComsolCube10mm.java",
  run_dir="runs/<run>",
  output_file="runs/<run>/outputs/comsol_cube_10mm.mph"
)
comsol_validate_mph_loadable_file(
  mph_file="runs/<run>/outputs/comsol_cube_10mm.mph",
  run_dir="runs/<run>",
  validated_copy="runs/<run>/outputs/comsol_cube_10mm.validated.mph"
)
scan_run_evidence(run_dir="runs/<run>")
generate_run_report(run_dir="runs/<run>")
```

## Run Manually

From this folder:

```powershell
.\scripts\run_comsol_cube_smoke.ps1
```

Expected generated files are ignored by git:

- `outputs/comsol_cube_10mm.mph`
- `logs/comsol_compile.log`
- `logs/comsol_batch.log`

If the run fails, inspect the log parser result from `scan_run_evidence`. License
checkout failures should be reported as `license_error`, not as successful runs.


## Expected Evidence Shape

`expected/evidence-example.json` shows the kind of evidence summary expected from
a successful local smoke run. It is not a bundled solver result; real users must
generate their own `runs/<run>/evidence.json` with `scan_run_evidence`.
