from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from ..config import configured_solver_paths, load_toolbox_config
from .common import run_process


def _matlab_candidates_from_root(root: str | None) -> list[Path]:
    if not root:
        return []
    base = Path(root)
    if not base.exists():
        return []
    return sorted(base.glob("R*/bin/matlab.exe"))


def resolve_matlab_command(matlab_command: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "matlab")
    matlab_root = os.environ.get("MATLABROOT") or configured.get("root")
    candidates: list[str | Path | None] = [
        matlab_command,
        os.environ.get("MATLAB_EXE"),
        configured.get("matlab_exe"),
        shutil.which("matlab"),
        *_matlab_candidates_from_root(matlab_root),
    ]
    for candidate in candidates:
        if candidate and Path(str(candidate)).exists():
            return str(Path(str(candidate)))
        if candidate and shutil.which(str(candidate)):
            return str(shutil.which(str(candidate)))
    return None


def matlab_check_install(matlab_command: str | None = None, matlab_root: str | None = None) -> dict[str, Any]:
    configured = configured_solver_paths(load_toolbox_config(), "matlab")
    root = matlab_root or os.environ.get("MATLABROOT") or configured.get("root")
    command = resolve_matlab_command(matlab_command)
    checks = {
        "matlab_root": {"path": root, "exists": bool(root and Path(root).exists())},
        "matlab_exe": {"path": command, "exists": bool(command and Path(command).exists())},
    }
    return {
        "status": "ok" if any(item["exists"] for item in checks.values()) else "missing",
        "checks": checks,
        "message": "This check does not launch MATLAB or modify models.",
    }


def matlab_run_script(
    script_path: str,
    run_dir: str,
    matlab_command: str | None = None,
    timeout_sec: int = 3600,
) -> dict[str, Any]:
    command = resolve_matlab_command(matlab_command)
    script = Path(script_path)
    if command is None:
        return {"status": "missing", "message": "MATLAB command not found. Set MATLAB_EXE or MATLABROOT."}
    if not script.exists():
        return {"status": "missing", "message": f"MATLAB script not found: {script}"}
    return run_process(
        command=command,
        args=["-batch", f"run('{script.as_posix()}')"],
        run_dir=run_dir,
        log_name="matlab_batch.log",
        timeout_sec=timeout_sec,
    )
