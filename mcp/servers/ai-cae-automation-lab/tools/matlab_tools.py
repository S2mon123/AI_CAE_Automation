from __future__ import annotations

from typing import Any

from ai_cae_lab.adapters.matlab import matlab_check_install, matlab_run_script


def check_matlab_installation(matlab_command: str | None = None, matlab_root: str | None = None) -> dict[str, Any]:
    return matlab_check_install(matlab_command, matlab_root)


def run_matlab_script(script_path: str, run_dir: str, matlab_command: str | None = None, timeout_sec: int = 3600) -> dict[str, Any]:
    return matlab_run_script(script_path, run_dir, matlab_command, timeout_sec)
