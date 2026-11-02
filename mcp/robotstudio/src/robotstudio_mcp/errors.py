from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RobotStudioMcpError(Exception):
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    retryable: bool = False

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "retryable": self.retryable,
        }


def require(condition: bool, code: str, message: str, **details: Any) -> None:
    if not condition:
        raise RobotStudioMcpError(code, message, details)
