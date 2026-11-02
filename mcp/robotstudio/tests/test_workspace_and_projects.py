from __future__ import annotations

from pathlib import Path

import pytest

from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.policies.workspace import WorkspaceGuard
from robotstudio_mcp.projects.service import ProjectService


def test_workspace_rejects_traversal(tmp_path: Path) -> None:
    guard = WorkspaceGuard(tmp_path / "workspace")
    with pytest.raises(RobotStudioMcpError, match="escapes"):
        guard.resolve_inside("..", "outside.txt")


def test_project_manifest_import_inventory_and_checkpoint(tmp_path: Path) -> None:
    service = ProjectService(tmp_path / "workspace")
    created = service.create("IRB120 Inspection")
    project_id = created["manifest"]["project_id"]
    assert created["manifest"]["controller_scope"] == "virtual_only"

    source = tmp_path / "sample.mod"
    source.write_text("MODULE Sample\nENDMODULE\n", encoding="utf-8")
    imported = service.import_file(project_id, source, "rapid")
    assert imported["relative_path"] == "input/rapid/sample.mod"
    assert len(imported["sha256"]) == 64

    with pytest.raises(RobotStudioMcpError, match="overwrite=true"):
        service.import_file(project_id, source, "rapid")

    inventory = service.inventory(project_id)
    assert {item["relative_path"] for item in inventory} >= {"manifest.json", "input/rapid/sample.mod"}
    checkpoint = service.checkpoint(project_id, "before inspection")
    assert checkpoint["rollback_available"] is False
    assert service.summary(project_id)["last_checkpoint"] == checkpoint["checkpoint_id"]


def test_project_id_cannot_be_a_path(tmp_path: Path) -> None:
    service = ProjectService(tmp_path / "workspace")
    with pytest.raises(RobotStudioMcpError, match="invalid format"):
        service.summary("../outside")
