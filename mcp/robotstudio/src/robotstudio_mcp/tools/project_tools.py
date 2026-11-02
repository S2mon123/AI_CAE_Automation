from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP

from robotstudio_mcp.app import AppContext
from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.result_models import OperationTimer
from robotstudio_mcp.tools.common import finish_failure, finish_success

ImportCategory = Literal["stations", "rapid", "geometry", "controller_backups"]


def register_project_tools(mcp: FastMCP, app: AppContext) -> None:
    @mcp.tool(name="create_project")
    def create_project(name: str) -> dict[str, Any]:
        """Create an isolated project under the configured RobotStudio MCP workspace."""
        timer = OperationTimer()
        try:
            result = app.projects.create(name)
            project_id = result["manifest"]["project_id"]
            return finish_success(
                app,
                "create_project",
                result,
                timer=timer,
                scope="project",
                side_effect="filesystem_write",
                project_id=project_id,
            )
        except RobotStudioMcpError as exc:
            return finish_failure(
                app,
                "create_project",
                exc,
                timer=timer,
                scope="project",
                side_effect="filesystem_write",
            )

    @mcp.tool(name="get_project_summary")
    def get_project_summary(project_id: str) -> dict[str, Any]:
        """Read an isolated project's manifest."""
        timer = OperationTimer()
        try:
            return finish_success(
                app,
                "get_project_summary",
                app.projects.summary(project_id),
                timer=timer,
                scope="project",
                project_id=project_id,
            )
        except RobotStudioMcpError as exc:
            return finish_failure(app, "get_project_summary", exc, timer=timer, scope="project", project_id=project_id)

    @mcp.tool(name="import_project_file")
    def import_project_file(
        project_id: str,
        source_path: str,
        category: ImportCategory,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Copy one explicitly named external file into a project input category; never imports directories."""
        timer = OperationTimer()
        try:
            result = app.projects.import_file(project_id, Path(source_path), category, overwrite)
            return finish_success(
                app,
                "import_project_file",
                result,
                timer=timer,
                scope="project",
                side_effect="filesystem_write",
                project_id=project_id,
            )
        except (OSError, RobotStudioMcpError) as exc:
            error = (
                exc if isinstance(exc, RobotStudioMcpError) else RobotStudioMcpError("RS_FILE_IMPORT_FAILED", str(exc))
            )
            return finish_failure(
                app,
                "import_project_file",
                error,
                timer=timer,
                scope="project",
                side_effect="filesystem_write",
                project_id=project_id,
            )

    @mcp.tool(name="list_project_files")
    def list_project_files(project_id: str) -> dict[str, Any]:
        """List project files with relative paths, sizes, timestamps, and SHA-256 evidence."""
        timer = OperationTimer()
        try:
            return finish_success(
                app,
                "list_project_files",
                app.projects.inventory(project_id),
                timer=timer,
                scope="project",
                project_id=project_id,
            )
        except RobotStudioMcpError as exc:
            return finish_failure(app, "list_project_files", exc, timer=timer, scope="project", project_id=project_id)

    @mcp.tool(name="create_project_checkpoint")
    def create_project_checkpoint(project_id: str, label: str | None = None) -> dict[str, Any]:
        """Write an immutable manifest and file-hash checkpoint for project evidence."""
        timer = OperationTimer()
        try:
            record = app.projects.checkpoint(project_id, label)
            value = finish_success(
                app,
                "create_project_checkpoint",
                record,
                timer=timer,
                scope="project",
                side_effect="filesystem_write",
                project_id=project_id,
            )
            value["checkpoint"] = {
                "created": True,
                "id": record["checkpoint_id"],
                "rollback_available": False,
            }
            return value
        except RobotStudioMcpError as exc:
            return finish_failure(
                app,
                "create_project_checkpoint",
                exc,
                timer=timer,
                scope="project",
                side_effect="filesystem_write",
                project_id=project_id,
            )

    @mcp.tool(name="list_project_artifacts")
    def list_project_artifacts(project_id: str) -> dict[str, Any]:
        """List files below the project output directory with content hashes."""
        timer = OperationTimer()
        try:
            return finish_success(
                app,
                "list_project_artifacts",
                app.projects.artifacts(project_id),
                timer=timer,
                scope="project",
                project_id=project_id,
            )
        except RobotStudioMcpError as exc:
            return finish_failure(
                app, "list_project_artifacts", exc, timer=timer, scope="project", project_id=project_id
            )
