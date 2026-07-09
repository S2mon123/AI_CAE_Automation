from __future__ import annotations

from typing import Any

from ai_cae_lab.adapters.abaqus import abaqus_run_no_gui, abaqus_submit_inp, resolve_abaqus_command


def check_abaqus_command(abaqus_command: str | None = None) -> dict[str, Any]:
    command = resolve_abaqus_command(abaqus_command)
    return {"status": "ok" if command else "missing", "command": command}


def run_no_gui_script(script_path: str, run_dir: str, abaqus_command: str | None = None, timeout_sec: int = 3600) -> dict[str, Any]:
    return abaqus_run_no_gui(script_path, run_dir, abaqus_command, timeout_sec)


def submit_input_deck(input_path: str, run_dir: str, job_name: str, abaqus_command: str | None = None, timeout_sec: int = 7200) -> dict[str, Any]:
    return abaqus_submit_inp(input_path, run_dir, job_name, abaqus_command, timeout_sec)
