# LAMMPS And OVITO Tension Example Skeleton

This example is intentionally potential-free. The smoke input uses
`pair_style zero` to validate parsing and execution only.

```text
scripts/
  in.smoke
  ovito_pipeline.py
runs/<timestamp>/
  logs/lammps_run.log
  outputs/final.data
  outputs/trajectory.lammpstrj
  exports/thermo.csv
  exports/stress_strain.csv
  exports/render.png
  report.md
```

A real material workflow must provide a licensed potential, provenance,
equilibration, loading rate, stress convention, size/rate/seed checks, and
separate LAMMPS and OVITO evidence.
