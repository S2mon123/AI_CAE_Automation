from __future__ import annotations

from typing import Any

from ai_cae_lab.runs import create_run
from ai_cae_lab.templates import write_solver_smoke_template as _write_solver_smoke_template


def create_run_record(
    solver: str,
    case_name: str,
    objective: str = "",
    root: str = "runs",
    tags_csv: str = "",
) -> dict[str, Any]:
    tags = [item.strip() for item in tags_csv.split(",") if item.strip()]
    return create_run(root=root, solver=solver, case_name=case_name, objective=objective, tags=tags)


def write_solver_smoke_template(
    solver: str,
    run_dir: str,
    case_name: str = "smoke-test",
    overwrite: bool = False,
) -> dict[str, Any]:
    return _write_solver_smoke_template(solver=solver, run_dir=run_dir, case_name=case_name, overwrite=overwrite)
