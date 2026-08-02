# HyperMesh Quality Gates

- CAD import returns success and creates nonzero expected entities.
- No unresolved duplicate surfaces, intersections, or unintended free edges remain.
- The chosen shell/quad, hex/sweep, or tet route is justified against geometry,
  solver formulation, analysis physics, and decomposition cost.
- Every partition has a stated purpose and does not create unresolved sliver
  surfaces, short edges, acute wedges, or residual unmappable blocks.
- Mapped/swept blocks record source, target, path, shared-face dependencies,
  sweep direction, and verified mappability before volume meshing.
- Surface and volume element counts are nonzero.
- Element type and solver profile match the downstream analysis.
- Retained cylinders, holes, circular edges, contacts, interfaces, and
  load/constraint boundaries have explicit local controls rather than only a
  global size.
- Mating or shared edges use compatible division counts; intentional
  nonconformal interfaces name their coupling/contact method.
- Washer, radial, axial, and biased transition layers record counts, direction,
  minimum/maximum spacing, and growth ratio where applicable.
- Quality metrics use named criteria: aspect ratio, skew, Jacobian, warpage,
  minimum/maximum angle, tet collapse, or solver-specific checks.
- Failed element counts and percentages are exported, not hidden.
- Every metric also exports its exact worst value, element ID, centroid or
  location, and ranked worst set; a failure threshold is not a worst value.
- Tetra reports cross-correlate minimum-height, collapse, aspect, and volume-
  skew sets and distinguish severe failures from marginal misses.
- Individual solver-specific metrics remain available when an aggregate QI is
  reported; a better compound QI does not override a severe metric failure.
- Quality remediation records the diagnosed cause, operation, affected patch,
  and before/after counts and worst values.
- A tetra volume is not repaired until its closed boundary-tria mesh has passed
  topology and active 2D quality checks or its exceptions are documented.
- Any quality exception is localized and justified.
- Solver-deck export completes and the deck is nonempty.

Block downstream solve claims when logs contain translator failure, nonzero
`*geomimport` error code, BatchMesher nonzero return value, zero elements, or
unresolved severe quality failures.
