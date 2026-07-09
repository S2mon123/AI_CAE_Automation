# Inputs

These are small seed files for the public weld-pool example.

- `stageA_plate_ansys.msh`: structured Stage A plate mesh exported from the mesh
  generation script.
- `stageA_probe_volume_only.cas.h5`: small Fluent seed case used by the local
  validation run before material/model/UDF setup.
- `stageA_mesh_meta.json`: mesh dimensions, cell counts, coordinate definition,
  and physical group names.

Generated dense `.dat.h5` files are intentionally not tracked. Create them in a
local `runs/` folder.
