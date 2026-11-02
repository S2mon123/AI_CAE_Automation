from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from ..config import configured_solver_paths, load_toolbox_config
from .common import run_process


def resolve_lammps_command(lammps_exe: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "lammps")
    for candidate in [
        lammps_exe,
        os.environ.get("LAMMPS_EXE"),
        configured.get("lammps_exe"),
        shutil.which("lmp"),
        shutil.which("lmp_serial"),
        shutil.which("lmp_mpi"),
    ]:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
        if candidate and shutil.which(str(candidate)):
            return str(shutil.which(str(candidate)))
    return None


def lammps_check_install(lammps_exe: str | None = None) -> dict[str, Any]:
    command = resolve_lammps_command(lammps_exe)
    return {
        "status": "ok" if command else "missing",
        "checks": {"lammps_exe": {"path": command, "exists": bool(command)}},
        "message": "Potential files are user-supplied inputs and require separate redistribution-rights review.",
    }


def lammps_run_input(
    input_path: str,
    run_dir: str,
    lammps_exe: str | None = None,
    extra_args: list[str] | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    command = resolve_lammps_command(lammps_exe)
    input_file = Path(input_path)
    if command is None:
        return {"status": "missing", "message": "LAMMPS executable not found. Set LAMMPS_EXE."}
    if not input_file.exists():
        return {"status": "missing", "message": f"LAMMPS input not found: {input_file}"}
    return run_process(
        command=command,
        args=[*(extra_args or []), "-in", input_file.name],
        run_dir=run_dir,
        log_name="lammps_run.log",
        timeout_sec=timeout_sec,
        cwd=input_file.parent,
    )
