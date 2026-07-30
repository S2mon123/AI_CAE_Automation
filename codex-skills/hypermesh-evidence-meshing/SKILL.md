---
name: hypermesh-evidence-meshing
description: Evidence-first Altair HyperMesh automation for CAD import, cleanup, surface or volume meshing, Tcl and hmbatch execution, BatchMesher diagnostics, solver-deck export, and mesh-quality reporting. Use when Codex must create, repair, audit, or export a HyperMesh model while preventing CAD-import failures or empty/low-quality meshes from being reported as success.
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
available.

## Gate the Workflow

1. Copy source CAD into the run input area; never overwrite the original.
2. Confirm the CAD reader/import completed and count imported surfaces/solids.
3. Audit free edges, duplicate surfaces, intersections, normals, and topology.
4. Generate surface mesh before volume mesh when the workflow requires it.
5. Apply explicit quality thresholds for the chosen solver profile.
6. Export `.hm`, solver deck, quality report, and command/log evidence.

Read [references/quality-gates.md](references/quality-gates.md) before accepting
the mesh. A return code of zero without entities and quality statistics is not a
successful mesh.

## Finish

Report source geometry type, import translator, entity counts, element counts,
element types, size controls, failed-quality counts, remediation, and exported
solver profile. Preserve failed BatchMesher logs because they identify translator
or parameter-file problems.
