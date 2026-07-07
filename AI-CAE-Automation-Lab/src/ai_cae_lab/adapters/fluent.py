from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from .common import run_process


def _fluent_candidates_from_root(root: str | None) -> list[Path]:
    if not root:
        return []
    base = Path(root)
    if not base.exists():
        return []
    patterns = [
        "v*/fluent/ntbin/win64/fluent.exe",
        "v*/fluent/bin/fluent",
        "fluent/ntbin/win64/fluent.exe",
        "fluent/bin/fluent",
    ]
    hits: list[Path] = []
    for pattern in patterns:
        hits.extend(sorted(base.glob(pattern)))
    return hits


def resolve_fluent_command(fluent_command: str | None = None) -> str | None:
    candidates: list[str | Path | None] = [
        fluent_command,
        os.environ.get("FLUENT_EXE"),
        shutil.which("fluent"),
        *_fluent_candidates_from_root(os.environ.get("FLUENT_ROOT")),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
        if candidate and shutil.which(str(candidate)):
            return str(shutil.which(str(candidate)))
    return None


def fluent_run_journal(
    journal_path: str,
    run_dir: str,
    fluent_command: str | None = None,
    dimension: str = "3ddp",
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    command = resolve_fluent_command(fluent_command)
    journal = Path(journal_path)
    if command is None:
        return {"status": "missing", "message": "Fluent command not found. Set FLUENT_EXE or FLUENT_ROOT."}
    if not journal.exists():
        return {"status": "missing", "message": f"journal not found: {journal}"}
    return run_process(
        command=command,
        args=[dimension, "-g", "-i", str(journal)],
        run_dir=run_dir,
        log_name="fluent_journal.log",
        timeout_sec=timeout_sec,
    )
