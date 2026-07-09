# Abaqus Drilling Example Skeleton

This folder is a public project layout for an Abaqus/Explicit drilling validation case.

It intentionally does not include private STEP files, `.odb` files, or commercial solver output.

## Suggested Layout

```text
input/
  tool.step
  workpiece.json
scripts/
  build_model.py
  postprocess_odb.py
runs/
  <timestamp>/
    logs/
    images/
    curves/
    report.md
```

## Key Outputs

- feed displacement,
- axial force,
- torque,
- element status,
- damage,
- plastic strain,
- energy balance,
- center-section image.
