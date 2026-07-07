from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_codex_home() -> Path:
    value = os.environ.get("CODEX_HOME")
    if value:
        return Path(value).expanduser()
    return Path.home() / ".codex"


def skill_source_dirs(root: Path) -> list[Path]:
    skills_root = root / "codex-skills"
    if not skills_root.exists():
        raise FileNotFoundError(f"codex-skills directory not found: {skills_root}")
    return sorted(path for path in skills_root.iterdir() if path.is_dir() and (path / "SKILL.md").exists())


def copy_skills(root: Path, codex_home: Path, force: bool) -> list[dict[str, str]]:
    target_root = codex_home / "skills"
    target_root.mkdir(parents=True, exist_ok=True)
    installed: list[dict[str, str]] = []

    for source in skill_source_dirs(root):
        target = target_root / source.name
        if target.exists() and not force:
            installed.append({"skill": source.name, "status": "skipped", "path": str(target)})
            continue
        shutil.copytree(source, target, dirs_exist_ok=True)
        installed.append({"skill": source.name, "status": "installed", "path": str(target)})

    return installed


def mcp_command(root: Path) -> tuple[str, list[str]]:
    exe = root / ".venv" / "Scripts" / "ai-cae-mcp-server.exe"
    if exe.exists():
        return str(exe), []
    return "python", ["-m", "ai_cae_lab.mcp_server"]


def mcp_json(root: Path) -> dict[str, object]:
    command, args = mcp_command(root)
    return {
        "mcpServers": {
            "ai-cae-automation-lab": {
                "command": command,
                "args": args,
                "env": {
                    "ABAQUS_COMMAND": "<optional-path-to-abaqus-command>",
                    "FLUENT_ROOT": "<optional-path-to-ansys-root>",
                    "COMSOL_ROOT": "<optional-path-to-comsol-root>",
                    "MATLABROOT": "<optional-path-to-matlab-root>",
                    "PCSCHEMATIC_ROOT": "<optional-path-to-pcschematic-root>",
                    "PCSCHEMATIC_TLB": "<optional-path-to-pcschematic-tlb>",
                },
            }
        }
    }


def mcp_toml(root: Path) -> str:
    command, args = mcp_command(root)
    args_text = "[" + ", ".join(json.dumps(arg) for arg in args) + "]"
    return "\n".join(
        [
            "[mcp_servers.ai-cae-automation-lab]",
            f"command = {json.dumps(command)}",
            f"args = {args_text}",
            "startup_timeout_sec = 120",
            "",
            "[mcp_servers.ai-cae-automation-lab.env]",
            'ABAQUS_COMMAND = "<optional-path-to-abaqus-command>"',
            'FLUENT_ROOT = "<optional-path-to-ansys-root>"',
            'COMSOL_ROOT = "<optional-path-to-comsol-root>"',
            'MATLABROOT = "<optional-path-to-matlab-root>"',
            'PCSCHEMATIC_ROOT = "<optional-path-to-pcschematic-root>"',
            'PCSCHEMATIC_TLB = "<optional-path-to-pcschematic-tlb>"',
            "",
        ]
    )


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install AI CAE Automation Lab Codex skills and generate MCP config snippets."
    )
    parser.add_argument("--codex-home", default=str(default_codex_home()), help="Codex home directory.")
    parser.add_argument("--install-skills", action="store_true", help="Copy codex-skills into Codex skills.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing installed skill folders.")
    parser.add_argument("--write-mcp-json", type=Path, help="Write a JSON MCP client config snippet.")
    parser.add_argument("--write-mcp-toml", type=Path, help="Write a Codex config.toml MCP snippet.")
    parser.add_argument("--print-mcp-toml", action="store_true", help="Print a Codex config.toml MCP snippet.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable install summary.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    root = repo_root()
    codex_home = Path(args.codex_home).expanduser()
    summary: dict[str, object] = {
        "repo_root": str(root),
        "codex_home": str(codex_home),
        "skills": [],
        "mcp_json": None,
        "mcp_toml": None,
    }

    if args.install_skills:
        summary["skills"] = copy_skills(root, codex_home, args.force)

    if args.write_mcp_json:
        write_json(args.write_mcp_json, mcp_json(root))
        summary["mcp_json"] = str(args.write_mcp_json)

    if args.write_mcp_toml:
        args.write_mcp_toml.parent.mkdir(parents=True, exist_ok=True)
        args.write_mcp_toml.write_text(mcp_toml(root), encoding="utf-8")
        summary["mcp_toml"] = str(args.write_mcp_toml)

    if args.print_mcp_toml:
        print(mcp_toml(root))

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    elif not args.print_mcp_toml:
        print("AI CAE Codex asset installer")
        print(f"repo: {root}")
        print(f"codex home: {codex_home}")
        for item in summary["skills"]:
            print(f"{item['status']}: {item['skill']} -> {item['path']}")
        if summary["mcp_json"]:
            print(f"wrote MCP JSON: {summary['mcp_json']}")
        if summary["mcp_toml"]:
            print(f"wrote MCP TOML: {summary['mcp_toml']}")


if __name__ == "__main__":
    main()
