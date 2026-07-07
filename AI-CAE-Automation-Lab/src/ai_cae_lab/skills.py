from __future__ import annotations


SKILL_PACKS = [
    {
        "name": "ai-cae-run-manager",
        "path": "codex-skills/ai-cae-run-manager",
        "purpose": "Evidence-first run folders, scans, credibility grades, and reports.",
        "best_with": ["env_check", "create_run_record", "scan_run_evidence", "generate_run_report"],
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
        "name": "comsol-evidence-multiphysics",
        "path": "codex-skills/comsol-evidence-multiphysics",
        "purpose": "COMSOL Java API, batch runs, local API docs, MPH exports, and multiphysics reports.",
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
