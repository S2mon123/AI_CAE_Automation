# Tetra Quality Optimization

Use this reference for first- or second-order tetra meshes when minimum height,
tet collapse, aspect ratio, volumetric skew, or a solver-specific 3D criterion
fails. The workflow is surface-first and cause-driven: exact values and failed
patches are evidence; a smoother-looking mesh is not.

## 1. Audit Exact Values, Not Only Failure Counts

For every active metric export the threshold, direction, failed count, failed
rate, exact worst value, worst element ID, centroid, and a ranked worst-element
list. HyperMesh documents `hm_getelemcheckvalues mark_id 3 check_type` for this
purpose. Useful 3D `check_type` values include `minlength`, `tetracollapse`,
`aspect`, `volumetricskew`, and `jacobian`.

```tcl
*createmark elems 1 all
set collapse_values [hm_getelemcheckvalues 1 3 tetracollapse]
set height_values   [hm_getelemcheckvalues 1 3 minlength]
set aspect_values   [hm_getelemcheckvalues 1 3 aspect]
set skew_values     [hm_getelemcheckvalues 1 3 volumetricskew]
set jacobian_values [hm_getelemcheckvalues 1 3 jacobian]
```

Do not infer the worst value from the failure threshold. Keep the HyperMesh
check method and solver profile in the report because quality definitions can
change with the selected method. For linear tetra elements, a Jacobian value of
one can coexist with poor collapse or skew and does not overrule them.

In addition to the worst value, report meaningful distributions. At minimum,
split minimum-height failures into `<0.25*gate`, `0.25-0.5*gate`,
`0.5-0.75*gate`, and `0.75-1.0*gate`, then distinguish severe degeneracy from
marginal misses.

## 2. Localize and Cross-Correlate Failed Patches

1. Export every failed element ID/value/centroid per metric.
2. Group failures by face/edge adjacency or a radius related to local size; add
   at least one neighboring layer before remediation.
3. Intersect metric sets. If every collapse/aspect/skew failure is contained in
   the minimum-height set, repair their common geometric or boundary-triangle
   cause first.
4. Map clusters to CAD surface/edge IDs and identify short edges, sliver faces,
   narrow gaps, small fillets/chamfers, hole ligaments, intersections, contacts,
   load/constraint regions, material interfaces, and symmetry boundaries.
5. Record whether the worst element is on the boundary or inside the volume and
   whether adjacent surface trias already fail size, angle, aspect, or skew.

Repeated optimizer runs that merely renumber bad elements are not improvement.
Reject a run when the dominant failure count improves by less than one percent,
another metric worsens, or failures migrate into a more critical region.

## 3. Check Geometry-to-Criteria Feasibility

Before meshing, compare these quantities in one table:

- smallest retained edge and narrowest retained face;
- smallest protected fillet/chamfer profile and hole ligament;
- target surface size and global minimum size;
- local protected-feature size and allowed growth;
- minimum-height/length quality gate.

If a retained feature is approximately equal to or smaller than the
minimum-height gate, there is no robust geometric margin. Choose one reviewed
route:

- preserve it and use an explicit local control plus a retained-versus-
  simplified sensitivity/convergence study;
- reconstruct or suppress it only when its physics role is negligible;
- revise the criterion only with downstream solver/formulation justification.

Do not apply the smallest curvature size globally. As a BatchMesher planning
baseline, Altair recommends a minimum size near 33% of target size, with roughly
40-50% still practical in some cases. Use this as a regular-surface baseline,
not a universal law. Put smaller sizes only on protected holes, blends,
contacts, or result-sensitive regions and transition outward explicitly.

## 4. Surface-First Remediation Sequence

Apply this order:

1. Repair free/T/non-manifold edges, intersections, overlaps, duplicate faces,
   bad normals, sliver surfaces, and unprotected cosmetic short edges.
2. Classify every small hole, fillet, chamfer, and narrow face as protected,
   local-control, sensitivity-study, or suppression candidate. Never automatic-
   suppress unknown load/contact/fatigue features.
3. Generate the closed surface-tria mesh first. Check free/T-edges, duplicates,
   minimum normalized height/size, aspect, skew, min/max angle, curvature
   adherence, and transition quality before tetra generation.
4. Use a regular model-level size range. Add surface-deviation, angle-based,
   hole/washer, fillet, proximity, and local-size controls only to measured
   feature sets. Prefer a local fine band with growth at or below about 1.25
   when the original 1.3 transition contributes abrupt flat tets.
5. Generate the affected tetra volume with the installed-version options for
   minimum-height restriction and quality optimization. Preserve anchors and
   required boundaries.
6. If failures remain, remesh the failed cluster plus neighbors. In Solid Mesh
   Optimization, boundary-triangle `Remesh` usually offers more freedom than
   fixed triangles or edge swaps; protect feature lines, component interfaces,
   geometry edges, and anchor nodes.
7. Re-run every active metric and compare exact worst values, counts, locations,
   element count, time, geometry adherence, and moved boundary nodes.

Node smoothing or tetra optimization belongs after geometry and boundary-tria
repair. It cannot remove a CAD sliver or create transition distance that the
surface topology does not provide.

## 5. Acceptance Contract

Block automatic acceptance unless all of the following hold:

- exact worst values and IDs exist even for metrics with zero failures;
- all active solver-specific failure counts are zero, or each residual
  exception is localized and backed by solver evidence;
- no protected feature, contact, load, constraint, material, or interface
  entity was lost;
- geometry volume/bounding-box deviation and free/non-manifold topology remain
  within documented tolerances;
- no metric improves by hiding a worse value in another criterion;
- any removed stress/contact/fatigue feature has sensitivity or convergence
  evidence;
- the final-order mesh is checked after second-order conversion when used.

## Research Basis

- [Altair tetra-meshing tutorial: curvature/proximity, defeaturing, surface-first mesh, and mesh controls](https://2025.help.altair.com/2025/hwdesktop/hwx/topics/tutorials/hwx/tetrameshing_t.htm)
- [Altair Solid Mesh Optimization: boundary remesh, anchors, feature lines, and rejection](https://2025.help.altair.com/2025/hwdesktop/hwx/topics/pre_processing/meshing/solid_mesh_optimization_t.htm)
- [Altair `hm_getelemcheckvalues` command](https://2025.help.altair.com/2025/hwdesktop/hwd/topics/reference/hm/hm_getelemcheckvalues.htm)
- [Altair element-quality definitions for minimum height, tet collapse, aspect, and volume skew](https://2025.help.altair.com/2025/hwdesktop/cfd/topics/pre_processing/meshing/element_quality_calculations_hypermesh_r.htm)
- [Altair BatchMesher criteria/parameter best practices](https://2025.help.altair.com/2025.1/hwdesktop/hwx/topics/pre_processing/meshing/batchmesher_criteria_parameter_best_practices_r.htm)
- [Bilibili Solid Mesh Optimization notes](https://www.bilibili.com/opus/992617012877328386): practical emphasis on surface-mesh quality and local remesh/optimization; exact commands and definitions were cross-checked against Altair documentation.
- [Bilibili HyperMesh quality-check and tetra-workflow course](https://www.bilibili.com/video/BV1Mh4y117nQ/): community workflow reference; numerical rules were not accepted without official cross-checking.
