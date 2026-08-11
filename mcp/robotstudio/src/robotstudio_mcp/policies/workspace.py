from __future__ import annotations

from pathlib import Path

from robotstudio_mcp.errors import RobotStudioMcpError


class WorkspaceGuard:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve(strict=False)

    def resolve_inside(self, *parts: str | Path, must_exist: bool = False) -> Path:
        candidate = self.root.joinpath(*parts).resolve(strict=False)
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise RobotStudioMcpError(
                "RS_PATH_OUTSIDE_WORKSPACE",
                "Resolved path escapes the configured RobotStudio MCP workspace.",
                {"path": str(candidate)},
            ) from exc
        if must_exist and not candidate.exists():
            raise RobotStudioMcpError("RS_ENTITY_NOT_FOUND", "Workspace path does not exist.", {"path": str(candidate)})
        return candidate

    def validate_external_import(self, source: Path) -> Path:
        candidate = source.expanduser().resolve(strict=True)
        if not candidate.is_file():
            raise RobotStudioMcpError("RS_ENTITY_NOT_FOUND", "Import source must be an existing file.")
        return candidate
