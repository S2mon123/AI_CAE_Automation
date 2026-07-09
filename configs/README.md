# Configuration Examples

This folder contains public-safe configuration examples. Copy them outside the
repository before adding local machine paths, license settings, or private
project locations.

Use environment variables or a private JSON config instead of committed local
paths. The recommended first-run path is:

```powershell
.\.venv\Scripts\ai-cae-toolbox.exe setup
. .\private\activate-ai-cae.ps1
```

`setup` writes `private/ai-cae.local.json`, `private/activate-ai-cae.ps1`, and `private/codex-mcp.local.toml`. Example/template files are not loaded automatically by the toolbox. Start from `local.toolchain.template.json` only when you want to hand-edit a private file, then set `AI_CAE_TOOLBOX_CONFIG` or place it under `private/ai-cae.local.json`. Validate private configs against `local.toolchain.schema.json` when your editor or CI supports JSON Schema.

| Solver | Suggested environment variables |
|---|---|
| Abaqus | `ABAQUS_COMMAND` |
| Ansys Workbench | `ANSYS_ROOT`, `WORKBENCH_EXE`, `ANSYS_WORKBENCH_EXE` |
| Ansys Fluent | `FLUENT_EXE`, `FLUENT_ROOT` |
| COMSOL | `COMSOL_EXE`, `COMSOL_ROOT`, `COMSOL_BATCH`, `COMSOL_COMPILE`, `COMSOL_MPHSERVER`, `COMSOL_JAVA` |
| MATLAB | `MATLAB_EXE`, `MATLABROOT` |
| OpenFOAM | `OPENFOAM_ROOT`, `WM_PROJECT_DIR`, `OPENFOAM_BLOCKMESH`, `OPENFOAM_CHECKMESH` |
| ParaView | `PARAVIEW_ROOT`, `PVPYTHON_EXE` |
| PCSCHEMATIC | `PCSCHEMATIC_EXE`, `PCSCHEMATIC_ROOT`, `PCSCHEMATIC_TLB` |

Do not commit real customer models, licensed manuals, raw solver outputs, or
private installation paths.
