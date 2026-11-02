from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class AuditLogger:
    def __init__(self, log_path: Path) -> None:
        self._log_path = log_path
        self._lock = threading.Lock()

    def write(
        self,
        event: str,
        *,
        operation: str | None = None,
        request_id: str | None = None,
        ok: bool | None = None,
        side_effect: str = "none",
        summary: dict[str, Any] | None = None,
    ) -> None:
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
            "operation": operation,
            "request_id": request_id,
            "ok": ok,
            "side_effect": side_effect,
            "summary": self._sanitize(summary or {}),
        }
        line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock, self._log_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(line + "\n")

    @classmethod
    def _sanitize(cls, value: Any) -> Any:
        if isinstance(value, dict):
            output: dict[str, Any] = {}
            for key, item in value.items():
                if any(secret in key.lower() for secret in ("token", "password", "secret", "credential")):
                    output[key] = "<redacted>"
                else:
                    output[key] = cls._sanitize(item)
            return output
        if isinstance(value, (list, tuple)):
            return [cls._sanitize(item) for item in value]
        if isinstance(value, Path):
            return str(value)
        return value
