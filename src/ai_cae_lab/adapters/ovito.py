from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from ..config import configured_solver_paths, load_toolbox_config
from .common import probe_python_import, run_process


def _resolve(candidates: list[str | Path | None]) -> str | None:
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
        if candidate and shutil.which(str(candidate)):
            return str(shutil.which(str(candidate)))
    return None


def resolve_ovito_gui(ovito_exe: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "ovito")
    return _resolve([ovito_exe, os.environ.get("OVITO_EXE"), configured.get("ovito_exe"), shutil.which("ovito")])


def resolve_ovito_script_command(command: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "ovito")
    return _resolve(
        [
            command,
            os.environ.get("OVITOS_EXE"),
            configured.get("script_command"),
            configured.get("ovitos_exe"),
            shutil.which("ovitos"),
            os.environ.get("OVITO_PYTHON"),
            configured.get("python"),
        ]
    )


def ovito_check_install(ovito_exe: str | None = None, script_command: str | None = None) -> dict[str, Any]:
    gui = resolve_ovito_gui(ovito_exe)
    script = resolve_ovito_script_command(script_command)
    import_probe = probe_python_import(script, "ovito") if script else None
    scripting_ok = bool(import_probe and import_probe["ok"])
    if scripting_ok:
        status = "ok"
    elif gui:
        status = "partial"
    else:
        status = "missing"
    return {
        "status": status,
        "checks": {
            "ovito_gui": {"path": gui, "exists": bool(gui)},
            "ovito_script_command": {
                "path": script,
                "exists": bool(script),
                "import_ok": scripting_ok,
            },
        },
        "capabilities": {
            "interactive_gui": bool(gui),
            "batch_python": scripting_ok,
        },
        "import_probe": import_probe,
        "message": (
            "OVITO Basic may provide only the GUI. Batch postprocessing then requires a compatible external Python "
            "environment with the OVITO package; do not claim ovitos availability from ovito.exe alone."
        ),
    }


def ovito_run_script(
    script_path: str,
    run_dir: str,
    script_command: str | None = None,
    timeout_sec: int = 3600,
) -> dict[str, Any]:
    command = resolve_ovito_script_command(script_command)
    script = Path(script_path)
    if command is None:
        return {"status": "missing", "message": "ovitos or OVITO Python not found."}
    if not script.exists():
        return {"status": "missing", "message": f"OVITO script not found: {script}"}
    return run_process(
        command=command,
        args=[str(script)],
        run_dir=run_dir,
        log_name="ovito_postprocess.log",
        timeout_sec=timeout_sec,
        cwd=script.parent,
    )
