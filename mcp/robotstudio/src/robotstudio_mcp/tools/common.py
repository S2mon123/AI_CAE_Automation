from __future__ import annotations

from typing import Any

from robotstudio_mcp.app import AppContext
from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.result_models import OperationTimer, failure, success


def finish_success(
    app: AppContext,
    operation: str,
    result: Any,
    *,
    timer: OperationTimer,
    scope: str,
    side_effect: str = "none",
    project_id: str | None = None,
    warnings: list[str] | None = None,
    evidence: list[Any] | None = None,
) -> dict[str, Any]:
    value = success(
        operation,
        result,
        timer=timer,
        scope=scope,
        side_effect=side_effect,
        project_id=project_id,
        warnings=warnings,
        evidence=evidence,
    )
    app.audit.write(
        "tool_call",
        operation=operation,
        request_id=timer.request_id,
        ok=True,
        side_effect=side_effect,
        summary={"project_id": project_id},
    )
    return value


def finish_failure(
    app: AppContext,
    operation: str,
    error: RobotStudioMcpError,
    *,
    timer: OperationTimer,
    scope: str,
    side_effect: str = "none",
    project_id: str | None = None,
) -> dict[str, Any]:
    value = failure(
        operation,
        error,
        timer=timer,
        scope=scope,
        side_effect=side_effect,
        project_id=project_id,
    )
    app.audit.write(
        "tool_call",
        operation=operation,
        request_id=timer.request_id,
        ok=False,
        side_effect=side_effect,
        summary={"project_id": project_id, "error_code": error.code},
    )
    return value


def bridge_operation(
    app: AppContext,
    operation: str,
    method: str,
    params: dict[str, Any] | None = None,
    *,
    scope: str,
    side_effect: str = "none",
) -> dict[str, Any]:
    timer = OperationTimer()
    try:
        response = app.bridge.call(method, params)
        timer.request_id = str(response.get("request_id") or timer.request_id)
        return finish_success(
            app,
            operation,
            response.get("result"),
            timer=timer,
            scope=scope,
            side_effect=side_effect,
            warnings=response.get("warnings") if isinstance(response.get("warnings"), list) else None,
            evidence=response.get("evidence") if isinstance(response.get("evidence"), list) else None,
        )
    except RobotStudioMcpError as exc:
        return finish_failure(
            app,
            operation,
            exc,
            timer=timer,
            scope=scope,
            side_effect=side_effect,
        )


def pagination(offset: int, limit: int) -> tuple[int, int]:
    if offset < 0:
        raise RobotStudioMcpError("RS_INVALID_ARGUMENT", "offset must be non-negative.")
    if limit < 1 or limit > 1000:
        raise RobotStudioMcpError("RS_INVALID_ARGUMENT", "limit must be between 1 and 1000.")
    return offset, limit
