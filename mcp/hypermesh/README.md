# HyperMesh MCP Profile

This local `stdio` profile discovers `hmbatch.exe`, runs explicit user-supplied
Tcl through `hmbatch -tcl`, and exposes evidence-first HyperMesh guidance. It
does not assume an undocumented Python API or report a successful mesh from a
zero process return code alone.

The profile organizes meshing as a decision process:

1. select shell/quad, mapped/swept hex, or tet/boundary-surface route;
2. protect physics-driving features and remove only justified detail;
3. design patch/block topology and mesh dependencies before cutting geometry;
4. create local hole, curvature, fillet, bias, and size-transition controls;
5. mesh difficult sources/terminal regions before dependent regions;
6. diagnose quality failures by geometry, partition, connectivity, node
   position, or criteria cause, then apply the least destructive remedy.

## Run

From the repository root:

```powershell
python -m pip install -e ".[mcp]"
python mcp\hypermesh\server.py
```

To install the profile entry command as well, install the root project first so
the declared shared-core dependency is satisfied:

```powershell
python -m pip install -e ".[mcp]"
python -m pip install -e "mcp\hypermesh"
ai-cae-hypermesh-mcp
```

Codex registration is shown in
[`examples/codex-config.example.toml`](examples/codex-config.example.toml).
Machine-specific paths belong in ignored local configuration or environment
variables; do not commit them.

## MCP Coverage

| Area | Implementation |
| --- | --- |
| Base protocol, lifecycle, capability negotiation, cancellation messages | Official MCP Python SDK |
| Tools | Installation check, workspace validation, partition/transition/circular/fillet-chamfer/sphere/flange planning, Tcl execution, run/evidence/report tools |
| Resources | Workflow, partition strategy, feature meshing, fillet/chamfer decisions, sphere/flange patterns, quality remediation/gates, server manifest |
| Prompts | `hypermesh_meshing_plan` |
| Structured outputs | Typed dictionary outputs from profile tools |
| Logging and progress | Start/end logs and progress on `hypermesh_run_tcl_file` when the client supports them |
| Roots | Optional compatibility query through `hypermesh_list_client_roots` |
| Transport | Explicit local `stdio` |
| Authentication | Intentionally absent for local `stdio`; required before any remote HTTP deployment |
| Sampling, elicitation, tasks | Not required by this deterministic local bridge |

MCP components are modular, not a checklist in which every server must implement
every capability. In particular, roots are exposed by a supporting **client** and
queried by the server. They are informational, not a filesystem sandbox, and are
deprecated in the 2026 protocol revision. This profile keeps a compatibility
tool for current 1.x clients but uses explicit configuration for path policy:

```powershell
$env:AI_CAE_HYPERMESH_WORKSPACE_ROOTS = "<workspace-root-a>;<workspace-root-b>"
```

Alternatively, pass `workspace_root` to the validation or execution tool. If a
boundary is configured, both the Tcl input and run directory must resolve inside
it. Symlink/junction-resolved paths are checked with `Path.resolve`.

## Profile Primitives

### Tools

- `hypermesh_mcp_manifest`: report primitives, SDK responsibilities, and path policy.
- `hypermesh_check_installation`: resolve `hmbatch` without launching HyperMesh.
- `hypermesh_validate_workspace_paths`: validate Tcl/run paths before execution.
- `hypermesh_plan_partition_strategy`: create route-specific patch/block logic,
  dependency order, risks, and acceptance checks for quad shell, mapped hex, or
  tetra meshing.
- `hypermesh_plan_size_transition`: derive transition-layer count, actual growth,
  and minimum transition-band length from fine/coarse sizes.
- `hypermesh_plan_circular_feature_mesh`: calculate auditable circumferential,
  curvature-angle, axial, and washer/radial division baselines.
- `hypermesh_plan_fillet_chamfer_mesh`: classify a measured fillet, round,
  chamfer, or bevel by analysis role; derive profile rows, chord length,
  chordal deviation, minimum-size conflicts, transition layers, and shell/hex/
  tet topology rules without automatically deleting geometry.
- `hypermesh_plan_tetra_quality_remediation`: combine exact worst values,
  failure-set overlap, geometry/criteria feasibility, and optimizer history into
  a surface-first tetra remediation and acceptance plan.
- `hypermesh_plan_sphere_mesh`: calculate great-circle/quarter-arc counts,
  non-collapsing core and outer radial blocks, through-thickness layers,
  construction planes/curves, risks, and acceptance checks for spheres and
  spherical shells.
- `hypermesh_plan_flange_mesh`: calculate bolt pitch, PCD counts, adjacent-hole
  chord/ligament, bore/rim clearances, construction rings/radial lines, washer
  conflicts, and axial layers for flange and hub partitions.
- `hypermesh_list_client_roots`: query roots only when the client declares the
  legacy capability; never treat the result as authorization.
- `hypermesh_run_tcl_file`: run explicit Tcl, capture the process log, and attach
  workspace-policy results. Import/entity/quality/export evidence is still
  required after process completion.

The shared profile also exposes run creation, context scoping, toolchain
discovery, bridge planning, smoke templates, evidence scanning, and report
generation.

### Resources and Prompt

- `hypermesh://guidance/workflow`
- `hypermesh://guidance/quality-gates`
- `hypermesh://guidance/partition-strategy`
- `hypermesh://guidance/feature-meshing`
- `hypermesh://guidance/fillet-chamfer-meshing`
- `hypermesh://guidance/shape-partition-patterns`
- `hypermesh://guidance/quality-remediation`
- `hypermesh://guidance/tetra-quality-optimization`
- `hypermesh://server/manifest`
- prompt `hypermesh_meshing_plan`

The guidance covers four-sided 2D patches, transition bands, source/target/path
block contracts, one- and three-direction mappability, terminal-block
backtracking, direction-change connector blocks, symmetry sectors, circular
edges, through/blind/slotted holes, radial/corner-quad washers, fillet rows,
curvature controls, intersections, biased seeding, and cause-driven QI repair.
Planning tools generate baselines and audit data; engineering acceptance still
depends on solver profile, element formulation/order, physics, and measured
quality results.

### Spheres and spherical shells

- Measure the center, three local axes, outer/inner radii, thickness, openings,
  symmetry, contacts, loads, and supports before constructing partition curves.
- Use three orthogonal center planes to verify a valid one-eighth sector, but do
  not assume analysis symmetry if loading, contact, or material breaks it.
- Avoid latitude/longitude pole collapse. For an all-quad shell, prefer six
  cube-projected four-sided patches; for an all-hex solid, use a finite
  cube-like core and six curved outer blocks instead of sweeping to one center
  node.
- Match great-circle, quarter-arc, core-interface, and replicated-seam counts;
  check quality at poles, extraordinary nodes, core transitions, and seams.

### Flanges and hubbed plates

- Measure the center/axis, outer and bore radii, hub/step radii, PCD, hole size,
  count and phase, flange/hub thickness, fillets, gasket/contact bands, loads,
  and constraints.
- Build only needed concentric rings at bore, hub/step, washer/contact,
  transition, and rim limits. Add radial lines through hole centers and
  mid-pitch planes, then connect hole quadrants to their washer/transition ring.
- Check adjacent-hole chord ligament and inner/outer radial clearance before
  choosing size. Mesh hole/washer sectors first and isolate variable-thickness
  hub/neck blocks before an axial Solid Map sweep.
- Use a one-pitch cyclic model only when geometry, material, contact, bolt
  pretension, loads, and constraints are all periodic.

### Fillets, rounds, chamfers, and bevels

- Inventory stable feature IDs, analysis role, radius or planar profile width,
  included angle, tangency/end edges, adjacent geometry, target/minimum size,
  chordal deviation, and intended mesh route before cleanup.
- Preserve features that drive fatigue/stress, contact, sealing, load transfer,
  boundaries, materials, thickness changes, or mapped-block topology. Treat a
  cosmetic feature as a suppression candidate only after representability and
  retained-versus-simplified sensitivity review.
- For a retained fillet, derive rows from arc length, maximum turn angle, and
  maximum chordal deviation; use a longitudinal centerline split only when it
  improves flow without creating short end edges. For a retained chamfer,
  treat it as a planar band with explicit rows and matched long-edge counts.
- Isolate shoulder/fillet/chamfer transitions before mapped-hex sweeps. For
  tetra meshing, prefer curvature/proximity controls over excessive cuts.
- After defeaturing, verify protected loads/contacts/interfaces, topology,
  minimum feature size, area/volume change, and all active mesh metrics.

## Partition Logic

### 2D shells and midsurfaces

- Split geometry into controlled feature, transition, and regular far-field
  patches rather than sending every trim edge directly to `automesh`.
- Prefer four-sided/map-friendly patches with compatible opposite/shared edge
  counts. Suppress meaningless lines; preserve material, thickness, contact,
  load, and constraint boundaries.
- Create washer/O-grid topology before meshing surrounding regions. Place
  unavoidable singularities or allowed trias away from critical features.
- Use explicit transition bands and growth limits; do not expect smoothing to
  repair an abrupt fine-to-coarse topology.

### Mapped/swept solids

- Treat partitioning as decomposition into basic sweepable blocks, not as
  arbitrary geometric slicing.
- Record each block's source, target, path/along faces, sweep direction, shared
  faces, divisions, and predecessor/dependent blocks.
- Exploit symmetry, backtrack from terminal blocks toward the core, then mesh in
  reverse dependency order. Use a small three-direction mappable block where
  sweep directions change.
- Split curved sectors only when their forced sweep role causes distortion. The
  commonly taught 90-degree bisection is a heuristic that must pass Jacobian,
  warpage, and aspect checks.
- Do not assume all individually mappable blocks can be meshed together; shared
  face constraints can conflict.

### Quality remediation

Repair topology and geometry before local remesh, connectivity edits, and node
smoothing. Use split/swap/combine for a diagnosed local pattern, and constrain
smoothing with feature/interface anchor nodes. Re-run every active metric after
each repair so improvement in QI does not hide a new solver-specific failure.

## Acceptance Gates

Treat these as independent gates:

1. CAD reader/import status and nonzero expected surfaces/solids.
2. Chosen mesh route and retained/suppressed feature inventory.
3. Patch/block plan with purposeful cuts, source-target-path topology, shared
   faces, dependencies, and no residual slivers or unmappable blocks.
4. Nonzero nodes/elements with recorded types, local controls, and actual
   feature/transition creation counts.
5. Named solver-specific quality thresholds, individual failed counts/worst
   values, diagnosed causes, and localized before/after remediation evidence.
6. Nonempty `.hm` and downstream solver-deck exports.
7. Preserved Tcl, command line, hmbatch/BatchMesher logs, summaries, and report.

## Research Basis

Community workflows were synthesized rather than copied from any single
tutorial. The main practical sources were:

- [Altair China HyperMesh basic training on Bilibili](https://www.bilibili.com/video/BV1Bp4y1v752/): geometry cleanup, Quick Edit, Automesh/QI, ruled/drag, Solid Map, multi-volume, and tetra workflows.
- [Altair China hexahedral partition logic on Bilibili](https://www.bilibili.com/video/BV1xh411f7Q1): mappability, block decomposition, and virtual partition reasoning.
- [2D graded-mesh workflow on Bilibili](https://www.bilibili.com/video/BV1Et4y1E7ct/) and [multi-scale circular/structured examples](https://www.bilibili.com/video/BV1pk4y1f7Ve/).
- [Bilibili sphere structured-mesh example](https://www.bilibili.com/video/BV1TB421r7t9/) and [Jishulink sphere example](https://www.jishulink.com/post/1818472): recurring sphere workflow and one-eighth symmetry pattern.
- [Bilibili HyperMesh study notes](https://www.bilibili.com/opus/1035259234909945926): constructing points/nodes and surface-projected lines before splitting geometry.
- [Bilibili double-fillet meshing example](https://www.bilibili.com/video/BV1HW4y1273B/): practical fillet-row and local contact-region workflow.
- [Jishulink BatchMesher fillet controls](https://www.jishulink.com/post/421562): radius/arc-width formulas, minimum rows, chordal deviation, centerline split, and enforced-row options.
- [Zhihu washer example](https://www.zhihu.com/tardis/bd/art/622454411): hole layers, scaling, connector/local-axis options, and minimum nodes around holes.
- [Baidu high-quality hex example](https://jingyan.baidu.com/article/454316ab04332ff7a6c03a7e.html): mappability inspection, solid splitting, source-face mesh, and staged Solid Map.
- [Baidu QI repair example](https://jingyan.baidu.com/article/90bc8fc8b053aef653640cce.html): failed-patch review and local split/cleanup workflow.

The rules were cross-checked against current Altair documentation for
[mesh-control precedence and feature controls](https://help.altair.com/hwdesktop/hwx/topics/pre_processing/meshing/mesh_controls_type_surface_meshing_r.htm),
[hole/washer and BatchMesher parameters](https://2025.help.altair.com/2025.1/hwdesktop/hwx/topics/pre_processing/meshing/meshing_parameter_settings_r.htm),
[Solid Map mappability](https://2021.help.altair.com/2021/hwdesktop/hwx/topics/pre_processing/meshing/meshing_solid_map_unity_c.htm),
[measurements and snap points](https://www.help.altair.com/2021/hwdesktop/hwx/topics/chapter_heads/measures_r.htm),
[hole/flange feature detection](https://help.altair.com/hwdesktop/hwx/topics/pre_processing/model_setup/features_r.htm),
[fillet centerline splitting](https://help.altair.com/hwdesktop/hwd/topics/reference/hm/_createfilletmidlines.htm),
[edge-fillet defeaturing](https://2022.help.altair.com/2022.3/hwdesktop/hwd/topics/reference/hm/_removeedgefillets.htm),
[curved-surface chordal controls](https://2022.help.altair.com/2022.2/hwdesktop/hm/topics/tutorials/hm/hm_3120_2d_mesh_in_curved_surfaces_c.htm),
[line, offset/washer, and graphical splits](https://2025.help.altair.com/2025/hwdesktop/hwx/topics/pre_processing/geometry/surface_split_line_t.htm),
[quality criteria](https://help.altair.com/hwdesktop/hwx/topics/pre_processing/meshing/batchmesher_settings_criteria_r.htm),
and [split/swap/combine repair](https://2025.help.altair.com/2025/hwdesktop/hwx/topics/pre_processing/meshing/element_split_t.htm).

UI paths and labels differ between Classic and newer ribbon releases. The MCP
therefore describes topology intent and validates evidence but does not invent
version-specific Tcl commands.

## Protocol Self-Check

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
python -m pytest mcp\hypermesh\tests -q
```

The tests build the server in-process and verify tools, resources, prompts,
partition/transition/feature calculations, workspace containment, and
Skill-backed resource loading without launching commercial software.
