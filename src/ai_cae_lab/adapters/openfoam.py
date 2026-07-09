from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from .common import run_process


def resolve_openfoam_command(command_name: str, explicit_path: str | None = None) -> str | None:
    candidates = [
        explicit_path,
        os.environ.get(f"OPENFOAM_{command_name.upper()}"),
        shutil.which(command_name),
    ]
    for candidate in candidates:
        if candidate and Path(str(candidate)).exists():
            return str(Path(str(candidate)))
        if candidate and shutil.which(str(candidate)):
            return str(shutil.which(str(candidate)))
    return None


def openfoam_check_install(openfoam_root: str | None = None) -> dict[str, Any]:
    root = openfoam_root or os.environ.get("OPENFOAM_ROOT") or os.environ.get("WM_PROJECT_DIR")
    checks = {
        "openfoam_root": {"path": root, "exists": bool(root and Path(root).exists())},
        "blockMesh": {"path": resolve_openfoam_command("blockMesh"), "exists": bool(resolve_openfoam_command("blockMesh"))},
        "checkMesh": {"path": resolve_openfoam_command("checkMesh"), "exists": bool(resolve_openfoam_command("checkMesh"))},
        "wsl": {"path": shutil.which("wsl"), "exists": bool(shutil.which("wsl"))},
    }
    return {
        "status": "ok" if any(item["exists"] for item in checks.values()) else "missing",
        "checks": checks,
        "message": "This check does not launch an OpenFOAM case.",
    }


def openfoam_run_command(
    command_name: str,
    case_dir: str,
    run_dir: str,
    timeout_sec: int = 3600,
) -> dict[str, Any]:
    command = resolve_openfoam_command(command_name)
    case = Path(case_dir)
    if command is None:
        return {"status": "missing", "message": f"OpenFOAM command not found: {command_name}"}
    if not case.exists():
        return {"status": "missing", "message": f"OpenFOAM case directory not found: {case}"}
    return run_process(
        command=command,
        args=["-case", str(case)],
        run_dir=run_dir,
        log_name=f"openfoam_{command_name}.log",
        timeout_sec=timeout_sec,
    )
