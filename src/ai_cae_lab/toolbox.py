from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .adapters import known_adapters
from .config import bridge_plan, toolchain_paths
from .context_scope import solver_context_scope
from .discovery import (
    discover_toolchains,
    setup_local,
    write_activation_script,
    write_codex_mcp_config,
    write_local_config,
)
from .env_check import format_text, run_checks
from .evidence import scan_evidence
from .report import generate_report
from .runs import create_run
from .skills import list_skill_packs
from .templates import write_solver_smoke_template


def print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def command_env_check(args: argparse.Namespace) -> None:
    results = run_checks(deep=getattr(args, "deep", False))
    if args.json:
        print_json([asdict(item) for item in results])
    else:
        print(format_text(results))


def _print_discovery_summary(payload: dict[str, object]) -> None:
    print(f"discovered_at: {payload.get('discovered_at')}")
    solvers = payload.get("solvers", {})
    if not isinstance(solvers, dict):
        return
    for name, record in solvers.items():
        if not isinstance(record, dict):
            continue
        print(f"[{record.get('status', 'unknown')}] {name}")
        paths = record.get("paths", {})
        if isinstance(paths, dict):
            for key, value in sorted(paths.items()):
                print(f"  - {key}: {value}")
        messages = record.get("messages", [])
        if isinstance(messages, list):
            for message in messages:
                print(f"  - {message}")


def command_discover(args: argparse.Namespace) -> None:
    payload = discover_toolchains(deep=args.deep)
    if args.json:
        print_json(payload)
    else:
        _print_discovery_summary(payload)


def command_doctor(args: argparse.Namespace) -> None:
    results = run_checks(deep=args.deep)
    if args.json:
        print_json([asdict(item) for item in results])
    else:
        print(format_text(results))
        print()
        print("next steps:")
        print("  - Run ai-cae-toolbox setup to generate private/ai-cae.local.json.")
        print("  - Activate private/activate-ai-cae.ps1 before launching Codex or long solver tasks.")
        print("  - Use context-scope --solver <name> so agents read only solver-relevant files.")


def command_setup(args: argparse.Namespace) -> None:
    payload = setup_local(deep=args.deep)
    if args.json:
        print_json(payload)
    else:
        print("AI CAE local setup complete")
        print(f"local config: {payload['local_config']}")
        print(f"activation script: {payload['activation_script']}")
        print(f"Codex MCP config: {payload['codex_mcp_config']}")
        print()
        _print_discovery_summary(payload["discovery"])


def command_write_local_config(args: argparse.Namespace) -> None:
    payload = write_local_config(path=args.path, deep=args.deep)
    if args.json:
        print_json(payload)
    else:
        print(f"local config written: {payload['path']}")


def command_write_activation_script(args: argparse.Namespace) -> None:
    payload = write_activation_script(config_path=args.config, output_path=args.path)
    if args.json:
        print_json(payload)
    else:
        print(f"activation script written: {payload['path']}")


def command_write_codex_mcp_config(args: argparse.Namespace) -> None:
    payload = write_codex_mcp_config(output_path=args.path)
    if args.json:
        print_json(payload)
    else:
        print(f"Codex MCP config written: {payload['path']}")


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


def command_context_scope(args: argparse.Namespace) -> None:
    payload = solver_context_scope(args.solver, include_common=not args.no_common)
    if args.json:
        print_json(payload)
    else:
        print(f"solver: {payload['solver']}")
        print("read this context only:")
        for item in payload["scope"]:
            print(f"  - {item['path']} ({item['kind']})")
        if payload["missing"]:
            print("missing optional paths:")
            for item in payload["missing"]:
                print(f"  - {item}")
        print("rules:")
        for rule in payload["rules"]:
            print(f"  - {rule}")


def command_toolchain_paths(args: argparse.Namespace) -> None:
    payload = toolchain_paths(args.solver, args.config)
    if args.json:
        print_json(payload)
    else:
        print(f"solver: {payload['solver']}")
        print(f"config: {payload['config_path'] or 'not configured'}")
        print("environment variables:")
        for name in payload["environment_variables"]:
            marker = "set" if name in payload["environment_values_set"] else "not set"
            print(f"  - {name}: {marker}")
        if payload["configured_paths"]:
            print("configured private paths:")
            for key, value in payload["configured_paths"].items():
                print(f"  - {key}: {value}")
        print("path resolution order:")
        for item in payload["path_resolution_order"]:
            print(f"  - {item}")

def command_bridge_plan(args: argparse.Namespace) -> None:
    payload = bridge_plan(args.solver, args.objective, args.config)
    if args.json:
        print_json(payload)
    else:
        print(f"solver: {payload['solver']}")
        print(f"config: {payload['config_path'] or 'default'}")
        print("recommended MCP tools:")
        for tool in payload["recommended_mcp_tools"]:
            print(f"  - {tool}")
        print("phases:")
        for phase in payload["phases"]:
            print(f"  - {phase}")


def command_write_smoke_template(args: argparse.Namespace) -> None:
    payload = write_solver_smoke_template(
        solver=args.solver,
        run_dir=args.run_dir,
        case_name=args.case,
        overwrite=args.overwrite,
    )
    if args.json:
        print_json(payload)
    else:
        print(f"status: {payload['status']}")
        for path in payload.get("written", []):
            print(f"written: {path}")
        for path in payload.get("skipped", []):
            print(f"skipped: {path}")


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

    setup_parser = subparsers.add_parser("setup", help="Discover local CAE tools and write private config files.")
    setup_parser.add_argument("--deep", action="store_true", help="Use slower discovery rules where supported.")
    setup_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    setup_parser.set_defaults(func=command_setup)

    discover_parser = subparsers.add_parser("discover", help="Discover local CAE toolchains without writing files.")
    discover_parser.add_argument("--deep", action="store_true", help="Use slower discovery rules where supported.")
    discover_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    discover_parser.set_defaults(func=command_discover)

    doctor_parser = subparsers.add_parser("doctor", help="Diagnose local CAE path configuration.")
    doctor_parser.add_argument("--deep", action="store_true", help="Use slower discovery rules where supported.")
    doctor_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    doctor_parser.set_defaults(func=command_doctor)

    local_config_parser = subparsers.add_parser("write-local-config", help="Write private/ai-cae.local.json from discovery.")
    local_config_parser.add_argument("--path", default=None, help="Optional output JSON path.")
    local_config_parser.add_argument("--deep", action="store_true", help="Use slower discovery rules where supported.")
    local_config_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    local_config_parser.set_defaults(func=command_write_local_config)

    activation_parser = subparsers.add_parser("write-activation-script", help="Write a PowerShell activation script from local config.")
    activation_parser.add_argument("--config", default=None, help="Optional local config JSON path.")
    activation_parser.add_argument("--path", default=None, help="Optional output PowerShell path.")
    activation_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    activation_parser.set_defaults(func=command_write_activation_script)

    codex_mcp_parser = subparsers.add_parser("write-codex-mcp-config", help="Write a local Codex MCP TOML snippet.")
    codex_mcp_parser.add_argument("--path", default=None, help="Optional output TOML path.")
    codex_mcp_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    codex_mcp_parser.set_defaults(func=command_write_codex_mcp_config)

    env_parser = subparsers.add_parser("env-check", help="Check local CAE automation environment.")
    env_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    env_parser.add_argument("--deep", action="store_true", help="Use slower discovery rules where supported.")
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

    context_parser = subparsers.add_parser("context-scope", help="Print minimal files/directories to read for one solver.")
    context_parser.add_argument("--solver", required=True, help="Solver or automation target name.")
    context_parser.add_argument("--no-common", action="store_true", help="Omit shared docs/config context.")
    context_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    context_parser.set_defaults(func=command_context_scope)

    paths_parser = subparsers.add_parser("toolchain-paths", help="Explain executable path resolution for one solver.")
    paths_parser.add_argument("--solver", required=True, help="Solver or automation target name.")
    paths_parser.add_argument("--config", default=None, help="Optional private toolbox JSON config path.")
    paths_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    paths_parser.set_defaults(func=command_toolchain_paths)
    bridge_parser = subparsers.add_parser("bridge-plan", help="Print a structured solver bridge plan.")
    bridge_parser.add_argument("--solver", required=True, help="Solver or automation target name.")
    bridge_parser.add_argument("--objective", default="", help="Engineering objective for the bridge plan.")
    bridge_parser.add_argument("--config", default=None, help="Optional toolbox JSON config path.")
    bridge_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    bridge_parser.set_defaults(func=command_bridge_plan)

    template_parser = subparsers.add_parser("write-smoke-template", help="Write a solver-native smoke template.")
    template_parser.add_argument("--solver", required=True, help="Solver or automation target name.")
    template_parser.add_argument("--run-dir", required=True, type=Path, help="Run directory created by create-run.")
    template_parser.add_argument("--case", default="smoke-test", help="Case name used inside generated files.")
    template_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing template files.")
    template_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    template_parser.set_defaults(func=command_write_smoke_template)

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
