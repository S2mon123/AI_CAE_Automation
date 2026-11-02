from __future__ import annotations

import hashlib
import json
import re
import uuid
from pathlib import Path


class Store:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, relative: str) -> Path:
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root) or path == self.root:
            raise ValueError("WORKSPACE_PATH_ESCAPE")
        return path

    def read_bytes(self, relative: str, max_bytes: int = 8_388_608) -> bytes:
        path = self.path(relative)
        with path.open("rb") as handle:
            data = handle.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError("FILE_TOO_LARGE")
        return data

    def read(self, relative: str) -> dict:
        value = json.loads(self.read_bytes(relative).decode("utf-8-sig"))
        if not isinstance(value, dict):
            raise ValueError("JSON_OBJECT_REQUIRED")
        return value

    def write_new(self, relative: str, value: dict | str) -> dict:
        path = self.path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = (
            json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
            if isinstance(value, dict)
            else value
        ).encode("utf-8")
        # Exclusive creation protects pre-existing source, including AI_ modules.
        with path.open("xb") as handle:
            handle.write(data)
        return {"path": str(path), "relative_path": relative, "sha256": hashlib.sha256(data).hexdigest()}

    def task(self, task_id: str) -> dict:
        if not re.fullmatch("[a-f0-9]{32}", task_id):
            raise ValueError("INVALID_TASK_ID")
        return self.read(f"tasks/{task_id}/task.json")

    @staticmethod
    def new_id() -> str:
        return uuid.uuid4().hex
