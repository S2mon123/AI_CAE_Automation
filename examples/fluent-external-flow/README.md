# Fluent External Flow Example Skeleton

This folder is a public project layout for an external-flow CFD validation case.

## Suggested Layout

```text
input/
  geometry.step
scripts/
  mesh.py
  solve.py
  postprocess.py
runs/
  <timestamp>/
    transcript.log
    residuals.csv
    forces.csv
    images/
    report.md
```

## First Validation Target

- geometry axis audit,
- coarse mesh,
- short steady solve,
- residual history,
- Cl/Cd monitor,
- pressure and velocity images.
