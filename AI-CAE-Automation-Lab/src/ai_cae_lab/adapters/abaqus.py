from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from .common import run_process


DEFAULT_ABAQUS_COMMANDS = [
    r"C:\SIMULIA\Commands\abaqus.bat",
    r"D:\SIMULIA\Commands\abaqus.bat",
    r"G:\SIMULIA\Commands\abaqus.bat",
]


def resolve_abaqus_command(abaqus_command: str | None = None) -> str | None:
    candidates = [
        abaqus_command,
        os.environ.get("ABAQUS_COMMAND"),
        shutil.which("abaqus"),
        *DEFAULT_ABAQUS_COMMANDS,
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
        if candidate and shutil.which(candidate):
            return str(shutil.which(candidate))
    return None


def abaqus_run_no_gui(
    script_path: str,
    run_dir: str,
    abaqus_command: str | None = None,
    timeout_sec: int = 3600,
) -> dict[str, Any]:
    command = resolve_abaqus_command(abaqus_command)
    script = Path(script_path)
    if command is None:
        return {"status": "missing", "message": "Abaqus command not found. Set ABAQUS_COMMAND."}
    if not script.exists():
        return {"status": "missing", "message": f"script not found: {script}"}
    return run_process(
        command=command,
        args=["cae", f"noGUI={script}"],
        run_dir=run_dir,
        log_name="abaqus_no_gui.log",
        timeout_sec=timeout_sec,
    )


def abaqus_submit_inp(
    input_path: str,
    run_dir: str,
    job_name: str,
    abaqus_command: str | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    command = resolve_abaqus_command(abaqus_command)
    inp = Path(input_path)
    if command is None:
        return {"status": "missing", "message": "Abaqus command not found. Set ABAQUS_COMMAND."}
    if not inp.exists():
        return {"status": "missing", "message": f"input deck not found: {inp}"}
    return run_process(
        command=command,
        args=[f"job={job_name}", f"input={inp}", "interactive"],
        run_dir=run_dir,
        log_name=f"abaqus_{job_name}.log",
        timeout_sec=timeout_sec,
        cwd=Path(run_dir) / "outputs",
    )
