"""Tool-group wrappers for the AI CAE Automation Lab MCP bridge."""

from .bridge_tools import bridge_plan, context_scope, toolchain_paths
from .discovery_tools import discover_toolchains, setup_local_toolchain
from .evidence_tools import generate_run_report, scan_run_evidence
from .run_tools import create_run_record, write_solver_smoke_template

__all__ = [
    "bridge_plan",
    "context_scope",
    "toolchain_paths",
    "discover_toolchains",
    "setup_local_toolchain",
    "generate_run_report",
    "scan_run_evidence",
    "create_run_record",
    "write_solver_smoke_template",
]
