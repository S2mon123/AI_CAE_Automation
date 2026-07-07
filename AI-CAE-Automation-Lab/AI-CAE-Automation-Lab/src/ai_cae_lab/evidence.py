from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

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
SCRIPT_EXTENSIONS = {".py", ".jou", ".jnl", ".mac", ".bas", ".pas", ".c", ".cpp", ".h", ".udf"}
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


def credibility_grade(kinds: set[str]) -> tuple[str, list[str]]:
    has_log = "log" in kinds
    has_input = bool(kinds & {"input", "script"})
    has_output = "solver_output" in kinds
    has_data = "structured_data" in kinds
    has_visual = "visual" in kinds
    has_report = "report" in kinds

    missing: list[str] = []
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

    if has_log and has_output and has_data and has_visual and has_report:
        return "report-grade", missing
    if has_log and has_output and (has_data or has_visual):
        return "engineering-draft", missing
    if has_log and has_visual:
        return "visual-validation", missing
    if has_log and (has_input or has_output):
        return "functional-validation", missing
    return "dry-run", missing


def scan_evidence(run_dir: str | Path, write: bool = True) -> dict[str, Any]:
    root = Path(run_dir)
    if not root.exists():
        raise FileNotFoundError(f"run directory does not exist: {root}")

    run = load_run(root)
    items: list[EvidenceItem] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            items.append(
                EvidenceItem(
                    path=relative,
                    kind=classify_file(path),
                    size_bytes=path.stat().st_size,
                    sha256=sha256_file(path),
                )
            )

    kinds = {item.kind for item in items}
    grade, missing = credibility_grade(kinds)
    counts: dict[str, int] = {}
    for item in items:
        counts[item.kind] = counts.get(item.kind, 0) + 1

    payload = {
        "schema_version": "0.1",
        "scanned_at": utc_now(),
        "run_id": run["run_id"],
        "run_dir": str(root),
        "credibility_grade": grade,
        "missing_for_next_grade": missing,
        "counts": counts,
        "items": [asdict(item) for item in items],
    }
    if write:
        write_json(root / "evidence.json", payload)
    return payload
