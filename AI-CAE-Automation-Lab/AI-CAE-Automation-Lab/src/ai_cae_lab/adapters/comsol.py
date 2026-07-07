from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .common import run_process


def _comsol_roots(root: str | None) -> list[Path]:
    if not root:
        return []
    base = Path(root)
    if not base.exists():
        return []
    if (base / "Multiphysics").exists():
        return [base]
    return sorted(base.glob("COMSOL*"))


def resolve_comsol_batch(comsol_batch: str | None = None) -> str | None:
    root = os.environ.get("COMSOL_ROOT")
    roots = _comsol_roots(root)
    candidates: list[str | Path | None] = [
        comsol_batch,
        os.environ.get("COMSOL_BATCH"),
        os.environ.get("COMSOL_EXE"),
        *[item / "Multiphysics" / "bin" / "win64" / "comsolbatch.exe" for item in roots],
        *[item / "Multiphysics" / "bin" / "win64" / "comsol.exe" for item in roots],
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
    return None


def resolve_comsol_java(java_path: str | None = None) -> str | None:
    root = os.environ.get("COMSOL_ROOT")
    roots = _comsol_roots(root)
    candidates: list[str | Path | None] = [
        java_path,
        os.environ.get("COMSOL_JAVA"),
        *[item / "Multiphysics" / "java" / "win64" / "jre" / "bin" / "java.exe" for item in roots],
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
    return None


def comsol_check_install(
    comsol_root: str | None = None,
    comsol_batch: str | None = None,
    java_path: str | None = None,
) -> dict[str, Any]:
    root = comsol_root or os.environ.get("COMSOL_ROOT")
    batch = resolve_comsol_batch(comsol_batch)
    java = resolve_comsol_java(java_path)
    docs_root = Path(root) / "Multiphysics" / "doc" if root else None
    api_index = (
        Path(root)
        / "Multiphysics"
        / "doc"
        / "help"
        / "wtpwebapps"
        / "ROOT"
        / "doc"
        / "com.comsol.help.comsol"
        / "api"
        / "index.html"
        if root
        else None
    )
    checks = {
        "comsol_root": {"path": root, "exists": bool(root and Path(root).exists())},
        "comsol_batch": {"path": batch, "exists": bool(batch and Path(batch).exists())},
        "comsol_java": {"path": java, "exists": bool(java and Path(java).exists())},
        "docs_root": {"path": str(docs_root) if docs_root else None, "exists": bool(docs_root and docs_root.exists())},
        "api_index": {"path": str(api_index) if api_index else None, "exists": bool(api_index and api_index.exists())},
    }
    return {
        "status": "ok" if checks["comsol_batch"]["exists"] or checks["comsol_java"]["exists"] else "missing",
        "checks": checks,
        "message": "This check does not launch COMSOL or modify models.",
    }


def comsol_run_batch(
    run_dir: str,
    input_file: str | None = None,
    output_file: str | None = None,
    comsol_batch: str | None = None,
    extra_args: list[str] | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    command = resolve_comsol_batch(comsol_batch)
    if command is None:
        return {"status": "missing", "message": "COMSOL batch command not found. Set COMSOL_BATCH or COMSOL_ROOT."}
    args: list[str] = []
    if input_file:
        path = Path(input_file)
        if not path.exists():
            return {"status": "missing", "message": f"COMSOL input file not found: {path}"}
        args.extend(["-inputfile", str(path)])
    if output_file:
        args.extend(["-outputfile", output_file])
    if extra_args:
        args.extend(extra_args)
    return run_process(
        command=command,
        args=args,
        run_dir=run_dir,
        log_name="comsol_batch.log",
        timeout_sec=timeout_sec,
    )
