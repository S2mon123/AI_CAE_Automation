from __future__ import annotations

from typing import Any

from ai_cae_lab.config import bridge_plan as _bridge_plan, toolchain_paths as _toolchain_paths
from ai_cae_lab.context_scope import solver_context_scope


def context_scope(solver: str, include_common: bool = True) -> dict[str, Any]:
    return solver_context_scope(solver=solver, include_common=include_common)


def toolchain_paths(solver: str, config_path: str | None = None) -> dict[str, Any]:
    return _toolchain_paths(solver=solver, config_path=config_path)


def bridge_plan(solver: str, objective: str = "", config_path: str | None = None) -> dict[str, Any]:
    return _bridge_plan(solver=solver, objective=objective, config_path=config_path)
