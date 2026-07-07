from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"


@dataclass
class RunRecord:
    run_id: str
    created_at: str
    solver: str
    case_name: str
    objective: str
    status: str = "created"
    tags: list[str] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION
    directories: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def slugify(value: str, fallback: str = "case") -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower())
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-._")
    return normalized or fallback


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def create_run(
    root: str | Path,
    solver: str,
    case_name: str,
    objective: str = "",
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    created_at = utc_now()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    solver_slug = slugify(solver, fallback="solver")
    case_slug = slugify(case_name)
    run_id = f"{stamp}_{solver_slug}_{case_slug}"
    run_dir = Path(root) / run_id

    directories = {
        "inputs": "inputs",
        "outputs": "outputs",
        "logs": "logs",
        "scripts": "scripts",
        "exports": "exports",
    }
    for relative in directories.values():
        (run_dir / relative).mkdir(parents=True, exist_ok=True)

    record = RunRecord(
        run_id=run_id,
        created_at=created_at,
        solver=solver,
        case_name=case_name,
        objective=objective,
        tags=tags or [],
        directories=directories,
        metadata=metadata or {},
    )

    write_json(run_dir / "run.json", asdict(record))
    (run_dir / "run.log").write_text(
        f"[{created_at}] run created\n"
        f"solver={solver}\n"
        f"case_name={case_name}\n"
        f"objective={objective or 'not provided'}\n",
        encoding="utf-8",
    )

    payload = asdict(record)
    payload["run_dir"] = str(run_dir)
    payload["run_json"] = str(run_dir / "run.json")
    return payload


def load_run(run_dir: str | Path) -> dict[str, Any]:
    path = Path(run_dir) / "run.json"
    if not path.exists():
        raise FileNotFoundError(f"run.json not found in {Path(run_dir)}")
    payload = load_json(path)
    payload["run_dir"] = str(Path(run_dir))
    return payload
