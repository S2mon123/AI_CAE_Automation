# AEDT Wireless-Power Example Skeleton

This public layout demonstrates the evidence contract for a Maxwell wireless
power-transfer workflow. It does not include a private `.aedt` project or a
claimed solved result.

```text
inputs/
  parameters.example.json
scripts/
  build_and_solve.py
runs/<timestamp>/
  logs/
  outputs/project.aedt
  exports/matrix.csv
  exports/field.png
  report.md
```

Acceptance requires the actual Maxwell design/solution type, winding polarity,
matrix setup, positive self-inductances, bounded coupling, M12/M21 reciprocity,
native solver logs, and field/table exports. An HFSS-only bridge is not a
substitute for Maxwell.
