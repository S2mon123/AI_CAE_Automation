from __future__ import annotations

import hashlib
import json
import re
import secrets
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.policies.workspace import WorkspaceGuard

PROJECT_ID_RE = re.compile(r"^rs_[0-9]{8}_[a-f0-9]{8}$")
IMPORT_CATEGORIES = frozenset({"stations", "rapid", "geometry", "controller_backups"})
PROJECT_DIRS = (
    "input/stations",
    "input/rapid",
    "input/geometry",
    "input/controller_backups",
    "working",
    "checkpoints/project",
    "checkpoints/station",
    "checkpoints/rapid",
    "output/stations",
    "output/rapid",
    "output/screenshots",
    "output/reports",
    "output/evidence",
    "runs",
    "logs",
)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ProjectService:
    def __init__(self, workspace: Path) -> None:
        self.guard = WorkspaceGuard(workspace)
        self.projects_root = self.guard.resolve_inside("projects")
        self.projects_root.mkdir(parents=True, exist_ok=True)

    def _project_path(self, project_id: str) -> Path:
        if not PROJECT_ID_RE.fullmatch(project_id):
            raise RobotStudioMcpError("RS_PROJECT_ID_INVALID", "Project ID has an invalid format.")
        return self.guard.resolve_inside("projects", project_id)

    def _manifest_path(self, project_id: str) -> Path:
        path = self._project_path(project_id) / "manifest.json"
        if not path.is_file():
            raise RobotStudioMcpError("RS_ENTITY_NOT_FOUND", "RobotStudio MCP project does not exist.")
        return path

    def create(self, name: str) -> dict[str, Any]:
        clean_name = name.strip()
        if not clean_name or len(clean_name) > 120 or any(ord(char) < 32 for char in clean_name):
            raise RobotStudioMcpError(
                "RS_PROJECT_NAME_INVALID", "Project name must contain 1-120 printable characters."
            )
        project_id = f"rs_{datetime.now(UTC):%Y%m%d}_{secrets.token_hex(4)}"
        root = self._project_path(project_id)
        root.mkdir(parents=True, exist_ok=False)
        for relative in PROJECT_DIRS:
            (root / relative).mkdir(parents=True, exist_ok=True)
        manifest = {
            "project_id": project_id,
            "name": clean_name,
            "created_at": _utc_now(),
            "updated_at": _utc_now(),
            "robotstudio_version": None,
            "robotware_version": None,
            "controller_scope": "virtual_only",
            "active_station": None,
            "artifacts": [],
            "jobs": [],
            "last_checkpoint": None,
        }
        _atomic_json(root / "manifest.json", manifest)
        return {"manifest": manifest, "project_root": str(root)}

    def summary(self, project_id: str) -> dict[str, Any]:
        try:
            value = json.loads(self._manifest_path(project_id).read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RobotStudioMcpError("RS_PROJECT_MANIFEST_INVALID", "Project manifest is not valid JSON.") from exc
        return value

    def import_file(self, project_id: str, source: Path, category: str, overwrite: bool = False) -> dict[str, Any]:
        if category not in IMPORT_CATEGORIES:
            raise RobotStudioMcpError(
                "RS_IMPORT_CATEGORY_INVALID",
                "Import category is not allowed.",
                {"allowed": sorted(IMPORT_CATEGORIES)},
            )
        source = self.guard.validate_external_import(source)
        destination = self._project_path(project_id) / "input" / category / source.name
        destination = destination.resolve(strict=False)
        if destination.exists() and not overwrite:
            raise RobotStudioMcpError(
                "RS_FILE_EXISTS",
                "Destination exists; set overwrite=true only after explicit user approval.",
                {"destination": str(destination)},
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return {
            "relative_path": destination.relative_to(self._project_path(project_id)).as_posix(),
            "size": destination.stat().st_size,
            "sha256": _sha256(destination),
        }

    def inventory(self, project_id: str) -> list[dict[str, Any]]:
        root = self._project_path(project_id)
        self._manifest_path(project_id)
        files: list[dict[str, Any]] = []
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            if path.name.endswith(".tmp"):
                continue
            files.append(
                {
                    "relative_path": path.relative_to(root).as_posix(),
                    "size": path.stat().st_size,
                    "sha256": _sha256(path),
                    "modified_utc": datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat(),
                }
            )
        return files

    def checkpoint(self, project_id: str, label: str | None = None) -> dict[str, Any]:
        root = self._project_path(project_id)
        manifest = self.summary(project_id)
        checkpoint_id = f"cp_{datetime.now(UTC):%Y%m%dT%H%M%SZ}_{secrets.token_hex(3)}"
        checkpoint_dir = root / "checkpoints" / "project" / checkpoint_id
        checkpoint_dir.mkdir(parents=True, exist_ok=False)
        record = {
            "checkpoint_id": checkpoint_id,
            "project_id": project_id,
            "label": label.strip()[:120] if label else None,
            "created_at": _utc_now(),
            "manifest": manifest,
            "inventory": self.inventory(project_id),
            "rollback_available": False,
            "note": (
                "Phase 0/1 project checkpoints are immutable evidence snapshots; automatic rollback is not exposed."
            ),
        }
        _atomic_json(checkpoint_dir / "checkpoint.json", record)
        manifest["last_checkpoint"] = checkpoint_id
        manifest["updated_at"] = _utc_now()
        _atomic_json(root / "manifest.json", manifest)
        return record

    def artifacts(self, project_id: str) -> list[dict[str, Any]]:
        self._manifest_path(project_id)
        return [item for item in self.inventory(project_id) if item["relative_path"].startswith("output/")]
