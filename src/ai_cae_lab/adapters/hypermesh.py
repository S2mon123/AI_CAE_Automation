from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from ..config import configured_solver_paths, load_toolbox_config
from .common import run_process


def resolve_hmbatch(batch_exe: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "hypermesh")
    for candidate in [
        batch_exe,
        os.environ.get("HMBATCH_EXE"),
        configured.get("batch_exe"),
        shutil.which("hmbatch"),
    ]:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
        if candidate and shutil.which(str(candidate)):
            return str(shutil.which(str(candidate)))
    return None


def hypermesh_check_install(batch_exe: str | None = None) -> dict[str, Any]:
    batch = resolve_hmbatch(batch_exe)
    return {
        "status": "ok" if batch else "missing",
        "checks": {"hmbatch_exe": {"path": batch, "exists": bool(batch)}},
        "message": "The public adapter supports explicit user-supplied Tcl through hmbatch -tcl.",
    }


def hypermesh_run_tcl(
    script_path: str,
    run_dir: str,
    batch_exe: str | None = None,
    timeout_sec: int = 3600,
) -> dict[str, Any]:
    command = resolve_hmbatch(batch_exe)
    script = Path(script_path)
    if command is None:
        return {"status": "missing", "message": "hmbatch.exe not found. Set HMBATCH_EXE."}
    if not script.exists():
        return {"status": "missing", "message": f"Tcl script not found: {script}"}
    return run_process(
        command=command,
        args=["-tcl", str(script)],
        run_dir=run_dir,
        log_name="hypermesh_hmbatch.log",
        timeout_sec=timeout_sec,
        cwd=script.parent,
    )
