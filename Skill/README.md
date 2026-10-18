# Skill Index

This directory mirrors the public "MCP + Skill" repository shape and points to
the maintained Codex skill packs under `codex-skills/`.

## Maintained Skills

- [Adams evidence MBD](../codex-skills/adams-evidence-mbd/SKILL.md): standalone
  Adams MCP modeling, transient execution and reaction-history validation.

| Skill | Path | Purpose |
|---|---|---|
| `ai-cae-run-manager` | `codex-skills/ai-cae-run-manager` | Create run records, logs, reports, and evidence chains |
| `aedt-evidence-electromagnetics` | `codex-skills/aedt-evidence-electromagnetics` | AEDT/PyAEDT design, solve, field, and table evidence |
| `abaqus-evidence-simulation` | `codex-skills/abaqus-evidence-simulation` | Abaqus evidence-first automation |
| `fluent-evidence-cfd` | `codex-skills/fluent-evidence-cfd` | Fluent journal and CFD evidence workflows |
| `ansys-mechanical-evidence-structural` | `codex-skills/ansys-mechanical-evidence-structural` | Mechanical solve, MAPDL, reaction, mesh, and RST gates |
| `hypermesh-evidence-meshing` | `codex-skills/hypermesh-evidence-meshing` | CAD import, Tcl meshing, quality, and deck export |
| `lammps-evidence-md` | `codex-skills/lammps-evidence-md` | LAMMPS input, potential, thermo, trajectory, and validation |
| `ovito-evidence-postprocessing` | `codex-skills/ovito-evidence-postprocessing` | OVITO pipeline, render, table, and provenance evidence |
| `comsol-evidence-multiphysics` | `codex-skills/comsol-evidence-multiphysics` | COMSOL Java API and batch workflows |
| `open-toolchain-evidence` | `codex-skills/open-toolchain-evidence` | OpenFOAM, ParaView, MATLAB-style open bridge workflows |
| `pcschematic-evidence-cad` | `codex-skills/pcschematic-evidence-cad` | Electrical CAD evidence workflows |

Install them with:

```powershell
.\.venv\Scripts\python.exe scripts\install_codex_assets.py --install-skills --force
```

The actual skill source of truth is `codex-skills/`; this directory is an index
for GitHub readers who expect an MCP/Skill style project layout.
