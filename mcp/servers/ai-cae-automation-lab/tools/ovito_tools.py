from __future__ import annotations

from typing import Any

from ai_cae_lab.adapters.ovito import ovito_check_install, ovito_run_script


def check_ovito_installation(
    ovito_exe: str | None = None,
    script_command: str | None = None,
) -> dict[str, Any]:
    return ovito_check_install(ovito_exe, script_command)


def run_ovito_script(
    script_path: str,
    run_dir: str,
    script_command: str | None = None,
    timeout_sec: int = 3600,
) -> dict[str, Any]:
    return ovito_run_script(script_path, run_dir, script_command, timeout_sec)
