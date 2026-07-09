from __future__ import annotations

from typing import Any

from ai_cae_lab.adapters.openfoam import openfoam_check_install, openfoam_run_command


def check_openfoam_installation(openfoam_root: str | None = None) -> dict[str, Any]:
    return openfoam_check_install(openfoam_root)


def run_openfoam_command(command_name: str, case_dir: str, run_dir: str, timeout_sec: int = 3600) -> dict[str, Any]:
    return openfoam_run_command(command_name, case_dir, run_dir, timeout_sec)
