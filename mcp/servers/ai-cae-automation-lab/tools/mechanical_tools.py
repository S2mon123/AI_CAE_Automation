from __future__ import annotations

from typing import Any

from ai_cae_lab.adapters.mechanical import (
    mechanical_check_install,
    mechanical_run_python_controller,
    mechanical_run_workbench_journal,
    mechanical_validate_result_summary,
)


def check_mechanical_installation(
    workbench_exe: str | None = None,
    python_exe: str | None = None,
) -> dict[str, Any]:
    return mechanical_check_install(workbench_exe, python_exe)


def run_mechanical_workbench_journal(
    journal_path: str,
    run_dir: str,
    workbench_exe: str | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    return mechanical_run_workbench_journal(journal_path, run_dir, workbench_exe, timeout_sec)


def run_pymechanical_controller(
    script_path: str,
    run_dir: str,
    python_exe: str | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    return mechanical_run_python_controller(script_path, run_dir, python_exe, timeout_sec)


def validate_mechanical_result_summary(
    summary_path: str,
    solve_log_path: str | None = None,
) -> dict[str, Any]:
    return mechanical_validate_result_summary(summary_path, solve_log_path)
