from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .common import run_process


def _first_existing(paths: list[str | Path | None]) -> str | None:
    for value in paths:
        if value and Path(value).exists():
            return str(Path(value))
    return None


def _ansys_root_candidates(root: str | None) -> list[Path]:
    if not root:
        return []
    base = Path(root)
    if not base.exists():
        return []
    return sorted(base.glob("v*"))


def resolve_workbench_command(workbench_command: str | None = None) -> str | None:
    root = os.environ.get("ANSYS_ROOT")
    version_roots = _ansys_root_candidates(root)
    candidates: list[str | Path | None] = [
        workbench_command,
        os.environ.get("WORKBENCH_EXE"),
        os.environ.get("ANSYS_WORKBENCH_EXE"),
        *[item / "Framework" / "bin" / "Win64" / "RunWB2.exe" for item in version_roots],
    ]
    return _first_existing(candidates)


def ansys_check_install(
    ansys_root: str | None = None,
    fluent_exe: str | None = None,
    workbench_exe: str | None = None,
) -> dict[str, Any]:
    root = ansys_root or os.environ.get("ANSYS_ROOT") or os.environ.get("FLUENT_ROOT")
    fluent = fluent_exe or os.environ.get("FLUENT_EXE")
    workbench = resolve_workbench_command(workbench_exe)

    checks = {
        "ansys_root": {"path": root, "exists": bool(root and Path(root).exists())},
        "fluent_exe": {"path": fluent, "exists": bool(fluent and Path(fluent).exists())},
        "workbench_exe": {"path": workbench, "exists": bool(workbench and Path(workbench).exists())},
    }
    return {
        "status": "ok" if any(item["exists"] for item in checks.values()) else "missing",
        "checks": checks,
        "message": "This check does not launch Ansys products or modify projects.",
    }


def ansys_run_workbench_journal(
    journal_path: str,
    run_dir: str,
    workbench_command: str | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    command = resolve_workbench_command(workbench_command)
    journal = Path(journal_path)
    if command is None:
        return {"status": "missing", "message": "Workbench command not found. Set WORKBENCH_EXE or ANSYS_ROOT."}
    if not journal.exists():
        return {"status": "missing", "message": f"Workbench journal not found: {journal}"}
    return run_process(
        command=command,
        args=["-B", "-R", str(journal)],
        run_dir=run_dir,
        log_name="ansys_workbench_journal.log",
        timeout_sec=timeout_sec,
    )
