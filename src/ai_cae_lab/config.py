from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .context_scope import solver_context_scope


DEFAULT_CONFIG_FILENAMES = (
    "private/ai-cae.local.json",
    "private/toolbox.local.json",
    "ai-cae-toolbox.local.json",
    "toolbox.local.json",
    "configs/toolbox.local.json",
)
EXAMPLE_CONFIG_FILENAMES = (
    "configs/toolbox.example.json",
    "configs/local.toolchain.template.json",
)
SOLVER_CONFIG_KEYS = {
    "abaqus",
    "ansys",
    "fluent",
    "workbench",
    "ansys-workbench",
    "comsol",
    "matlab",
    "openfoam",
    "paraview",
    "pcschematic",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def normalize_solver_key(solver: str) -> str:
    key = solver.strip().lower()
    aliases = {
        "workbench": "ansys-workbench",
        "ansys": "ansys",
        "ansys-fluent": "fluent",
        "comsol-multiphysics": "comsol",
    }
    return aliases.get(key, key)


def is_placeholder_value(value: object) -> bool:
    if not isinstance(value, str):
        return False
    stripped = value.strip()
    return stripped.startswith("<") and stripped.endswith(">")


def _remove_placeholders(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _remove_placeholders(item) for key, item in value.items() if not is_placeholder_value(item)}
    if isinstance(value, list):
        return [_remove_placeholders(item) for item in value if not is_placeholder_value(item)]
    return value


def _normalize_toolbox_config(payload: dict[str, Any]) -> dict[str, Any]:
    solver_paths = payload.setdefault("solver_paths", {})
    for key in list(payload.keys()):
        if key in SOLVER_CONFIG_KEYS and isinstance(payload[key], dict):
            solver_paths.setdefault(normalize_solver_key(key), payload[key])
    if "workbench" in solver_paths and "ansys-workbench" not in solver_paths:
        solver_paths["ansys-workbench"] = solver_paths["workbench"]
    return payload


def load_toolbox_config(config_path: str | Path | None = None, include_examples: bool = False) -> dict[str, Any]:
    """Load a private local JSON config, falling back to empty public-safe defaults.

    Public example configs are not loaded by default because their placeholder
    values must never be treated as real author-machine paths.
    """
    candidates: list[Path] = []
    if config_path:
        candidates.append(Path(config_path))
    env_path = os.environ.get("AI_CAE_TOOLBOX_CONFIG")
    if env_path:
        candidates.append(Path(env_path))
    root = _repo_root()
    candidates.extend(root / name for name in DEFAULT_CONFIG_FILENAMES)
    if include_examples:
        candidates.extend(root / name for name in EXAMPLE_CONFIG_FILENAMES)

    for candidate in candidates:
        if candidate.exists():
            payload = json.loads(candidate.read_text(encoding="utf-8-sig"))
            payload = _normalize_toolbox_config(_remove_placeholders(payload))
            payload["_config_path"] = str(candidate)
            payload["_config_is_example"] = any(candidate.match(name) for name in EXAMPLE_CONFIG_FILENAMES)
            return payload

    return {
        "_config_path": None,
        "_config_is_example": False,
        "runs_root": "runs",
        "solver_environment_variables": {},
        "solver_paths": {},
        "bridge_profiles": {},
    }


def solver_env_names(config: dict[str, Any], solver: str) -> list[str]:
    solver = normalize_solver_key(solver)
    defaults = {
        "abaqus": ["ABAQUS_COMMAND"],
        "ansys": ["ANSYS_ROOT"],
        "ansys-workbench": ["ANSYS_ROOT", "WORKBENCH_EXE", "ANSYS_WORKBENCH_EXE"],
        "fluent": ["FLUENT_EXE", "FLUENT_ROOT"],
        "comsol": ["COMSOL_EXE", "COMSOL_ROOT", "COMSOL_BATCH", "COMSOL_COMPILE", "COMSOL_MPHSERVER", "COMSOL_JAVA"],
        "matlab": ["MATLAB_EXE", "MATLABROOT"],
        "openfoam": ["OPENFOAM_ROOT", "WM_PROJECT_DIR", "OPENFOAM_BLOCKMESH", "OPENFOAM_CHECKMESH"],
        "paraview": ["PARAVIEW_ROOT", "PVPYTHON_EXE"],
        "pcschematic": ["PCSCHEMATIC_EXE", "PCSCHEMATIC_ROOT", "PCSCHEMATIC_TLB"],
    }
    envs = config.get("solver_environment_variables", {})
    names = envs.get(solver, [])
    if solver == "ansys-workbench" and not names:
        names = envs.get("workbench", []) or envs.get("ansys", [])
    if not names:
        names = defaults.get(solver, [])
    return [str(item) for item in names]


def configured_solver_paths(config: dict[str, Any], solver: str) -> dict[str, str]:
    solver = normalize_solver_key(solver)
    paths = config.get("solver_paths", {})
    value = paths.get(solver, {})
    if solver == "ansys-workbench" and not value:
        value = paths.get("workbench", {}) or paths.get("ansys", {})
    if not isinstance(value, dict):
        return {}
    return {str(key): str(item) for key, item in value.items() if not is_placeholder_value(item)}


def toolchain_paths(
    solver: str,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    config = load_toolbox_config(config_path)
    solver_key = normalize_solver_key(solver)
    env_names = solver_env_names(config, solver_key)
    env_paths = {name: os.environ.get(name) for name in env_names if os.environ.get(name)}
    configured_paths = configured_solver_paths(config, solver_key)
    return {
        "solver": solver_key,
        "config_path": config.get("_config_path"),
        "config_is_example": config.get("_config_is_example", False),
        "environment_variables": env_names,
        "environment_values_set": env_paths,
        "configured_paths": configured_paths,
        "path_resolution_order": [
            "explicit MCP/CLI argument",
            "environment variable",
            "private local config from private/ai-cae.local.json or AI_CAE_TOOLBOX_CONFIG",
            "safe auto-discovery from registry, PATH, and known vendor install roots",
        ],
        "rules": [
            "Committed example/template paths are placeholders, not author-machine paths.",
            "Do not assume the repository author's drive letters or installation folders exist on another machine.",
            "When a path is missing, run ai-cae-toolbox setup or set an environment variable/private local config.",
        ],
    }


def bridge_plan(
    solver: str,
    objective: str = "",
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    """Return a structured, auditable solver bridge plan for agents."""
    config = load_toolbox_config(config_path)
    solver_key = normalize_solver_key(solver)
    env_names = solver_env_names(config, solver_key)
    configured_paths = configured_solver_paths(config, solver_key)

    tool_map = {
        "abaqus": [
            "solver_context_scope",
            "solver_toolchain_paths",
            "create_run_record",
            "write_solver_smoke_template",
            "abaqus_run_no_gui_script",
            "abaqus_submit_input_deck",
            "scan_run_evidence",
        ],
        "fluent": [
            "solver_context_scope",
            "solver_toolchain_paths",
            "create_run_record",
            "write_solver_smoke_template",
            "fluent_run_journal_file",
            "scan_run_evidence",
        ],
        "ansys-workbench": [
            "solver_context_scope",
            "solver_toolchain_paths",
            "create_run_record",
            "write_solver_smoke_template",
            "ansys_check_installation",
            "ansys_run_workbench_journal_file",
            "scan_run_evidence",
        ],
        "comsol": [
            "solver_context_scope",
            "solver_toolchain_paths",
            "create_run_record",
            "write_solver_smoke_template",
            "comsol_check_installation",
            "comsol_write_cube_smoke_java",
            "comsol_compile_java_file",
            "comsol_run_compiled_java_class",
            "comsol_run_java_model_to_mph_file",
            "comsol_write_mph_validator_java",
            "comsol_validate_mph_loadable_file",
            "comsol_run_batch_file",
            "scan_run_evidence",
        ],
        "matlab": [
            "solver_context_scope",
            "solver_toolchain_paths",
            "create_run_record",
            "write_solver_smoke_template",
            "matlab_check_installation",
            "scan_run_evidence",
        ],
        "openfoam": [
            "solver_context_scope",
            "solver_toolchain_paths",
            "create_run_record",
            "write_solver_smoke_template",
            "openfoam_check_installation",
            "scan_run_evidence",
        ],
        "paraview": [
            "solver_context_scope",
            "solver_toolchain_paths",
            "create_run_record",
            "write_solver_smoke_template",
            "paraview_check_installation",
            "scan_run_evidence",
        ],
        "pcschematic": [
            "solver_context_scope",
            "solver_toolchain_paths",
            "create_run_record",
            "pcschematic_check_installation",
            "scan_run_evidence",
        ],
    }

    phases = [
        "Call solver_context_scope first and load only the returned solver-relevant files.",
        "Resolve executable paths from explicit arguments, environment variables, private local config, or setup discovery.",
        "Create a run record before launching any solver.",
        "Check configured paths and module availability where the solver exposes a safe command.",
        "Generate or copy solver-native scripts into the run scripts directory.",
        "Run the smallest smoke case before attempting the full engineering model.",
        "Scan only the run directory for evidence, then grade logs and outputs.",
        "Only claim success when logs and artifacts support the claim.",
    ]

    return {
        "solver": solver_key,
        "objective": objective,
        "config_path": config.get("_config_path"),
        "environment_variables": env_names,
        "configured_paths": configured_paths,
        "context_scope": solver_context_scope(solver_key),
        "recommended_mcp_tools": tool_map.get(solver_key, ["solver_context_scope", "create_run_record", "scan_run_evidence"]),
        "phases": phases,
        "privacy_rules": [
            "Keep commercial solver binaries, manuals, licenses, and generated large result files out of git.",
            "Store machine-specific paths in a local config file ignored by git.",
            "Commit public templates, adapters, prompts, and documentation only.",
        ],
    }
