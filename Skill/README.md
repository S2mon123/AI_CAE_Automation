# Skill Index

This directory mirrors the public "MCP + Skill" repository shape and points to
the maintained Codex skill packs under `codex-skills/`.

## Maintained Skills

| Skill | Path | Purpose |
|---|---|---|
| `ai-cae-run-manager` | `codex-skills/ai-cae-run-manager` | Create run records, logs, reports, and evidence chains |
| `abaqus-evidence-simulation` | `codex-skills/abaqus-evidence-simulation` | Abaqus evidence-first automation |
| `fluent-evidence-cfd` | `codex-skills/fluent-evidence-cfd` | Fluent journal and CFD evidence workflows |
| `comsol-evidence-multiphysics` | `codex-skills/comsol-evidence-multiphysics` | COMSOL Java API and batch workflows |
| `open-toolchain-evidence` | `codex-skills/open-toolchain-evidence` | OpenFOAM, ParaView, MATLAB-style open bridge workflows |
| `pcschematic-evidence-cad` | `codex-skills/pcschematic-evidence-cad` | Electrical CAD evidence workflows |

Install them with:

```powershell
.\.venv\Scripts\python.exe scripts\install_codex_assets.py --install-skills --force
```

The actual skill source of truth is `codex-skills/`; this directory is an index
for GitHub readers who expect an MCP/Skill style project layout.
