from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ..config import configured_solver_paths, load_toolbox_config


def pcschematic_check_install(
    exe_path: str | None = None,
    root_path: str | None = None,
    tlb_path: str | None = None,
) -> dict[str, Any]:
    configured = configured_solver_paths(load_toolbox_config(), "pcschematic")
    exe = exe_path or os.environ.get("PCSCHEMATIC_EXE") or configured.get("exe")
    root = root_path or os.environ.get("PCSCHEMATIC_ROOT") or configured.get("root")
    tlb = tlb_path or os.environ.get("PCSCHEMATIC_TLB") or configured.get("tlb")

    checks = {
        "exe": {"path": exe, "exists": bool(exe and Path(exe).exists())},
        "root": {"path": root, "exists": bool(root and Path(root).exists())},
        "tlb": {"path": tlb, "exists": bool(tlb and Path(tlb).exists())},
    }
    status = "ok" if checks["exe"]["exists"] else ("partial" if any(item["exists"] for item in checks.values()) else "missing")
    return {
        "status": status,
        "checks": checks,
        "message": "This check does not launch PCSCHEMATIC or modify installation files.",
    }
