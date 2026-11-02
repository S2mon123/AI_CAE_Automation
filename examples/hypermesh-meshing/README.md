# HyperMesh Meshing Example Skeleton

This layout validates CAD import, mesh creation, quality checks, and solver-deck
export through explicit Tcl and `hmbatch -tcl`.

```text
inputs/
  geometry-placeholder.txt
scripts/
  import_mesh_export.tcl
runs/<timestamp>/
  logs/hypermesh_hmbatch.log
  outputs/model.hm
  outputs/model.fem
  exports/mesh-summary.json
  exports/quality.csv
  report.md
```

Do not include proprietary CAD in the public example. Import return codes,
nonzero entity/element counts, quality failures, and nonempty deck export are
independent gates.
