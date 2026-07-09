from __future__ import annotations

from typing import Any

from ai_cae_lab.adapters.paraview import paraview_check_install, paraview_run_script


def check_paraview_installation(pvpython: str | None = None, paraview_root: str | None = None) -> dict[str, Any]:
    return paraview_check_install(pvpython, paraview_root)


def run_pvpython_script(script_path: str, run_dir: str, pvpython: str | None = None, timeout_sec: int = 3600) -> dict[str, Any]:
    return paraview_run_script(script_path, run_dir, pvpython, timeout_sec)
