from __future__ import annotations

from typing import Any

from ai_cae_lab.adapters.ansys import ansys_check_install, ansys_run_workbench_journal
from ai_cae_lab.adapters.fluent import fluent_run_journal


def check_ansys_installation(ansys_root: str | None = None, fluent_exe: str | None = None, workbench_exe: str | None = None) -> dict[str, Any]:
    return ansys_check_install(ansys_root, fluent_exe, workbench_exe)


def run_fluent_journal(journal_path: str, run_dir: str, fluent_command: str | None = None, dimension: str = "3ddp", timeout_sec: int = 7200) -> dict[str, Any]:
    return fluent_run_journal(journal_path, run_dir, fluent_command, dimension, timeout_sec)


def run_workbench_journal(journal_path: str, run_dir: str, workbench_command: str | None = None, timeout_sec: int = 7200) -> dict[str, Any]:
    return ansys_run_workbench_journal(journal_path, run_dir, workbench_command, timeout_sec)
