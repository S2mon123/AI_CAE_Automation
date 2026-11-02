# Quad Surface Flow and Source-Mesh Quality

Use this reference for shell quadrilateral meshing and for the 2D source mesh
of a mapped or swept hexa block. Good-looking quads are not enough: the mesh
must encode compatible counts, deliberate singularity placement, feature
capture, size transition, and solver-specific quality.

## Contents

- Source-mesh invariants
- Plan before Automesh
- Primitive topology patterns
- Edge density and transition design
- Interactive meshing loop
- Cause-driven quality improvement
- Source-face release gate
- Learning basis

## Source-Mesh Invariants

- A regular four-sided mapped patch requires compatible opposite edge counts.
- Adjacent conformal patches must use the same nodes and divisions on their
  shared edge.
- The total boundary-edge parity is a useful all-quad feasibility diagnostic,
  but it does not prove that a good quadrangulation exists.
- A triangle, disk center, branch, or abrupt count change introduces a topology
  singularity unless it is repartitioned into a finite quad layout.
- For pure mapped hex, every source element must be a quad. A source tria
  propagates to a penta/wedge.
- Smoothing improves node position; it cannot invent a missing transition band,
  remove a five-sided residual patch, or fix incompatible boundary counts.

Place unavoidable extraordinary nodes away from contacts, loads, sharp
gradients, tight curvature, and source regions that will be propagated through
many layers.

## Plan Before Automesh

1. Set solver profile, units, element order, target/min/max size, growth limit,
   and named quality criteria.
2. Measure the model. Avoid a target size that is wildly inconsistent with the
   geometric scale and could create an excessive element count.
3. Mark protected boundaries and mesh-driving points: corners, tangent points,
   hole quarter points, contact endpoints, symmetry lines, and thickness/size
   changes.
4. Clean duplicates, gaps, slivers, short edges, and unintended topology.
   Suppress only mesh-irrelevant shared edges.
5. Sketch principal mesh-flow directions and locate every planned singularity
   and fine-to-coarse transition.
6. Partition into simple patches, preferably four-sided, and create a table of
   ordered boundary counts before meshing.
7. Mesh the most constrained feature patch first and propagate its shared-edge
   counts outward.

For each patch, record `patch ID -> boundary loop -> ordered counts -> mesh
method -> flow direction -> neighbors -> protected nodes -> quality result`.

## Primitive Topology Patterns

### Rectangle or general four-sided patch

- Use a mapped/regular quad layout.
- Match opposite edge counts in pairs.
- Align rows with the dominant stress, flow, curvature, or extrusion direction
  when the solver/physics benefits.
- If the sides are strongly unequal, add a transition patch instead of forcing
  all size change into one row.

### Triangular region

A geometric triangle cannot be treated as a regular rectangular patch without
a singularity.

1. Add a centerline or interior point based on symmetry and feature intent.
2. Partition it into map-friendly subpatches with compatible counts.
3. Remove accidental hard points that create unmatched boundary segments.
4. Keep the singularity away from critical regions.
5. If solver rules permit a tria, compare a controlled mixed layout with the
   distortion caused by forcing pure quads. Pure-hex source faces cannot use
   that tria fallback.

### Disk

Do not run all radial rows into one center node. Use a finite square/diamond
core surrounded by transition patches:

1. create four principal points on the circumference;
2. construct a central four-sided core;
3. connect core corners/sides to the principal points;
4. assign compatible counts to each quadrant;
5. bias radially only when curvature or physics requires it;
6. place the core-to-ring singularities away from critical features.

### Annulus

- Divide both circles at corresponding angular locations.
- Use the same circumferential count on inner and outer arcs for a regular
  radial map.
- Choose radial rows from thickness, aspect, curvature, and any boundary-layer
  need; do not infer them only from circumference.
- Keep sector boundaries shared and identical when the annulus becomes a hexa
  source face.

### Plate with a circular hole: O-grid/washer

1. Preserve the hole and its four principal/tangent points.
2. Build a washer/O-grid around it instead of connecting the entire outer plate
   directly to the hole.
3. Split the outer plate so four principal flow paths leave the washer.
4. Set the around-hole count first; it controls curvature capture and often
   becomes an interface contract.
5. Allocate radial rows and then transition into rectangular far-field patches.
6. Move count transitions away from the hole, contact edge, or hotspot.

For an offset hole or a hole near an edge, allow asymmetric transition blocks.
Do not compress the short ligament into one severely distorted row merely to
retain visual symmetry.

### Circle-to-square or rounded-to-rectangular junction

Combine the disk/annulus and rectangle patterns:

- create an intermediate finite square or ring;
- quarter the circular boundary;
- connect circular principal points to corresponding rectangular directions;
- use explicit transition patches between circular and Cartesian flow;
- avoid a single many-sided patch that leaves Automesh to place singularities
  unpredictably.

### Concave corner or L-shaped region

- Extend the re-entrant corner directions to split the region into rectangles.
- Refine only as required by the corner physics and solver formulation.
- Use sufficient transition length so fine rows can grow outward gradually.
- Inspect skew and minimum angle at the concave corner; smoothing alone cannot
  cure a poor cut or a one-row transition.

### T, Y, or multi-branch junction

- Isolate branches into simple patches first.
- Design the compact junction as its own topology problem.
- Balance incoming row counts or add explicit transition bands.
- Place extraordinary nodes in the least critical branch or far-field region.
- For a future volume mesh, ensure each outgoing interface is a valid source or
  target loop for its block.

## Edge Density and Transition Design

Derive counts from geometry and criteria rather than accepting a single global
size:

1. calculate a first count from edge length and target size;
2. adjust circular counts for adequate angular resolution and sector symmetry;
3. enforce equal counts on opposite mapped sides and identical counts on shared
   conformal edges;
4. use integer-compatible counts across symmetric sectors and periodic faces;
5. allocate enough transition distance to respect the permitted growth ratio;
6. use bias to concentrate nodes near a feature without a sudden size jump;
7. recheck minimum length when adding density—more elements can worsen a
   short-edge or collapsed-transition failure.

When one boundary count changes, trace the consequence across every linked
opposite/shared edge and every downstream hexa block. A local count is often a
global dependency.

## Interactive Meshing Loop

Use Automesh or the current equivalent as an iterative preview, not a one-click
finalizer:

1. select one logical patch group and set element size/type/method;
2. display edge densities and locked/inherited counts;
3. set map style where the patch topology supports it;
4. correct opposite/shared counts and preview again;
5. inspect element flow, trias, singularities, feature nodes, and transitions;
6. reject the preview when an all-quad requirement is violated or bad flow is
   merely hidden by small elements;
7. accept the patch, then mesh the dependent neighbor using the retained shared
   edge;
8. run active quality checks before using the patch as a volume source.

If a line or hard point unexpectedly fixes a density or introduces a tria,
inspect whether it is a real topology boundary, an accidental point, or a
suppression/tolerance artifact. Repair that cause before manual node movement.

## Cause-Driven Quality Improvement

Apply the least destructive remedy that addresses the cause:

| Symptom | Likely cause | Preferred remedy |
| --- | --- | --- |
| unexpected tria | odd/incompatible counts, accidental point, many-sided patch | repair counts or repartition; do not hide it before a pure-hex map |
| skewed rows near a hole | no washer, too few sectors, abrupt radial transition | add/revise O-grid and densities |
| high aspect in a ligament | one compressed row or mismatched counts | repartition and add rows/transition length |
| poor warpage on curved surface | coarse curvature capture or bad geometry association | refine by curvature, split patch, and remesh |
| bad angle at concave corner | acute/sliver patch or wrong flow | revise partition; then local remesh |
| density will not change | shared/accepted neighbor locks the edge | edit upstream dependency or remesh both patches transactionally |
| smoothing does nothing | anchors/geometry constraints or topology cause | inspect constraints; move up to connectivity/partition repair |
| quality improves but feature drifts | unconstrained smoothing/move | restore checkpoint and anchor/project protected nodes |

Repair order:

1. geometry/topology cleanup;
2. patch partition and edge-density revision;
3. localized remesh/rebuild;
4. split, swap, or combine connectivity where permitted;
5. replace/move nodes with geometry association;
6. smooth last, with anchors and a stated objective such as size, shape, angle,
   or QI.

After every change, rerun all active metrics. HyperMesh's aggregate QI is useful
for ranking but must not hide an individual skew, Jacobian, warpage, aspect,
angle, or length failure. Metric definitions and thresholds are solver- and
element-specific.

## Source-Face Release Gate

Approve a quad mesh for hexa propagation only when evidence proves:

- intended topology/feature edges are preserved and irrelevant edges are
  intentionally suppressed;
- patch map method and principal flow directions are recorded;
- ordered boundary, circular, radial, and shared-edge counts are compatible;
- pure-hex source contains zero trias and no unintended duplicate elements;
- no unresolved free/disconnected edges or nonconformal shared nodes remain;
- individual solver-specific size, aspect, skew, warpage, Jacobian/shape, and
  angle checks pass;
- singularities and transitions lie outside protected critical regions;
- normals and geometry association are correct;
- accepted element/node counts and worst-quality locations are exported.

If any item fails, do not proceed to Map/Solid Map. A volume operation multiplies
source defects through the sweep and makes later repair more expensive.

## Learning Basis

The patterns were reconstructed from [the planar HyperMesh case set](https://www.bilibili.com/video/BV1cm421E77m/):

- 00:28-03:30 — rectangle, scale measurement, target size, and quad Automesh;
- 03:36-08:10 — triangular region partition, accidental point removal, and
  opposite-edge count correction;
- 08:25-12:30 — disk partition, interior-count control, parity/count changes,
  and elimination of an unintended tria;
- 12:42-16:45 — square plate with circular hole and four-way partition;
- 16:50-29:50 — combined circle/rectangle transition, finite interior square,
  topology cleanup, tolerance sensitivity, and iterative densities;
- 31:54-35:58 — local transition repair and density balancing;
- 36:05-41:16 — square-with-hole variant, opposite-count matching, refinement,
  and residual geometry/tolerance diagnosis.

The hexa consequence is reinforced by the source-face construction at
22:00-33:35 in [the new-interface mapped-hexa case](https://www.bilibili.com/video/BV1pRjE6KE49/).
Use [Altair Automesh parameters](https://help.altair.com/hwdesktop/hwd/topics/reference/hm/_automesh_params.htm),
[element smoothing](https://2025.help.altair.com/2025/hwdesktop/hwx/topics/pre_processing/meshing/element_smooth_t.htm),
and [quality calculation](https://2025.help.altair.com/2025.1/hwdesktop/hwx/topics/pre_processing/meshing/element_quality_how_its_calculated_c.htm)
to map these concepts to the installed release and active solver profile.
