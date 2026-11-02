# Ansys Mechanical Static Example Skeleton

Use a small cantilever or bracket to validate RunWB2/ExtAPI/PyMechanical before
attempting a private assembly.

```text
inputs/
  parameters.example.json
scripts/
  build_solve_export.wbjn
  pymechanical_controller.py
runs/<timestamp>/
  logs/solve.out
  outputs/model.wbpj
  outputs/file.rst
  exports/results.csv
  exports/deformation.png
  results-summary.json
  report.md
```

The result summary must satisfy all Mechanical acceptance gates. See
`results-summary.example.json` for the machine-readable contract.
