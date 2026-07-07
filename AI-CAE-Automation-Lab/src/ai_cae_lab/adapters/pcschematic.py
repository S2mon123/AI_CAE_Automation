from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def pcschematic_check_install(
    exe_path: str | None = None,
    root_path: str | None = None,
    tlb_path: str | None = None,
) -> dict[str, Any]:
    exe = exe_path or os.environ.get("PCSCHEMATIC_EXE")
    root = root_path or os.environ.get("PCSCHEMATIC_ROOT")
    tlb = tlb_path or os.environ.get("PCSCHEMATIC_TLB")

    checks = {
        "exe": {"path": exe, "exists": bool(exe and Path(exe).exists())},
        "root": {"path": root, "exists": bool(root and Path(root).exists())},
        "tlb": {"path": tlb, "exists": bool(tlb and Path(tlb).exists())},
    }
    status = "ok" if all(item["exists"] for item in checks.values()) else "incomplete"
    return {
        "status": status,
        "checks": checks,
        "message": "This check does not launch PCSCHEMATIC or modify installation files.",
    }
