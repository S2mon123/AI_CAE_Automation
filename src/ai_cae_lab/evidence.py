from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .logs import analyze_log_file
from .runs import load_run, utc_now, write_json


HASH_SIZE_LIMIT = 64 * 1024 * 1024


@dataclass
class EvidenceItem:
    path: str
    kind: str
    size_bytes: int
    sha256: str | None


SOLVER_OUTPUT_EXTENSIONS = {
    ".odb",
    ".sim",
    ".cas",
    ".dat",
    ".res",
    ".rfl",
    ".mph",
    ".wbpj",
    ".mechdat",
    ".pro",
}
INPUT_EXTENSIONS = {
    ".inp",
    ".cdb",
    ".msh",
    ".geo",
    ".step",
    ".stp",
    ".iges",
    ".igs",
    ".sat",
}
SCRIPT_EXTENSIONS = {".py", ".java", ".m", ".jou", ".jnl", ".mac", ".bas", ".pas", ".c", ".cpp", ".h", ".udf"}
LOG_EXTENSIONS = {".log", ".sta", ".msg", ".err", ".out", ".txt"}
TABLE_EXTENSIONS = {".csv", ".tsv", ".xlsx", ".xls"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".gif", ".bmp", ".tif", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".webm"}
REPORT_EXTENSIONS = {".md", ".pdf", ".docx", ".html"}


def sha256_file(path: Path) -> str | None:
    if path.stat().st_size > HASH_SIZE_LIMIT:
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify_file(path: Path) -> str:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if name == "run.json":
        return "run_metadata"
    if name == "run.log":
        return "run_metadata"
    if name == "evidence.json":
        return "evidence_metadata"
    if name == "report.md":
        return "report"
    if suffix in LOG_EXTENSIONS:
        return "log"
    if suffix in SOLVER_OUTPUT_EXTENSIONS:
        return "solver_output"
    if suffix in INPUT_EXTENSIONS:
        return "input"
    if suffix in SCRIPT_EXTENSIONS:
        return "script"
    if suffix in TABLE_EXTENSIONS or (suffix == ".json" and name not in {"run.json", "evidence.json"}):
        return "structured_data"
    if suffix in IMAGE_EXTENSIONS:
        return "visual"
    if suffix in VIDEO_EXTENSIONS:
        return "visual"
    if suffix in REPORT_EXTENSIONS:
        return "report"
    return "unknown"


def credibility_grade(kinds: set[str], execution_status: str = "unknown") -> tuple[str, list[str]]:
    has_log = "log" in kinds
    has_input = bool(kinds & {"input", "script"})
    has_output = "solver_output" in kinds
    has_data = "structured_data" in kinds
    has_visual = "visual" in kinds
    has_report = "report" in kinds

    missing: list[str] = []
    if execution_status in {"failed", "license_error"}:
        missing.append("successful solver log without failure or license signals")
        return "failed-run", missing
    if not has_log:
        missing.append("solver or automation log")
    if not has_input:
        missing.append("input deck, journal, script, or command source")
    if not has_output:
        missing.append("solver output or project artifact")
    if not has_data:
        missing.append("numeric CSV/JSON/XLSX export")
    if not has_visual:
        missing.append("visual evidence image or video")
    if not has_report:
        missing.append("review report")

    if execution_status == "success" and has_output and has_data and has_visual and has_report:
        return "report-grade", missing
    if execution_status == "success" and has_output and (has_data or has_visual):
        return "engineering-draft", missing
    if has_log and has_visual:
        return "visual-validation", missing
    if has_log and (has_input or has_output):
        return "functional-validation", missing
    return "dry-run", missing


def summarize_log_status(logs: list[dict[str, Any]]) -> str:
    statuses = {item["status"] for item in logs}
    if "license_error" in statuses:
        return "license_error"
    if "failed" in statuses:
        return "failed"
    if "success" in statuses:
        return "success"
    return "unknown"


def scan_evidence(run_dir: str | Path, write: bool = True) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise FileNotFoundError(f"run directory does not exist: {root}")

    run = load_run(root)
    items: list[EvidenceItem] = []
    log_analysis: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            kind = classify_file(path)
            items.append(
                EvidenceItem(
                    path=relative,
                    kind=kind,
                    size_bytes=path.stat().st_size,
                    sha256=sha256_file(path),
                )
            )
            if kind == "log":
                parsed = analyze_log_file(path)
                parsed["path"] = relative
                log_analysis.append(parsed)

    kinds = {item.kind for item in items}
    execution_status = summarize_log_status(log_analysis)
    grade, missing = credibility_grade(kinds, execution_status)
    counts: dict[str, int] = {}
    for item in items:
        counts[item.kind] = counts.get(item.kind, 0) + 1

    payload = {
        "schema_version": "0.2",
        "scanned_at": utc_now(),
        "run_id": run["run_id"],
        "run_dir": str(root),
        "execution_status": execution_status,
        "credibility_grade": grade,
        "missing_for_next_grade": missing,
        "counts": counts,
        "log_analysis": log_analysis,
        "items": [asdict(item) for item in items],
    }
    if write:
        write_json(root / "evidence.json", payload)
    return payload
