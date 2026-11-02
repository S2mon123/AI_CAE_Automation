from __future__ import annotations

from pathlib import Path

from robotstudio_mcp.audit import AuditLogger
from robotstudio_mcp.bridge.client import BridgeClient
from robotstudio_mcp.environment import EnvironmentProbe
from robotstudio_mcp.projects.service import ProjectService
from robotstudio_mcp.settings import Settings


class AppContext:
    def __init__(self, settings: Settings, bridge: BridgeClient | None = None) -> None:
        settings.ensure_workspace()
        self.settings = settings
        self.audit = AuditLogger(settings.workspace / "logs" / "server-audit.jsonl")
        self.environment = EnvironmentProbe(settings.installation_override)
        self.projects = ProjectService(settings.workspace)
        self.bridge = bridge or BridgeClient(settings, self.audit)

    def configure_installation(self, path: Path) -> None:
        self.environment.configure(path)
