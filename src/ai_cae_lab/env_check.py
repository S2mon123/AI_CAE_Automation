from __future__ import annotations

import argparse
import json
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path


DEFAULT_CANDIDATES = {
    "abaqus": [
        r"C:\SIMULIA\Commands\abaqus.bat",
        r"D:\SIMULIA\Commands\abaqus.bat",
        r"F:\Abaqus2026\ABAQUS2026\command\abaqus.bat",
        r"F:\Abaqus2026\ABAQUS2026\command\abq2026.bat",
        r"F:\Abaqus2026\Commands\abaqus.bat",
        r"G:\SIMULIA\Commands\abaqus.bat",
    ],
    "fluent": [
        r"C:\Program Files\ANSYS Inc",
        r"D:\Program Files\ANSYS Inc",
    ],
    "comsol": [
        r"C:\Program Files\COMSOL",
        r"D:\Program Files\COMSOL",
    ],
    "matlab": [
        r"C:\Program Files\MATLAB",
        r"D:\Program Files\MATLAB",
    ],
}


@dataclass
class CheckResult:
    name: str
    status: str
    details: list[str]


def path_exists(path: str) -> bool:
    return Path(path).exists()


def check_python() -> CheckResult:
    details = [
        f"sys executable from environment: {shutil.which('python') or 'not on PATH'}",
        f"conda python: {os.environ.get('CONDA_PYTHON_EXE', 'not set')}",
    ]
    return CheckResult("python", "ok", details)


def check_command(name: str) -> CheckResult:
    found = shutil.which(name)
    if found:
        return CheckResult(name, "ok", [found])
    return CheckResult(name, "missing", [f"{name} not found on PATH"])


def check_candidates(name: str, candidates: list[str]) -> CheckResult:
    hits = [path for path in candidates if path_exists(path)]
    if hits:
        return CheckResult(name, "ok", hits)
    return CheckResult(name, "missing", [f"no known candidate exists for {name}"])


def run_checks() -> list[CheckResult]:
    results = [check_python(), check_command("git")]
    for name, candidates in DEFAULT_CANDIDATES.items():
        results.append(check_candidates(name, candidates))
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
    args = parser.parse_args()

    results = run_checks()
    if args.json:
        print(json.dumps([asdict(item) for item in results], ensure_ascii=False, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
