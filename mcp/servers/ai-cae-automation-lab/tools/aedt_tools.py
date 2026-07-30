from __future__ import annotations

from typing import Any

from ai_cae_lab.adapters.aedt import aedt_check_install, aedt_run_pyaedt_script


def check_aedt_installation(aedt_exe: str | None = None, python_exe: str | None = None) -> dict[str, Any]:
    return aedt_check_install(aedt_exe, python_exe)


def run_pyaedt_script(
    script_path: str,
    run_dir: str,
    python_exe: str | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    return aedt_run_pyaedt_script(script_path, run_dir, python_exe, timeout_sec)
