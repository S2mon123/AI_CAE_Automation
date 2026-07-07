from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .adapters import known_adapters
from .env_check import format_text, run_checks
from .evidence import scan_evidence
from .report import generate_report
from .runs import create_run
from .skills import list_skill_packs


def print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def command_env_check(args: argparse.Namespace) -> None:
    results = run_checks()
    if args.json:
        print_json([asdict(item) for item in results])
    else:
        print(format_text(results))


def command_create_run(args: argparse.Namespace) -> None:
    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()] if args.tags else []
    payload = create_run(
        root=args.root,
        solver=args.solver,
        case_name=args.case,
        objective=args.objective,
        tags=tags,
    )
    if args.json:
        print_json(payload)
    else:
        print(f"created run: {payload['run_dir']}")
        print(f"run record: {payload['run_json']}")


def command_list_skills(args: argparse.Namespace) -> None:
    payload = list_skill_packs()
    if args.json:
        print_json(payload)
    else:
        for item in payload:
            print(f"{item['name']}: {item['purpose']}")


def command_list_adapters(args: argparse.Namespace) -> None:
    payload = [asdict(item) for item in known_adapters()]
    if args.json:
        print_json(payload)
    else:
        for item in payload:
            print(f"{item['name']} [{item['maturity']}]")


def command_scan_evidence(args: argparse.Namespace) -> None:
    payload = scan_evidence(args.run_dir, write=not args.no_write)
    if args.json:
        print_json(payload)
    else:
        print(f"run: {payload['run_id']}")
        print(f"credibility: {payload['credibility_grade']}")
        print("counts:")
        for kind, count in sorted(payload["counts"].items()):
            print(f"  - {kind}: {count}")


def command_generate_report(args: argparse.Namespace) -> None:
    payload = generate_report(args.run_dir)
    if args.json:
        print_json(payload)
    else:
        print(f"report: {payload['report_path']}")
        print(f"credibility: {payload['credibility_grade']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-cae-toolbox",
        description="Local AI CAE automation toolbox for run records, evidence scans, and MCP bridge workflows.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    env_parser = subparsers.add_parser("env-check", help="Check local CAE automation environment.")
    env_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    env_parser.set_defaults(func=command_env_check)

    run_parser = subparsers.add_parser("create-run", help="Create a traceable run directory.")
    run_parser.add_argument("--root", default="runs", help="Root directory for run records.")
    run_parser.add_argument("--solver", required=True, help="Solver or automation target name.")
    run_parser.add_argument("--case", required=True, help="Short case name.")
    run_parser.add_argument("--objective", default="", help="Run objective.")
    run_parser.add_argument("--tags", default="", help="Comma-separated tags.")
    run_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    run_parser.set_defaults(func=command_create_run)

    skills_parser = subparsers.add_parser("list-skills", help="List public Codex skill packs.")
    skills_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    skills_parser.set_defaults(func=command_list_skills)

    adapters_parser = subparsers.add_parser("list-adapters", help="List solver adapter capabilities.")
    adapters_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    adapters_parser.set_defaults(func=command_list_adapters)

    scan_parser = subparsers.add_parser("scan-evidence", help="Scan a run directory and grade evidence.")
    scan_parser.add_argument("run_dir", type=Path, help="Path to a run directory.")
    scan_parser.add_argument("--no-write", action="store_true", help="Do not write evidence.json.")
    scan_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    scan_parser.set_defaults(func=command_scan_evidence)

    report_parser = subparsers.add_parser("generate-report", help="Generate report.md for a run.")
    report_parser.add_argument("run_dir", type=Path, help="Path to a run directory.")
    report_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    report_parser.set_defaults(func=command_generate_report)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
