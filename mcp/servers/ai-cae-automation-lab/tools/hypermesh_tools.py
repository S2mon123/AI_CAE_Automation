from __future__ import annotations

from typing import Any

from ai_cae_lab.adapters.hypermesh import hypermesh_check_install, hypermesh_run_tcl


def check_hypermesh_installation(batch_exe: str | None = None) -> dict[str, Any]:
    return hypermesh_check_install(batch_exe)


def run_hypermesh_tcl(
    script_path: str,
    run_dir: str,
    batch_exe: str | None = None,
    timeout_sec: int = 3600,
) -> dict[str, Any]:
    return hypermesh_run_tcl(script_path, run_dir, batch_exe, timeout_sec)
