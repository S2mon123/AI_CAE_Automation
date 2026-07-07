from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def as_command(command: str, args: list[str]) -> list[str]:
    path = Path(command)
    if path.suffix.lower() in {".bat", ".cmd"}:
        return ["cmd.exe", "/c", command, *args]
    return [command, *args]


def ensure_run_dirs(run_dir: str | Path) -> Path:
    root = Path(run_dir)
    (root / "logs").mkdir(parents=True, exist_ok=True)
    (root / "outputs").mkdir(parents=True, exist_ok=True)
    (root / "exports").mkdir(parents=True, exist_ok=True)
    return root


def run_process(
    command: str,
    args: list[str],
    run_dir: str | Path,
    log_name: str,
    timeout_sec: int,
    cwd: str | Path | None = None,
) -> dict[str, Any]:
    root = ensure_run_dirs(run_dir)
    log_path = root / "logs" / log_name
    argv = as_command(command, args)
    workdir = Path(cwd) if cwd else root

    try:
        result = subprocess.run(
            argv,
            cwd=str(workdir),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        log_path.write_text(
            "COMMAND:\n"
            + " ".join(argv)
            + "\n\nSTDOUT:\n"
            + result.stdout
            + "\n\nSTDERR:\n"
            + result.stderr,
            encoding="utf-8",
        )
        return {
            "status": "completed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "command": argv,
            "cwd": str(workdir),
            "log_path": str(log_path),
        }
    except subprocess.TimeoutExpired as exc:
        log_path.write_text(
            "COMMAND:\n"
            + " ".join(argv)
            + f"\n\nTIMEOUT after {timeout_sec} seconds\n"
            + (exc.stdout or "")
            + "\n"
            + (exc.stderr or ""),
            encoding="utf-8",
        )
        return {
            "status": "timeout",
            "returncode": None,
            "command": argv,
            "cwd": str(workdir),
            "log_path": str(log_path),
            "timeout_sec": timeout_sec,
        }
