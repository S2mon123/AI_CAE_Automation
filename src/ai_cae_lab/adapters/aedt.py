from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from ..config import configured_solver_paths, load_toolbox_config
from .common import probe_python_import, run_process


def _first_command(candidates: list[str | Path | None]) -> str | None:
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists():
            return str(path)
        found = shutil.which(str(candidate))
        if found:
            return found
    return None


def resolve_aedt_exe(aedt_exe: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "aedt")
    root = os.environ.get("AEDT_INSTALL_DIR") or configured.get("root")
    return _first_command(
        [
            aedt_exe,
            os.environ.get("AEDT_EXE"),
            configured.get("aedt_exe"),
            Path(root) / "ansysedt.exe" if root else None,
            shutil.which("ansysedt"),
        ]
    )


def resolve_pyaedt_python(python_exe: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "aedt")
    return _first_command(
        [
            python_exe,
            os.environ.get("PYAEDT_PYTHON"),
            configured.get("python"),
            shutil.which("python"),
        ]
    )


def aedt_check_install(aedt_exe: str | None = None, python_exe: str | None = None) -> dict[str, Any]:
    aedt = resolve_aedt_exe(aedt_exe)
    python = resolve_pyaedt_python(python_exe)
    import_probe = probe_python_import(python, "ansys.aedt.core") if python else None
    checks = {
        "aedt_exe": {"path": aedt, "exists": bool(aedt and Path(aedt).exists())},
        "pyaedt_python": {
            "path": python,
            "exists": bool(python and Path(python).exists()),
            "import_ok": bool(import_probe and import_probe["ok"]),
        },
    }
    if checks["aedt_exe"]["exists"] and checks["pyaedt_python"]["import_ok"]:
        status = "ok"
    elif checks["aedt_exe"]["exists"] or checks["pyaedt_python"]["import_ok"]:
        status = "partial"
    else:
        status = "missing"
    return {
        "status": status,
        "checks": checks,
        "import_probe": import_probe,
        "message": (
            "The import probe does not start AEDT or prove that a license can be checked out. "
            "Run a disposable PyAEDT connection smoke before claiming desktop control."
        ),
    }


def aedt_run_pyaedt_script(
    script_path: str,
    run_dir: str,
    python_exe: str | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    command = resolve_pyaedt_python(python_exe)
    script = Path(script_path)
    if command is None:
        return {"status": "missing", "message": "PyAEDT Python not found. Set PYAEDT_PYTHON."}
    if not script.exists():
        return {"status": "missing", "message": f"PyAEDT script not found: {script}"}
    return run_process(
        command=command,
        args=[str(script)],
        run_dir=run_dir,
        log_name="aedt_pyaedt.log",
        timeout_sec=timeout_sec,
        cwd=script.parent,
    )
