from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

from ..config import configured_solver_paths, load_toolbox_config
from .ansys import ansys_run_workbench_journal, resolve_workbench_command
from .common import probe_python_import, run_process


def resolve_mechanical_python(python_exe: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "ansys-mechanical")
    candidates = [
        python_exe,
        os.environ.get("PYMECHANICAL_PYTHON"),
        configured.get("python"),
        shutil.which("python"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
        if candidate and shutil.which(str(candidate)):
            return str(shutil.which(str(candidate)))
    return None


def mechanical_check_install(
    workbench_exe: str | None = None,
    python_exe: str | None = None,
) -> dict[str, Any]:
    workbench = resolve_workbench_command(workbench_exe)
    python = resolve_mechanical_python(python_exe)
    import_probe = probe_python_import(python, "ansys.mechanical.core") if python else None
    checks = {
        "workbench_exe": {"path": workbench, "exists": bool(workbench and Path(workbench).exists())},
        "pymechanical_python": {
            "path": python,
            "exists": bool(python and Path(python).exists()),
            "import_ok": bool(import_probe and import_probe["ok"]),
        },
    }
    available_routes = []
    if checks["workbench_exe"]["exists"]:
        available_routes.append("Workbench RunWB2 journal / Mechanical ExtAPI")
    if checks["pymechanical_python"]["import_ok"]:
        available_routes.append("PyMechanical gRPC controller")
    return {
        "status": "ok" if available_routes else "missing",
        "checks": checks,
        "import_probe": import_probe,
        "available_routes": available_routes,
        "message": "A configured route is only a prerequisite; solve status and MAPDL logs are separate evidence gates.",
    }


def mechanical_run_workbench_journal(
    journal_path: str,
    run_dir: str,
    workbench_exe: str | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    return ansys_run_workbench_journal(journal_path, run_dir, workbench_exe, timeout_sec)


def mechanical_run_python_controller(
    script_path: str,
    run_dir: str,
    python_exe: str | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    command = resolve_mechanical_python(python_exe)
    script = Path(script_path)
    if command is None:
        return {"status": "missing", "message": "PyMechanical Python not found. Set PYMECHANICAL_PYTHON."}
    if not script.exists():
        return {"status": "missing", "message": f"controller script not found: {script}"}
    return run_process(
        command=command,
        args=[str(script)],
        run_dir=run_dir,
        log_name="mechanical_pythondriver.log",
        timeout_sec=timeout_sec,
        cwd=script.parent,
    )


def _resolve_summary_path(summary_file: Path, value: Any) -> Path | None:
    if not value:
        return None
    path = Path(str(value)).expanduser()
    if not path.is_absolute():
        path = summary_file.parent / path
    return path.resolve()


def _existing_exports(summary_file: Path, values: Any, suffixes: set[str]) -> list[str]:
    if not isinstance(values, list):
        return []
    hits: list[str] = []
    for value in values:
        path = _resolve_summary_path(summary_file, value)
        if path and path.exists() and path.suffix.lower() in suffixes:
            hits.append(str(path))
    return hits


def mechanical_validate_result_summary(summary_path: str, solve_log_path: str | None = None) -> dict[str, Any]:
    summary_file = Path(summary_path)
    if not summary_file.exists():
        return {"status": "missing", "message": f"result summary not found: {summary_file}"}
    try:
        payload = json.loads(summary_file.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "failed", "message": f"invalid result summary: {exc}"}
    state = str(payload.get("analysis_object_state", "")).strip().lower()
    normal = bool(payload.get("normal_mapdl_termination"))
    reaction_error = payload.get("reaction_balance_error_percent")
    reaction_ok = isinstance(reaction_error, (int, float)) and float(reaction_error) <= 1.0
    result_path = _resolve_summary_path(summary_file, payload.get("result_file"))
    result_exists = bool(result_path and result_path.exists() and result_path.suffix.lower() == ".rst")
    mesh = payload.get("mesh_quality", {})
    element_count = mesh.get("element_count") if isinstance(mesh, dict) else None
    failed_elements = mesh.get("failed_element_count") if isinstance(mesh, dict) else None
    mesh_accepted = mesh.get("accepted") if isinstance(mesh, dict) else None
    mesh_ok = bool(
        isinstance(element_count, int)
        and element_count > 0
        and (mesh_accepted is True or failed_elements == 0)
    )
    numeric_exports = _existing_exports(summary_file, payload.get("numeric_exports"), {".csv", ".json", ".txt"})
    image_exports = _existing_exports(
        summary_file,
        payload.get("image_exports"),
        {".png", ".jpg", ".jpeg", ".tif", ".tiff"},
    )
    log_value = solve_log_path or payload.get("solve_log_file")
    log_path = _resolve_summary_path(summary_file, log_value)
    solve_text = ""
    if log_path and log_path.exists():
        solve_text = log_path.read_text(encoding="utf-8", errors="replace").lower()
    log_normal = bool(
        solve_text
        and (
            "normal termination" in solve_text
            or "analysis has completed successfully" in solve_text
            or "solution completed" in solve_text
        )
    )
    gates = {
        "analysis_state_solved": state == "solved",
        "normal_mapdl_termination": normal and log_normal,
        "reaction_balance_within_1_percent": reaction_ok,
        "mesh_evidence_accepted": mesh_ok,
        "rst_result_file_exists": result_exists,
        "numeric_export_exists": bool(numeric_exports),
        "image_export_exists": bool(image_exports),
        "solve_log_exists": bool(log_path and log_path.exists()),
    }
    return {
        "status": "ok" if all(gates.values()) else "failed",
        "gates": gates,
        "reaction_balance_error_percent": reaction_error,
        "resolved_paths": {
            "result_file": str(result_path) if result_path else None,
            "solve_log_file": str(log_path) if log_path else None,
            "numeric_exports": numeric_exports,
            "image_exports": image_exports,
        },
        "message": (
            "Mechanical credibility requires every gate; a Workbench project, .mechdat, "
            "RST, or PNG alone is not proof of a solved and checked model."
        ),
    }
