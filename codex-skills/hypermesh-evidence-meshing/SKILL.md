---
name: hypermesh-evidence-meshing
description: Plan, create, repair, and evidence-gate Altair HyperMesh surface and volume meshes with geometry cleanup, quad-flow source meshes, mapped or swept hexa block decomposition, feature controls, tetra fallback, quality remediation, Tcl or hmbatch execution, and solver-deck export. Use for HyperMesh meshing or automation tasks where nonzero entities, topology, solver-specific quality, and exports must be verified.
---

# HyperMesh Evidence Meshing

Use explicit Tcl through `hmbatch -tcl` as the reproducible baseline. Do not
assume an undocumented Python API and do not modify vendor installation files.

## Start

```powershell
ai-cae-toolbox context-scope --solver hypermesh
ai-cae-toolbox bridge-plan --solver hypermesh --objective "<objective>"
ai-cae-toolbox create-run --solver hypermesh --case <case-name> --objective "<objective>"
ai-cae-toolbox write-smoke-template --solver hypermesh --run-dir <run-dir>
```

Use `hypermesh_check_installation` and `hypermesh_run_tcl_file` when MCP is
available. Use `hypermesh_mcp_manifest` to inspect the profile primitives and
`hypermesh_validate_workspace_paths` before execution when a workspace root is
configured. Use `hypermesh_plan_partition_strategy`,
`hypermesh_plan_size_transition`, and
`hypermesh_plan_circular_feature_mesh`, `hypermesh_plan_fillet_chamfer_mesh`,
`hypermesh_plan_tetra_quality_remediation`,
`hypermesh_plan_tetra_hotspot_remediation`,
`hypermesh_plan_tetra_zero_failure_search`,
`hypermesh_plan_sphere_mesh`, and `hypermesh_plan_flange_mesh` before writing
geometry-cut or meshing Tcl.

## Choose the Meshing Route

- For shells or midsurfaces, design quad flow and local transitions before
  `automesh`; allow trias only where the solver and physics permit them.
- For hex-dominant solids, prove each planned block is sweep/mapping-compatible
  and define source, target, path, shared-face dependencies, and mesh order.
- For a pure-hex mapped block, require an all-quad, quality-checked source mesh.
  A source tria propagates as a penta/wedge rather than a hexahedron.
- For tet-dominant solids, clean and protect the boundary surface mesh first;
  do not over-partition merely to imitate a hex workflow.
- Prefer a simpler, verifiable topology over a fragile pure-hex target when
  decomposition cost or distorted transition blocks outweighs its benefit.

## Gate the Workflow

1. Copy source CAD into the run input area; never overwrite the original.
2. Confirm the CAD reader/import completed and count imported surfaces/solids.
3. Define solver-specific size and quality criteria, then audit free edges,
   duplicate/overlapping surfaces, intersections, normals, and topology.
4. Classify mesh-driving features and preserve intentional circular edges,
   holes, contacts, loads, constraints, interfaces, and symmetry boundaries.
5. Write a partition plan before cutting geometry. For each patch/block, record
   why it exists, source/target/path topology, shared interfaces, and dependent
   blocks. A large number of cuts is not evidence of a valid decomposition.
6. Apply cuts incrementally. Re-check topology and mappability after each group
   and reject sliver surfaces, short edges, acute wedges, and conflicting sweep
   directions introduced by the cut.
7. Define edge densities, local size, bias, washer rings, transition bands, and
   sweep layers before generating dependent surface or volume mesh.
8. Treat the source-face quad mesh as a release gate. Verify all-quad intent,
   ordered boundary counts, feature capture, flow, and 2D quality before any
   mapped volume operation. Mesh difficult terminal/source regions first, then
   propagate compatible shared-face meshes through dependent blocks.
9. Diagnose failed elements by cause and node-to-geometry association. Cluster
   failures, rank one hotspot at a time, and distinguish geometry-edge,
   boundary-surface, and interior failures. Prefer topology repair or local
   remesh before connectivity edits, and use node smoothing only when geometry
   and topology are already suitable. Do not treat an absolute minimum-height
   failure as an automatic request for a smaller local element size.
10. When ordinary hotspot repair reaches a plateau, invoke the zero-failure
    escalation route: checkpoint, test feature-aware shape-preserving morphing
    on one/two neighboring layers, then route residual minimum-height and
    interior-skew failures to separate local operations. Rank every candidate
    globally and roll back regressions.
11. Export `.hm`, solver deck, quality report, partition/feature summaries, and
    command/log evidence.

Read [references/quality-gates.md](references/quality-gates.md) before accepting
the mesh. A return code of zero without entities and quality statistics is not a
successful mesh.

Read [references/partition-strategy.md](references/partition-strategy.md) before
cutting 2D surfaces or decomposing a solid for mapped/swept hex meshing.

Read [references/mapped-hexa-workflow.md](references/mapped-hexa-workflow.md)
for the complete manual or automated hexa workflow: topology cleanup, closed-
surface-to-solid conversion, mappability diagnosis, source-target-path block
planning, version-neutral route selection, staged mapping, interface control,
failure diagnosis, and final evidence.

Read [references/quad-surface-flow.md](references/quad-surface-flow.md) before
creating a shell quad mesh or any source mesh that will be propagated into a
hex volume. Use its rectangle, triangle, disk, annulus, hole, O-grid, junction,
concave-corner, and size-transition patterns, then pass its source-face gate.

Read [references/feature-meshing.md](references/feature-meshing.md) whenever the
geometry includes cylinders, holes, circular/curved edges, slots, thin annuli,
sweepable solids, fillets, steps, intersections, contacts, interfaces, or
boundary-condition regions.

Read [references/fillet-chamfer-meshing.md](references/fillet-chamfer-meshing.md)
whenever the geometry contains interior fillets, exterior rounds, edge blends,
chamfers, or bevels. Measure the profile, classify its physics role, derive
curvature/row/transition controls, and verify protected boundaries and topology
before accepting either preservation or defeaturing.

Read [references/shape-partition-patterns.md](references/shape-partition-patterns.md)
for spheres, spherical shells, domes, flange plates, hubs, bolt circles, or any
revolved part that needs measured centers/axes, construction lines, concentric
rings, meridians, symmetry planes, a non-collapsing core, or periodic sectors.

Read [references/quality-remediation.md](references/quality-remediation.md) when
QI or solver checks fail. Record the selected feature IDs, patch/block IDs,
derived division counts, failed element sets, and before/after statistics; do
not rely on a global element size or a final screenshot alone.

Read [references/tetra-quality-optimization.md](references/tetra-quality-optimization.md)
for any tetra route or tetra-quality failure. Export exact values with
`hm_getelemcheckvalues`, localize overlapping failures, prove feature-to-gate
feasibility, quality-check the boundary-tria mesh first, and reject node-only
optimization when it plateaus or only renumbers failed elements.

For a localized tetra repair, checkpoint the accepted mesh and process one
hotspot as a transaction. Re-run every active metric globally after fixed-
topology, edge-swap, or boundary-remesh candidates. Commit only a Pareto-safe
candidate; otherwise reload the checkpoint. Recompute hotspot IDs after every
accepted topology-changing operation because remeshing can invalidate element
IDs and adjacency.

For a hard zero-failure deliverable, all active failure counts must be zero in
both the working model and an independently reloaded solver deck. Then audit
pure element type, exact worst-value margins, moved boundary nodes, maximum
displacement, and current/initial CAD associations. Numerical quality approval
does not automatically approve geometry adherence; define and report an
engineering displacement tolerance. Never force-project stale initial geometry
IDs unless the referenced current entity exists and a checkpointed trial passes
all quality and topology gates.

## Finish

Report source geometry type, import translator, entity counts, element counts,
element types, global and local size controls, edge densities and bias, feature
division counts, block dependency and meshing order, failed-quality counts,
remediation, and exported solver profile. Preserve failed BatchMesher logs
because they identify translator, criteria, parameter-file, or topology
problems. For a zero-failure run, also report the independent-reload result,
exact quality margins, maximum boundary displacement, the applicable geometry
tolerance, and association changes.
