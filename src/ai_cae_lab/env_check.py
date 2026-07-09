from __future__ import annotations

import argparse
import json
import os
import shutil
from dataclasses import asdict, dataclass
from typing import Any

from .adapters.openfoam import openfoam_check_install
from .adapters.paraview import paraview_check_install
from .discovery import discover_toolchains


@dataclass
class CheckResult:
    name: str
    status: str
    details: list[str]


def check_python() -> CheckResult:
    details = [
        f"python on PATH: {shutil.which('python') or 'not found'}",
        f"conda python: {os.environ.get('CONDA_PYTHON_EXE', 'not set')}",
    ]
    return CheckResult("python", "ok", details)


def check_command(name: str) -> CheckResult:
    found = shutil.which(name)
    if found:
        return CheckResult(name, "ok", [found])
    return CheckResult(name, "missing", [f"{name} not found on PATH"])


def _details_from_adapter(payload: dict[str, Any]) -> list[str]:
    details: list[str] = [payload.get("message", "")]
    checks = payload.get("checks", {})
    if isinstance(checks, dict):
        for key, item in checks.items():
            if isinstance(item, dict):
                details.append(f"{key}: {item.get('path') or 'not set'} exists={item.get('exists')}")
    return [item for item in details if item]


def _details_from_discovery(record: dict[str, Any]) -> list[str]:
    details: list[str] = []
    paths = record.get("paths", {})
    sources = record.get("sources", {})
    if isinstance(paths, dict):
        for key, value in sorted(paths.items()):
            source = sources.get(key) if isinstance(sources, dict) else None
            suffix = f" ({source})" if source else ""
            details.append(f"{key}: {value}{suffix}")
    messages = record.get("messages", [])
    if isinstance(messages, list):
        details.extend(str(item) for item in messages)
    if not details:
        details.append("not found; run ai-cae-toolbox setup or set a private local config/environment variable")
    return details


def check_discovered_solver(name: str, discovery: dict[str, Any]) -> CheckResult:
    record = discovery.get("solvers", {}).get(name, {})
    if not isinstance(record, dict):
        return CheckResult(name, "unknown", ["discovery record not available"])
    return CheckResult(name, record.get("status", "unknown"), _details_from_discovery(record))


def check_openfoam() -> CheckResult:
    payload = openfoam_check_install()
    return CheckResult("openfoam", payload.get("status", "missing"), _details_from_adapter(payload))


def check_paraview() -> CheckResult:
    payload = paraview_check_install()
    return CheckResult("paraview", payload.get("status", "missing"), _details_from_adapter(payload))


def run_checks(deep: bool = False) -> list[CheckResult]:
    discovery = discover_toolchains(deep=deep)
    results = [
        check_python(),
        check_command("git"),
    ]
    for name in ("abaqus", "ansys", "fluent", "workbench", "comsol", "matlab", "pcschematic"):
        results.append(check_discovered_solver(name, discovery))
    results.extend([check_openfoam(), check_paraview()])
    return results


def format_text(results: list[CheckResult]) -> str:
    lines = ["AI CAE environment check", ""]
    for item in results:
        lines.append(f"[{item.status}] {item.name}")
        for detail in item.details:
            lines.append(f"  - {detail}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check local CAE automation environment.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--deep", action="store_true", help="Use slower discovery rules where supported.")
    args = parser.parse_args()

    results = run_checks(deep=args.deep)
    if args.json:
        print(json.dumps([asdict(item) for item in results], ensure_ascii=False, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
