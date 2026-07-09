from __future__ import annotations

import queue
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from ..runs import update_run_status


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


def _safe_update_run_status(run_dir: Path, status: str, message: str, metadata: dict[str, Any] | None = None) -> None:
    if not (run_dir / "run.json").exists():
        return
    try:
        update_run_status(run_dir, status, message=message, metadata=metadata)
    except Exception:
        # Process logging should not fail just because run metadata is malformed.
        return


def _reader_thread(stream: Any, output: "queue.Queue[str]") -> None:
    try:
        for line in iter(stream.readline, ""):
            output.put(line)
    finally:
        try:
            stream.close()
        except Exception:
            pass


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
    start_time = time.monotonic()
    line_queue: queue.Queue[str] = queue.Queue()

    _safe_update_run_status(root, "submitted", f"command queued: {Path(command).name}")
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        log.write("COMMAND:\n" + " ".join(argv) + "\n")
        log.write("CWD:\n" + str(workdir) + "\n\nOUTPUT:\n")
        log.flush()

        try:
            process = subprocess.Popen(
                argv,
                cwd=str(workdir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            log.write(f"\nPROCESS_START_FAILED: {exc}\n")
            _safe_update_run_status(root, "failed", f"process start failed: {exc}")
            return {
                "status": "failed",
                "returncode": None,
                "command": argv,
                "cwd": str(workdir),
                "log_path": str(log_path),
                "message": str(exc),
            }

        _safe_update_run_status(root, "running", f"pid={process.pid}", metadata={"pid": process.pid})
        if process.stdout is not None:
            thread = threading.Thread(target=_reader_thread, args=(process.stdout, line_queue), daemon=True)
            thread.start()

        timed_out = False
        while True:
            while True:
                try:
                    log.write(line_queue.get_nowait())
                except queue.Empty:
                    break
            log.flush()

            returncode = process.poll()
            if returncode is not None:
                break

            if timeout_sec and (time.monotonic() - start_time) > timeout_sec:
                timed_out = True
                log.write(f"\nTIMEOUT after {timeout_sec} seconds\n")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
                break
            time.sleep(0.1)

        while True:
            try:
                log.write(line_queue.get_nowait())
            except queue.Empty:
                break
        returncode = process.poll()
        elapsed_sec = round(time.monotonic() - start_time, 3)
        log.write(f"\nRETURN_CODE: {returncode}\nELAPSED_SECONDS: {elapsed_sec}\n")

    if timed_out:
        _safe_update_run_status(root, "failed", f"timeout after {timeout_sec} seconds")
        return {
            "status": "timeout",
            "returncode": returncode,
            "command": argv,
            "cwd": str(workdir),
            "log_path": str(log_path),
            "timeout_sec": timeout_sec,
            "elapsed_sec": elapsed_sec,
        }

    status = "completed" if returncode == 0 else "failed"
    _safe_update_run_status(root, status, f"returncode={returncode}")
    return {
        "status": status,
        "returncode": returncode,
        "command": argv,
        "cwd": str(workdir),
        "log_path": str(log_path),
        "elapsed_sec": elapsed_sec,
    }
