from __future__ import annotations

from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from robotstudio_mcp.app import AppContext
from robotstudio_mcp.bridge.contracts import capability_document
from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.policies.safety import safety_policy
from robotstudio_mcp.result_models import OperationTimer
from robotstudio_mcp.tools.common import finish_failure, finish_success


def register_environment_tools(mcp: FastMCP, app: AppContext) -> None:
    @mcp.tool(name="get_environment")
    def get_environment() -> dict[str, Any]:
        """Detect the local RobotStudio 2025 installation, matching SDK assemblies, Python, and workspace."""
        timer = OperationTimer()
        result = app.environment.inspect()
        result["workspace"] = str(app.settings.workspace)
        result["bridge_endpoint"] = f"{app.settings.bridge_host}:{app.settings.bridge_port}"
        result["controller_scope"] = app.settings.controller_scope
        result["bridge_token_present"] = app.settings.token_file.is_file()
        return finish_success(app, "get_environment", result, timer=timer, scope="environment")

    @mcp.tool(name="configure_robotstudio_installation")
    def configure_robotstudio_installation(path: str) -> dict[str, Any]:
        """Select an absolute RobotStudio 2025 installation directory for this MCP process only."""
        timer = OperationTimer()
        try:
            candidate = Path(path).expanduser().resolve(strict=True)
            if not (candidate / "Bin" / "RobotStudio.exe").is_file():
                raise RobotStudioMcpError(
                    "RS_ENV_NOT_FOUND",
                    "The selected directory does not contain Bin/RobotStudio.exe.",
                    {"path": str(candidate)},
                )
            app.configure_installation(candidate)
            compatibility = app.environment.compatibility()
            if not compatibility["compatible"]:
                raise RobotStudioMcpError(
                    "RS_VERSION_MISMATCH",
                    "The selected installation does not match the audited RobotStudio 2025.3 SDK.",
                    compatibility,
                )
            return finish_success(
                app,
                "configure_robotstudio_installation",
                {"path": str(candidate), "compatibility": compatibility, "persistence": "current_process_only"},
                timer=timer,
                scope="environment",
                side_effect="process_configuration",
            )
        except (OSError, RobotStudioMcpError) as exc:
            error = exc if isinstance(exc, RobotStudioMcpError) else RobotStudioMcpError("RS_ENV_NOT_FOUND", str(exc))
            return finish_failure(
                app,
                "configure_robotstudio_installation",
                error,
                timer=timer,
                scope="environment",
                side_effect="process_configuration",
            )

    @mcp.tool(name="get_bridge_status")
    def get_bridge_status() -> dict[str, Any]:
        """Check whether the authenticated in-process RobotStudio Add-In bridge is live."""
        timer = OperationTimer()
        status = app.bridge.status()
        return finish_success(app, "get_bridge_status", status, timer=timer, scope="bridge")

    @mcp.tool(name="get_live_capabilities")
    def get_live_capabilities() -> dict[str, Any]:
        """Return declared Phase 0/1 capabilities and, when online, the Add-In's actual method registry."""
        timer = OperationTimer()
        declared = capability_document()
        try:
            live = app.bridge.call("capabilities.get")
            declared["bridge_online"] = True
            declared["live"] = live.get("result")
        except RobotStudioMcpError as exc:
            declared["bridge_online"] = False
            declared["live"] = None
            declared["bridge_error"] = exc.as_dict()
        return finish_success(app, "get_live_capabilities", declared, timer=timer, scope="bridge")

    @mcp.tool(name="get_safety_policy")
    def get_safety_policy() -> dict[str, Any]:
        """Return the enforced read-only, virtual-controller-only safety policy."""
        timer = OperationTimer()
        return finish_success(app, "get_safety_policy", safety_policy(), timer=timer, scope="policy")

    @mcp.tool(name="get_version_compatibility")
    def get_version_compatibility() -> dict[str, Any]:
        """Compare RobotStudio.exe and SDK assembly versions against the audited 2025.3 target."""
        timer = OperationTimer()
        return finish_success(
            app,
            "get_version_compatibility",
            app.environment.compatibility(),
            timer=timer,
            scope="environment",
        )
