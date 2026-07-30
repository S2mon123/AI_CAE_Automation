from __future__ import annotations

from typing import Any

from ai_cae_lab.adapters.lammps import lammps_check_install, lammps_run_input


def check_lammps_installation(lammps_exe: str | None = None) -> dict[str, Any]:
    return lammps_check_install(lammps_exe)


def run_lammps_input(
    input_path: str,
    run_dir: str,
    lammps_exe: str | None = None,
    extra_args: list[str] | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    return lammps_run_input(input_path, run_dir, lammps_exe, extra_args, timeout_sec)
