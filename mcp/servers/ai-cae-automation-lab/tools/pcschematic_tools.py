from __future__ import annotations

from typing import Any

from ai_cae_lab.adapters.pcschematic import pcschematic_check_install


def check_pcschematic_installation(exe_path: str | None = None, root_path: str | None = None, tlb_path: str | None = None) -> dict[str, Any]:
    return pcschematic_check_install(exe_path, root_path, tlb_path)
