# Mapped and Swept Hexa Meshing Workflow

Use this workflow when a solid should be meshed mainly or entirely with
hexahedra. It applies to the current ribbon interface and the classic HyperMesh
panels: names and click paths change, but topology, source-target correspondence,
edge-count compatibility, and evidence do not.

## Contents

- Governing model
- Inputs and deliverables
- Translate classic and current UI concepts
- Clean and close the geometry
- Prove a block decomposition
- Select the volume route
- Gate the source-face mesh
- Build and execute the block dependency graph
- Common decomposition patterns
- Diagnose volume-mesh failures
- Verify and report
- Learning basis

## Governing Model

Think of mapped hexa meshing as controlled propagation of a 2D mesh:

1. decompose the solid into topologically simple blocks;
2. create or reuse a qualified source-face mesh;
3. establish a one-to-one boundary-loop relation to a target face;
4. propagate the source connectivity along a path or sweep direction;
5. preserve the propagated mesh on shared faces for dependent blocks.

The source-face topology becomes the volume topology. A source quad produces a
hexahedron through a regular sweep; a source tria produces a penta/wedge. Thus
"pure hex" is already violated if an unapproved tria remains on a source face.

Mappability is a topology-eligibility signal, not a quality certificate. A
mappable block can still create twisted, collapsed, high-aspect, or poor-
Jacobian elements when the source mesh, sweep path, or layer distribution is
bad.

## Inputs and Deliverables

Before modifying geometry, record:

- solver profile, unit system, analysis type, and element order;
- target/minimum/maximum size and every active 2D/3D quality criterion;
- geometry type: surfaces only, closed surface shell, or native solid;
- entity representation: native CAD geometry versus FE geometry and whether the
  installed release supports the intended volume-meshing operation on it;
- protected material, property, contact, load, constraint, symmetry, and
  connector boundaries;
- intentional holes, fillets, chamfers, washers, circular edges, and interfaces;
- pure-hex requirement versus permitted penta, pyramid, or tetra transitions.

The deliverables are not only a displayed mesh. Produce a block plan, patch and
edge-count table, topology audit, source-face quality report, volume-quality
report, entity/type counts, `.hm` model, solver deck, and execution log.

## Translate Classic and Current UI Concepts

Use intent rather than screen coordinates. Labels vary by release and profile:

| Engineering intent | Classic training vocabulary | Current workflow vocabulary |
| --- | --- | --- |
| repair/stitch/suppress topology | Quick Edit, edges, toggle/suppress | Topology/Geometry repair and edge edit |
| split a surface or solid | surface edit, solid edit, trim with plane/surface/lines | unified Split tools with entity and cutter selectors |
| build source quads | 2D Automesh panel | 2D mesh/Automesh context with interactive edge densities |
| map a block | 3D Solid Map, one volume/multi solids | Map tool with source, target, along faces, or mappability contexts |
| straight/curved/revolved sweep | linear solid, drag, line drag, spin | corresponding sweep/drag/map methods in the 3D ribbon |
| inspect quality | quality index/check elems panels | Evaluate/Quality tools and solver-specific criteria |

Before automation, query or inspect the installed version and solver profile.
Do not encode a tutorial's mouse location, translated label, or panel sequence
as if it were a stable API.

Do not confuse an entity-representation limitation with bad block topology. For
example, current Altair documentation lists Solid Map/hexa meshing among the
operations not supported on FE geometry. If the model is FE geometry, preserve
the source, then use a supported conversion/import path or select a different
meshing route for that release.

## Clean and Close the Geometry

### Interpret topology before meshing

In the standard HyperMesh topology display:

- **red** is a free edge owned by one surface;
- **green** is a shared edge owned by two surfaces;
- **yellow** is a non-manifold edge owned by three or more surfaces;
- **blue dashed** is a suppressed edge that the automesher ignores.

Use colors as diagnostics, not decoration. A red edge is valid on an intentional
shell boundary but blocks conversion of a supposed closed skin into a solid.
Yellow often indicates an overlap, duplicate surface, internal sheet, or
unintended branch. A blue suppressed edge is safe only when the boundary is not
needed for feature capture, loads, contacts, material regions, or mesh control.

### Cleanup sequence

1. Work on a copy and isolate one component or local region.
2. Find free edges, non-manifold edges, duplicate/overlapping surfaces, gaps,
   intersections, slivers, short edges, and inconsistent normals.
3. Delete only the proven duplicate or redundant sheet. Stitch intended surface
   pairs within a measured tolerance.
4. Suppress a shared edge only when the two adjacent surfaces should behave as
   one meshing patch. Suppression removes edge seeding and lets the mesh cross
   the boundary.
5. Choose cleanup tolerance from measured gap and feature sizes. If the
   tolerance is below the defect, the repair will not act; if it is too large,
   it can merge a real feature.
6. Recount topology after every repair. Confirm that each changed red/yellow
   edge became the intended shared or suppressed state.
7. Convert enclosed bounding surfaces to a solid only after the skin is closed.
   Prove success by solid count and topology, not by transparency or color
   alone.

Do not suppress a geometry boundary merely because it prevents mappability.
First decide whether it represents physics or geometry that must survive.

## Prove a Block Decomposition

### Block contract

For each proposed block, record:

| Field | Required decision |
| --- | --- |
| Purpose | feature capture, direction change, transition, interface, or terminal block |
| Source | face or existing 2D mesh to propagate |
| Target | corresponding face and ordered boundary loop |
| Path | vector, line/curve, rotation axis, or along faces |
| Mappability | expected one-direction or three-direction status |
| Counts | ordered source edges, target edges, sweep layers, bias |
| Interfaces | shared faces and whether they already carry mesh |
| Dependencies | predecessor blocks whose interface mesh is fixed |
| Risk | sliver, short edge, twist, concavity, branch, or size jump |

Source and target need compatible topology and ordered edge counts. Similar
shape by eye is insufficient: corners, holes, loops, and singularities must
correspond.

### Decomposition procedure

1. Identify natural sweep directions and constant-section regions.
2. Protect holes, bosses, contacts, loads, and material boundaries.
3. Split the easy base, arm, boss, annular, or branch regions into simple
   blocks. Use existing faces or planes for complete cuts; use curves or edges
   only when their extension creates the intended section.
4. Where direction changes, insert a compact connector block that can accept
   more than one source-target choice.
5. At branches, isolate terminal branches before resolving the central
   junction. Never sweep several branches independently into an undefined core.
6. Preview the cut. Reject new sliver faces, acute wedges, tiny residual blocks,
   or a final remainder with no compatible source and target.
7. Apply cuts in small groups; recount solids/shared faces and refresh
   mappability after each group.
8. If a cutter behaves unpredictably, do not accumulate repairs blindly. Undo
   or merge the bad cut and use a plane, surface, or alternate extension rule
   that represents the same planned section.

HyperMesh mappability colors commonly distinguish unassessed, unmappable,
one-direction-mappable, and three-direction-mappable solids. Treat a color
change after suppression or partitioning as feedback on the topology model;
still prove the actual source/target/path and quality.

## Select the Volume Route

Choose the simplest route that expresses the geometry truthfully.

| Route | Use when | Main controls | Main failure mode |
| --- | --- | --- | --- |
| Map / Solid Map | source and target loops correspond through a block | source mesh, target, along faces, layers, bias | incompatible loops or distorted propagation |
| Linear solid / drag | cross-section is constant along a straight vector | source elements, vector, distance, layers | wrong vector, premature intersection, bad layer size |
| Line drag | section follows a curve | source, guide line, orientation, layers | section twist or compression on tight curvature |
| Spin | revolved sector about an axis | source, axis, angle, circumferential count | collapsed cells at axis or periodic count mismatch |
| Offset | surface layers follow changing local normals | source surface elements, signed offset, layers | self-intersection, inverted layers, or confusing a shell layer with a solid core |
| Staged map | adjacent blocks share constrained interfaces | dependency order and retained interface mesh | remeshing an interface or conflicting source choices |
| Hybrid/tet fallback | credible blocks cannot be formed without harmful cuts | transition contract and solver support | undocumented nonconformity or unsupported element mix |

The current Map tool and older Solid Map/drag/spin panels expose these concepts
differently. Discover the installed controls and record the chosen route rather
than scripting a guessed panel path.

## Gate the Source-Face Mesh

Read [quad-surface-flow.md](quad-surface-flow.md) and do not generate volume
elements until the source mesh passes all of these checks:

- source face is the intended propagation face and its normals/orientation are
  understood;
- all elements are quads for a pure-hex requirement;
- boundary nodes lie on protected geometry and required feature points;
- ordered edge densities match the target loop and dependent shared faces;
- circular features have explicit circumferential and radial counts;
- transition bands exist in topology instead of being delegated to smoothing;
- size, aspect, skew, warpage, Jacobian/shape, and angle checks pass under the
  active solver profile;
- no duplicate elements, disconnected nodes, unintended free edges, or
  unresolved equivalence exist;
- the mesh flow is credible under propagation and contains no abrupt turn or
  singularity in a high-gradient/contact region.

If an existing source-face mesh fixes an interface, its node count is no longer
a free parameter for the next block. Black/locked densities or noneditable
counts in the UI are a dependency signal: change the upstream mesh or accept
the inherited count.

## Build and Execute the Block Dependency Graph

Represent blocks as a directed graph. An arrow `A -> B` means B consumes a
shared-face mesh produced by A.

1. Start with the most constrained feature source: a hole/washer, circular
   sector, contact face, or difficult curved end.
2. Mesh and quality-check that source patch.
3. Map or sweep its block; retain the shared target/interface mesh.
4. Use that interface as the next source and propagate outward through simpler
   blocks.
5. Mesh terminal/connector blocks only when all incoming interface counts are
   compatible.
6. After each block, check element type, shared-face conformity, duplicate
   nodes/elements, orientation, and every active metric. Checkpoint accepted
   stages.
7. Do not regenerate an accepted upstream face during a downstream retry unless
   the transaction explicitly rolls back the dependent blocks.

When using symmetry, mesh and checkpoint the smallest valid half/sector first.
Copy before reflecting so the accepted source is retained, select the symmetry
plane from verified points/axis, then equivalence the reflected interface only
within a justified tolerance. Recheck duplicate nodes/elements, free edges,
non-manifold/T-edges, element orientation, and quality. When extracting boundary
faces for topology checks, isolate the extracted skin; displaying the volume
mesh or a second skin at the same time can create duplicate faces and false
non-manifold results.

Even if every solid is colored mappable, a single multi-solid map may fail
because neighboring blocks demand inconsistent meshes on the same face.
Staged mapping is therefore an execution strategy, not a workaround of last
resort.

## Common Decomposition Patterns

### Plate, arm, and cylindrical boss

1. Separate plate thickness, arm/web, and boss into blocks.
2. Quarter the boss/annulus and connect its principal directions into the arm.
3. Build an all-quad source mesh on the plate or boss face.
4. Map the plate thickness first if it provides the arm interface; otherwise
   mesh the circular terminal first and propagate back toward the plate.
5. Add a connector block where the arm meets the boss so the circular and
   rectangular flows do not collide in one residual volume.

### Annular body with tangential branch or fork

1. Partition the annulus into sectors with explicit circumferential counts.
2. Isolate each prong/branch as a sweepable terminal block.
3. Place the circular-to-rectangular transition before the junction.
4. Map neighboring sectors in dependency order and keep the shared mesh.
5. Resolve the compact junction last; reject a plan that leaves a many-sided
   residual core.

### Bent or changing-section bracket

1. Split at section changes and major curvature-direction changes.
2. Use straight drag only for truly constant straight sections.
3. For curved paths, control line-drag orientation or divide the bend into
   smaller sectors to limit twist.
4. Insert a three-direction connector where sweep direction turns.
5. Propagate from constrained ends toward the connector and check Jacobian after
   each bend block.

### Revolved body or sphere sector

Use a noncollapsing core, meridional/sector partitions, and compatible periodic
counts. Never collapse an entire quad row onto the axis or a pole. See
[shape-partition-patterns.md](shape-partition-patterns.md).

## Diagnose Volume-Mesh Failures

| Symptom | Probable cause | Preferred action |
| --- | --- | --- |
| solid remains unmappable | extra face/edge, hole mismatch, branch, concavity, or wrong block topology | inspect boundary loops; suppress only irrelevant edges or repartition |
| map cannot identify source/target | open shell, noncorresponding loops, or wrong selection | repair closure and explicitly record ordered loops |
| unexpected pentas/wedges | trias on source or transition face | repair source to approved all-quad flow or document permitted pentas |
| gap or duplicate layer at shared face | blocks meshed independently or nodes not shared | retain one interface mesh; equivalence only with justified tolerance |
| negative/poor Jacobian near target | twisted path, bad source quad, target compression | revise source flow, path orientation, layer bias, or block split |
| high aspect through thickness | too few/many layers relative to source size | derive thickness layers from size/aspect limits and use controlled bias |
| locked density cannot be changed | upstream/shared mesh already fixes the count | revise dependency predecessor, not the downstream face alone |
| local smoothing has little effect | geometry/partition/connectivity cause remains | move up the repair hierarchy and remesh the block |
| UI mappability seems stale | display/update issue or incomplete topology refresh | reselect/isolate, refresh topology, then verify with an actual trial and counts |

## Verify and Report

At final acceptance, report:

- imported and final surface/solid counts plus topology states;
- block table, source/target/path, dependency graph, and mesh order;
- edge densities, bias laws, sweep layers, and local size controls;
- source-face element counts/types and quality before volume generation;
- final node/element counts by type; explicitly prove pure hex when required;
- free/non-manifold edges, duplicates, equivalence result, and shared-face
  conformity;
- failed count, percentage, worst value, and location for every active 3D
  quality metric;
- checkpoints, rejected trials, remediation, exceptions, and solver profile;
- independently reloaded deck counts and quality for high-assurance work.

Do not adopt a tutorial's numeric Jacobian or quality threshold as a universal
rule. HyperMesh quality calculations and acceptable limits depend on solver,
element type/order, formulation, and project criteria.

Use Quality Index for the supported 2D surface review. For the volume release
gate, run the named 3D checks directly; do not report a surface QI as evidence
that the mapped hexahedra pass Jacobian, aspect, or other solid criteria.

## Learning Basis

This workflow synthesizes the following demonstrations and uses official Altair
documentation to resolve UI terminology and generalize beyond one model:

- [New-interface bracket case](https://www.bilibili.com/video/BV1pRjE6KE49/):
  topology cleanup and closure at 00:00-06:00; hexa logic and block partitioning
  at 06:00-22:00; source quads, staged mapping, inherited counts, and final
  checks at 22:00-34:43.
- [HyperMesh 2025 3D meshing course, P5](https://www.bilibili.com/video/BV1HHZDBWEGa?p=5):
  hexa chapter begins near 1:01:17; source-target-guide and path interference at
  1:07:19-1:15:32; symmetry, direction-aware partitioning, and coupled block
  counts at 1:16:14-1:24:44; mirror/equivalence/face checks at
  1:24:48-1:28:43; manual multi-stage Extrude and association repair at
  1:28:45-1:48:58; local-normal Offset at 1:50:01-1:51:53.
- [Classic-interface 3D case](https://www.bilibili.com/video/BV1MA4y1f7rU/):
  symmetry and half-model strategy at 01:43-03:39; complete cutting at
  09:19-17:27; interface source quads and count-driven repartition at
  17:27-24:54; staged Solid Map at 25:00-31:51; mirror/equivalence and
  free/non-manifold edge diagnosis at 35:47-46:49.
- [Planar quad-mesh cases](https://www.bilibili.com/video/BV1cm421E77m/):
  source-mesh partition and density patterns for rectangles, triangles, disks,
  holes, circle-to-square transitions, and local repair.
- [Altair surface topology](https://2025.help.altair.com/2025/hwdesktop/hwx/topics/pre_processing/entities/surfaces_r.htm),
  [Map meshing](https://2025.help.altair.com/2025.1/hwdesktop/hwx/topics/pre_processing/meshing/meshing_solid_map_unity_c.htm),
  [surface stitching](https://2025.help.altair.com/2025/hwdesktop/hwx/topics/pre_processing/geometry/surface_stitch_t.htm),
  [solid splitting](https://2025.help.altair.com/2025/hwdesktop/hwx/topics/pre_processing/geometry/surface_split_plane_t.htm),
  and [FE geometry limitations](https://2025.help.altair.com/2025/hwdesktop/hwx/topics/chapter_heads/fegeometry_r.htm).

Video timestamps are navigational evidence, not verbatim transcripts. When a
demo's UI label conflicts with the installed release, preserve the documented
topology intent and verify the current control in official help.
