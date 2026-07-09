from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from .common import run_process


def _paraview_candidates_from_root(root: str | None) -> list[Path]:
    if not root:
        return []
    base = Path(root)
    if not base.exists():
        return []
    return [*sorted(base.glob("**/pvpython.exe")), *sorted(base.glob("**/paraview.exe"))]


def resolve_pvpython(pvpython: str | None = None) -> str | None:
    candidates: list[str | Path | None] = [
        pvpython,
        os.environ.get("PVPYTHON_EXE"),
        shutil.which("pvpython"),
        *_paraview_candidates_from_root(os.environ.get("PARAVIEW_ROOT")),
    ]
    for candidate in candidates:
        if candidate and Path(str(candidate)).exists():
            return str(Path(str(candidate)))
        if candidate and shutil.which(str(candidate)):
            return str(shutil.which(str(candidate)))
    return None


def paraview_check_install(pvpython: str | None = None, paraview_root: str | None = None) -> dict[str, Any]:
    root = paraview_root or os.environ.get("PARAVIEW_ROOT")
    command = resolve_pvpython(pvpython)
    checks = {
        "paraview_root": {"path": root, "exists": bool(root and Path(root).exists())},
        "pvpython": {"path": command, "exists": bool(command and Path(command).exists())},
    }
    return {
        "status": "ok" if any(item["exists"] for item in checks.values()) else "missing",
        "checks": checks,
        "message": "This check does not launch ParaView GUI.",
    }


def paraview_run_script(
    script_path: str,
    run_dir: str,
    pvpython: str | None = None,
    timeout_sec: int = 3600,
) -> dict[str, Any]:
    command = resolve_pvpython(pvpython)
    script = Path(script_path)
    if command is None:
        return {"status": "missing", "message": "pvpython not found. Set PVPYTHON_EXE or PARAVIEW_ROOT."}
    if not script.exists():
        return {"status": "missing", "message": f"ParaView script not found: {script}"}
    return run_process(
        command=command,
        args=[str(script)],
        run_dir=run_dir,
        log_name="paraview_pvpython.log",
        timeout_sec=timeout_sec,
    )
