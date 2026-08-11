from __future__ import annotations


SKILL_PACKS = [
    {
        "name": "ai-cae-run-manager",
        "path": "codex-skills/ai-cae-run-manager",
        "purpose": "Evidence-first run folders, scans, credibility grades, and reports.",
        "best_with": ["env_check", "create_run_record", "scan_run_evidence", "generate_run_report"],
    },
    {
        "name": "aedt-evidence-electromagnetics",
        "path": "codex-skills/aedt-evidence-electromagnetics",
        "purpose": "AEDT/PyAEDT electromagnetics with design-type checks, solver logs, fields, and tables.",
        "best_with": ["ai-cae-run-manager"],
    },
    {
        "name": "abaqus-evidence-simulation",
        "path": "codex-skills/abaqus-evidence-simulation",
        "purpose": "Abaqus modeling, input decks, job submission, ODB evidence, and result exports.",
        "best_with": ["ai-cae-run-manager"],
    },
    {
        "name": "fluent-evidence-cfd",
        "path": "codex-skills/fluent-evidence-cfd",
        "purpose": "Fluent journals, PyFluent workflows, residual logs, case/data evidence, and CFD exports.",
        "best_with": ["ai-cae-run-manager"],
    },
    {
        "name": "ansys-mechanical-evidence-structural",
        "path": "codex-skills/ansys-mechanical-evidence-structural",
        "purpose": "Mechanical structural analysis through RunWB2, ACT/ExtAPI, or PyMechanical with solve gates.",
        "best_with": ["ai-cae-run-manager"],
    },
    {
        "name": "hypermesh-evidence-meshing",
        "path": "codex-skills/hypermesh-evidence-meshing",
        "purpose": "HyperMesh Tcl/batch meshing with CAD-import and mesh-quality gates.",
        "best_with": ["ai-cae-run-manager"],
    },
    {
        "name": "lammps-evidence-md",
        "path": "codex-skills/lammps-evidence-md",
        "purpose": "LAMMPS molecular dynamics inputs, logs, thermo data, trajectories, and reproducibility checks.",
        "best_with": ["ai-cae-run-manager", "ovito-evidence-postprocessing"],
    },
    {
        "name": "ovito-evidence-postprocessing",
        "path": "codex-skills/ovito-evidence-postprocessing",
        "purpose": "OVITO visualization and atomistic postprocessing with pipeline and export evidence.",
        "best_with": ["ai-cae-run-manager", "lammps-evidence-md"],
    },
    {
        "name": "comsol-evidence-multiphysics",
        "path": "codex-skills/comsol-evidence-multiphysics",
        "purpose": "COMSOL Java API, batch runs, local API docs, MPH exports, and multiphysics reports.",
        "best_with": ["ai-cae-run-manager"],
    },
    {
        "name": "open-toolchain-evidence",
        "path": "codex-skills/open-toolchain-evidence",
        "purpose": "MATLAB/Simulink, OpenFOAM, and ParaView automation with logs and exported evidence.",
        "best_with": ["ai-cae-run-manager"],
    },
    {
        "name": "pcschematic-evidence-cad",
        "path": "codex-skills/pcschematic-evidence-cad",
        "purpose": "PCSCHEMATIC COM/OLE, component and symbol evidence, electrical CAD exports.",
        "best_with": ["ai-cae-run-manager"],
    },
]


def list_skill_packs() -> list[dict[str, object]]:
    return SKILL_PACKS.copy()
