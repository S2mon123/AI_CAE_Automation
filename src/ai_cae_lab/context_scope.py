from __future__ import annotations

from pathlib import Path
from typing import Any


COMMON_CONTEXT = [
    "README.md",
    "README.zh-CN.md",
    "mcp/MANIFEST.json",
    "mcp/README.md",
    "configs/README.md",
    "configs/toolbox.example.json",
    "configs/local.toolchain.schema.json",
    "docs/codex-mcp-skill-setup.md",
    "docs/deep-solver-bridge-mcp.md",
    "docs/mit-reference-and-mcp-restructure.md",
]

SOLVER_CONTEXT: dict[str, list[str]] = {
    "aedt": [
        "mcp/aedt",
        "codex-skills/aedt-evidence-electromagnetics",
        "examples/aedt-wireless-power",
        "prompts/aedt-electromagnetics.md",
        "src/ai_cae_lab/adapters/aedt.py",
        "src/ai_cae_lab/adapters/common.py",
        "checklists/aedt-evidence-chain.md",
    ],
    "abaqus": [
        "mcp/abaqus",
        "codex-skills/abaqus-evidence-simulation",
        "examples/abaqus-drilling",
        "prompts/abaqus-explicit-drilling.md",
        "src/ai_cae_lab/adapters/abaqus.py",
        "src/ai_cae_lab/adapters/common.py",
        "checklists/evidence-chain.md",
    ],
    "fluent": [
        "mcp/ansys/Fluent MCP",
        "mcp/ansys/fluent.md",
        "codex-skills/fluent-evidence-cfd",
        "examples/fluent-external-flow",
        "examples/fluent-sinusoidal-weld-pool",
        "prompts/fluent-external-flow.md",
        "prompts/fluent-sinusoidal-weld-pool.md",
        "src/ai_cae_lab/adapters/fluent.py",
        "src/ai_cae_lab/adapters/common.py",
        "checklists/fluent-weld-pool-evidence-chain.md",
    ],
    "ansys-workbench": [
        "mcp/ansys",
        "mcp/ansys/Workbench MCP",
        "docs/deep-solver-bridge-mcp.md",
        "src/ai_cae_lab/adapters/ansys.py",
        "src/ai_cae_lab/adapters/common.py",
        "checklists/evidence-chain.md",
    ],
    "ansys-mechanical": [
        "mcp/ansys/Mechanical MCP",
        "codex-skills/ansys-mechanical-evidence-structural",
        "examples/ansys-mechanical-static",
        "prompts/ansys-mechanical-structural.md",
        "src/ai_cae_lab/adapters/mechanical.py",
        "src/ai_cae_lab/adapters/ansys.py",
        "src/ai_cae_lab/adapters/common.py",
        "checklists/ansys-mechanical-evidence-chain.md",
    ],
    "hypermesh": [
        "mcp/hypermesh",
        "codex-skills/hypermesh-evidence-meshing",
        "examples/hypermesh-meshing",
        "prompts/hypermesh-meshing.md",
        "src/ai_cae_lab/adapters/hypermesh.py",
        "src/ai_cae_lab/adapters/common.py",
        "checklists/hypermesh-evidence-chain.md",
    ],
    "lammps": [
        "mcp/lammps",
        "codex-skills/lammps-evidence-md",
        "examples/lammps-tension",
        "prompts/lammps-molecular-dynamics.md",
        "src/ai_cae_lab/adapters/lammps.py",
        "src/ai_cae_lab/adapters/common.py",
        "checklists/lammps-ovito-evidence-chain.md",
    ],
    "ovito": [
        "mcp/ovito",
        "codex-skills/ovito-evidence-postprocessing",
        "examples/lammps-tension",
        "prompts/ovito-postprocessing.md",
        "src/ai_cae_lab/adapters/ovito.py",
        "src/ai_cae_lab/adapters/common.py",
        "checklists/lammps-ovito-evidence-chain.md",
    ],
    "comsol": [
        "mcp/comsol",
        "codex-skills/comsol-evidence-multiphysics",
        "codex-skills/comsol-motor-nvh-evidence",
        "examples/comsol-cube-10mm",
        "examples/comsol-ehd-soybean-drying",
        "examples/comsol-heat-transfer",
        "examples/comsol-pm-motor-nvh",
        "prompts/comsol-ehd-soybean-drying.md",
        "prompts/comsol-heat-transfer.md",
        "prompts/comsol-pm-motor-nvh.zh-CN.md",
        "src/ai_cae_lab/adapters/comsol.py",
        "src/ai_cae_lab/adapters/common.py",
        "src/ai_cae_lab/logs.py",
        "checklists/comsol-ehd-soybean-evidence-chain.md",
        "checklists/comsol-pm-motor-nvh-evidence-chain.md",
    ],
    "matlab": [
        "mcp/matlab",
        "codex-skills/open-toolchain-evidence",
        "src/ai_cae_lab/adapters/matlab.py",
        "src/ai_cae_lab/adapters/common.py",
        "checklists/evidence-chain.md",
    ],
    "openfoam": [
        "mcp/openfoam",
        "codex-skills/open-toolchain-evidence",
        "src/ai_cae_lab/adapters/openfoam.py",
        "src/ai_cae_lab/adapters/common.py",
        "checklists/evidence-chain.md",
    ],
    "paraview": [
        "mcp/paraview",
        "codex-skills/open-toolchain-evidence",
        "src/ai_cae_lab/adapters/paraview.py",
        "src/ai_cae_lab/adapters/common.py",
        "checklists/evidence-chain.md",
    ],
    "pcschematic": [
        "mcp/pcschematic",
        "codex-skills/pcschematic-evidence-cad",
        "examples/pcschematic-direct-motor-starter",
        "prompts/pcschematic-direct-motor-starter.md",
        "src/ai_cae_lab/adapters/pcschematic.py",
        "checklists/electrical-cad-evidence-chain.md",
    ],
}

ALIASES = {
    "ansys": "ansys-workbench",
    "ansys-aedt": "aedt",
    "hfss": "aedt",
    "maxwell": "aedt",
    "workbench": "ansys-workbench",
    "mechanical": "ansys-mechanical",
    "ansys-structural": "ansys-mechanical",
    "ansys-fluent": "fluent",
    "altair-hypermesh": "hypermesh",
    "comsol-multiphysics": "comsol",
    "pcschematic-automation": "pcschematic",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def normalize_solver(solver: str) -> str:
    key = solver.strip().lower()
    return ALIASES.get(key, key)


def solver_context_scope(
    solver: str,
    include_common: bool = True,
    root: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(root) if root else repo_root()
    solver_key = normalize_solver(solver)
    relative_paths = list(SOLVER_CONTEXT.get(solver_key, []))
    if include_common:
        relative_paths = [*COMMON_CONTEXT, *relative_paths]

    seen: set[str] = set()
    existing: list[dict[str, str]] = []
    missing: list[str] = []
    for relative in relative_paths:
        if relative in seen:
            continue
        seen.add(relative)
        path = base / relative
        if path.exists():
            existing.append(
                {
                    "path": relative,
                    "kind": "directory" if path.is_dir() else "file",
                }
            )
        else:
            missing.append(relative)

    return {
        "solver": solver_key,
        "repo_root": str(base),
        "scope": existing,
        "missing": missing,
        "rules": [
            "Load only these files/directories before planning a solver task unless the user asks for a repo-wide audit.",
            "Do not recursively scan the whole repository for normal modeling/simulation tasks.",
            "Use run directories for generated logs and outputs; scan evidence only inside the selected run directory.",
            "Resolve executable paths from environment variables or a private local config, never from committed author-machine paths.",
        ],
    }
