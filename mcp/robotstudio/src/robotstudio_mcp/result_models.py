from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from robotstudio_mcp.errors import RobotStudioMcpError


@dataclass(slots=True)
class OperationTimer:
    started: float = field(default_factory=time.perf_counter)
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @property
    def elapsed_ms(self) -> int:
        return max(0, round((time.perf_counter() - self.started) * 1000))


def success(
    operation: str,
    result: Any,
    *,
    scope: str = "server",
    side_effect: str = "none",
    timer: OperationTimer | None = None,
    project_id: str | None = None,
    warnings: list[str] | None = None,
    evidence: list[Any] | None = None,
) -> dict[str, Any]:
    timer = timer or OperationTimer()
    return {
        "ok": True,
        "operation": operation,
        "scope": scope,
        "side_effect": side_effect,
        "project_id": project_id,
        "request_id": timer.request_id,
        "result": result,
        "warnings": warnings or [],
        "checkpoint": None,
        "evidence": evidence or [],
        "elapsed_ms": timer.elapsed_ms,
    }


def failure(
    operation: str,
    error: RobotStudioMcpError,
    *,
    scope: str = "server",
    side_effect: str = "none",
    timer: OperationTimer | None = None,
    project_id: str | None = None,
    warnings: list[str] | None = None,
    evidence: list[Any] | None = None,
) -> dict[str, Any]:
    timer = timer or OperationTimer()
    return {
        "ok": False,
        "operation": operation,
        "scope": scope,
        "side_effect": side_effect,
        "project_id": project_id,
        "request_id": timer.request_id,
        "result": None,
        "error": error.as_dict(),
        "warnings": warnings or [],
        "checkpoint": None,
        "evidence": evidence or [],
        "elapsed_ms": timer.elapsed_ms,
    }
