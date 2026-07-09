from __future__ import annotations

import json
import os
import platform
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .config import configured_solver_paths, load_toolbox_config
from .runs import utc_now


STATUS_OK = "ok"
STATUS_PARTIAL = "partial"
STATUS_MISSING = "missing"
STATUS_INVALID = "invalid"
STATUS_UNKNOWN = "unknown"

SOLVER_KEYS = ("abaqus", "ansys", "fluent", "workbench", "comsol", "matlab", "pcschematic")


@dataclass
class PathHit:
    path: str
    source: str
    exists: bool


@dataclass
class DiscoveryRecord:
    name: str
    status: str = STATUS_MISSING
    root: str | None = None
    paths: dict[str, str] = field(default_factory=dict)
    checks: dict[str, bool] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _existing(path: str | Path | None) -> Path | None:
    if not path:
        return None
    try:
        value = Path(path).expanduser()
        if value.exists():
            return value.resolve()
    except OSError:
        return None
    return None


def _which(command: str) -> Path | None:
    found = shutil.which(command)
    return _existing(found)


def _first_existing(candidates: Iterable[tuple[str | Path | None, str]]) -> tuple[Path | None, str | None]:
    for value, source in candidates:
        hit = _existing(value)
        if hit:
            return hit, source
    return None, None


def _invalid_config_messages(candidates: Iterable[tuple[str | Path | None, str]]) -> list[str]:
    messages: list[str] = []
    for value, source in candidates:
        if not value or not (source.startswith("env:") or source.startswith("config:")):
            continue
        raw = str(value)
        if _existing(raw) or shutil.which(raw):
            continue
        messages.append(f"invalid configured path from {source}: {raw}")
    return messages


def _attach_invalid_config(record: DiscoveryRecord, candidates: Iterable[tuple[str | Path | None, str]]) -> DiscoveryRecord:
    messages = _invalid_config_messages(candidates)
    if messages:
        record.messages.extend(messages)
        if record.status == STATUS_MISSING:
            record.status = STATUS_INVALID
    return record


def _glob_existing(patterns: Iterable[str], limit: int = 40) -> list[tuple[Path, str]]:
    hits: list[tuple[Path, str]] = []
    for pattern in patterns:
        for raw in sorted(Path().glob(pattern)) if not Path(pattern).is_absolute() else sorted(Path(pattern.split("*")[0]).parent.glob(Path(pattern).name)):
            # This branch is intentionally unused for absolute Windows globs; Path.glob
            # cannot reliably handle drive-qualified wildcards from a relative cwd.
            if raw.exists():
                hits.append((raw.resolve(), f"glob:{pattern}"))
                if len(hits) >= limit:
                    return hits
    return hits


def _windows_glob(patterns: Iterable[str], limit: int = 80) -> list[tuple[Path, str]]:
    hits: list[tuple[Path, str]] = []
    for pattern in patterns:
        try:
            import glob

            for value in sorted(glob.glob(pattern)):
                hit = _existing(value)
                if hit:
                    hits.append((hit, f"glob:{pattern}"))
                    if len(hits) >= limit:
                        return hits
        except OSError:
            continue
    return hits


def _windows_drive_roots() -> list[str]:
    if os.name != "nt":
        return []
    roots: list[str] = []
    for code in range(ord("C"), ord("Z") + 1):
        root = f"{chr(code)}:\\"
        if Path(root).exists():
            roots.append(root)
    return roots


def _drive_patterns(suffixes: Iterable[str]) -> list[str]:
    patterns: list[str] = []
    for drive in _windows_drive_roots():
        for suffix in suffixes:
            patterns.append(drive + suffix.lstrip("\\"))
    return patterns


def _registry_values(keys: Iterable[tuple[str, str]], value_names: Iterable[str]) -> list[tuple[str, str]]:
    if os.name != "nt":
        return []
    try:
        import winreg
    except ImportError:
        return []

    hives = {
        "HKLM": winreg.HKEY_LOCAL_MACHINE,
        "HKCU": winreg.HKEY_CURRENT_USER,
    }
    results: list[tuple[str, str]] = []
    for hive_name, key_path in keys:
        hive = hives.get(hive_name)
        if hive is None:
            continue
        for view_flag in (0, getattr(winreg, "KEY_WOW64_64KEY", 0), getattr(winreg, "KEY_WOW64_32KEY", 0)):
            try:
                with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | view_flag) as key:
                    for value_name in value_names:
                        try:
                            value, _ = winreg.QueryValueEx(key, value_name)
                            if isinstance(value, str) and value:
                                results.append((value, f"registry:{hive_name}\\{key_path}:{value_name}"))
                        except OSError:
                            continue
            except OSError:
                continue
    return results


def _record(name: str, paths: dict[str, tuple[Path | None, str | None]], required: list[str], root_key: str | None = "root") -> DiscoveryRecord:
    record = DiscoveryRecord(name=name)
    for key, (path, source) in paths.items():
        exists = bool(path and path.exists())
        record.checks[key] = exists
        if exists and path:
            record.paths[key] = str(path)
            if source:
                record.sources[key] = source
    if root_key and root_key in record.paths:
        record.root = record.paths[root_key]

    missing_required = [key for key in required if not record.checks.get(key)]
    any_found = any(record.checks.values())
    if not any_found:
        record.status = STATUS_MISSING
    elif missing_required:
        record.status = STATUS_PARTIAL
        record.messages.append("missing required paths: " + ", ".join(missing_required))
    else:
        record.status = STATUS_OK
    return record


def _comsol_root_from_path(path: Path | None) -> Path | None:
    if not path:
        return None
    parts = list(path.parents)
    for parent in parts:
        if parent.name.lower() == "multiphysics":
            return parent.parent
    return None


def discover_comsol(deep: bool = False) -> DiscoveryRecord:
    env = os.environ
    configured = configured_solver_paths(load_toolbox_config(), "comsol")
    batch_candidates: list[tuple[str | Path | None, str]] = [
        (env.get("COMSOL_BATCH"), "env:COMSOL_BATCH"),
        (configured.get("batch"), "config:comsol.batch"),
        (_which("comsolbatch"), "PATH:comsolbatch"),
    ]
    exe_candidates: list[tuple[str | Path | None, str]] = [
        (env.get("COMSOL_EXE"), "env:COMSOL_EXE"),
        (configured.get("exe"), "config:comsol.exe"),
        (_which("comsol"), "PATH:comsol"),
    ]
    root_candidates: list[tuple[str | Path | None, str]] = [
        (env.get("COMSOL_ROOT"), "env:COMSOL_ROOT"),
        (configured.get("root"), "config:comsol.root"),
    ]
    root_candidates.extend(_registry_values([
        ("HKLM", r"SOFTWARE\COMSOL"),
        ("HKCU", r"SOFTWARE\COMSOL"),
    ], ["InstallDir", "RootDir", "Path"]))

    common_batch_patterns = _drive_patterns([
        r"COMSOL*\Multiphysics\bin\win64\comsolbatch.exe",
        r"COMSOL*\COMSOL*\Multiphysics\bin\win64\comsolbatch.exe",
        r"COMSOL*\COMSOL\COMSOL*\Multiphysics\bin\win64\comsolbatch.exe",
        r"Program Files\COMSOL\COMSOL*\Multiphysics\bin\win64\comsolbatch.exe",
        r"Program Files\COMSOL*\COMSOL*\Multiphysics\bin\win64\comsolbatch.exe",
    ])
    common_exe_patterns = [pattern.replace("comsolbatch.exe", "comsol.exe") for pattern in common_batch_patterns]
    common_compile_patterns = [pattern.replace("comsolbatch.exe", "comsolcompile.exe") for pattern in common_batch_patterns]
    common_mphserver_patterns = [pattern.replace("comsolbatch.exe", "comsolmphserver.exe") for pattern in common_batch_patterns]
    batch_candidates.extend(_windows_glob(common_batch_patterns))
    exe_candidates.extend(_windows_glob(common_exe_patterns))

    batch, batch_source = _first_existing(batch_candidates)
    exe, exe_source = _first_existing(exe_candidates)
    root, root_source = _first_existing(root_candidates)
    if not root:
        root = _comsol_root_from_path(batch) or _comsol_root_from_path(exe)
        root_source = "derived:comsol-executable" if root else None

    multiphysics = root / "Multiphysics" if root and (root / "Multiphysics").exists() else root
    java_candidates: list[tuple[str | Path | None, str]] = [
        (env.get("COMSOL_JAVA"), "env:COMSOL_JAVA"),
        (configured.get("java"), "config:comsol.java"),
        (multiphysics / "java" / "win64" / "jre" / "bin" / "java.exe" if multiphysics else None, "derived:COMSOL_ROOT"),
    ]
    compile_candidates: list[tuple[str | Path | None, str]] = [
        (env.get("COMSOL_COMPILE"), "env:COMSOL_COMPILE"),
        (configured.get("compile"), "config:comsol.compile"),
        (_which("comsolcompile"), "PATH:comsolcompile"),
        (multiphysics / "bin" / "win64" / "comsolcompile.exe" if multiphysics else None, "derived:COMSOL_ROOT"),
    ]
    compile_candidates.extend(_windows_glob(common_compile_patterns))
    mphserver_candidates: list[tuple[str | Path | None, str]] = [
        (env.get("COMSOL_MPHSERVER"), "env:COMSOL_MPHSERVER"),
        (configured.get("mphserver"), "config:comsol.mphserver"),
        (_which("comsolmphserver"), "PATH:comsolmphserver"),
        (multiphysics / "bin" / "win64" / "comsolmphserver.exe" if multiphysics else None, "derived:COMSOL_ROOT"),
    ]
    mphserver_candidates.extend(_windows_glob(common_mphserver_patterns))
    api_index = multiphysics / "doc" / "help" / "wtpwebapps" / "ROOT" / "doc" / "com.comsol.help.comsol" / "api" / "index.html" if multiphysics else None

    java, java_source = _first_existing(java_candidates)
    compile_cmd, compile_source = _first_existing(compile_candidates)
    mphserver, mphserver_source = _first_existing(mphserver_candidates)
    api, api_source = _first_existing([(api_index, "derived:COMSOL_ROOT")])

    record = _record(
        "comsol",
        {
            "root": (root, root_source),
            "batch": (batch, batch_source),
            "exe": (exe, exe_source),
            "java": (java, java_source),
            "compile": (compile_cmd, compile_source),
            "mphserver": (mphserver, mphserver_source),
            "api_index": (api, api_source),
        },
        required=["root", "batch", "exe", "java", "api_index"],
    )
    return _attach_invalid_config(
        record,
        [*batch_candidates, *exe_candidates, *root_candidates, *java_candidates, *compile_candidates, *mphserver_candidates],
    )


def discover_abaqus(deep: bool = False) -> DiscoveryRecord:
    env = os.environ
    configured = configured_solver_paths(load_toolbox_config(), "abaqus")
    candidates: list[tuple[str | Path | None, str]] = [
        (env.get("ABAQUS_COMMAND"), "env:ABAQUS_COMMAND"),
        (configured.get("command"), "config:abaqus.command"),
        (_which("abaqus"), "PATH:abaqus"),
    ]
    candidates.extend(_windows_glob(_drive_patterns([
        r"SIMULIA\Commands\abaqus.bat",
        r"ABAQUS*\commands\abaqus.bat",
        r"Program Files\Dassault Systemes\*\win_b64\code\bin\ABQLauncher.exe",
    ])))
    command, source = _first_existing(candidates)
    root = command.parent.parent if command and command.name.lower() == "abaqus.bat" else None
    record = _record(
        "abaqus",
        {"root": (root, "derived:abaqus-command" if root else None), "command": (command, source)},
        required=["command"],
    )
    return _attach_invalid_config(record, candidates)


def _ansys_version_root(path: Path | None) -> Path | None:
    if not path:
        return None
    for parent in path.parents:
        if parent.name.lower().startswith("v") and parent.parent.name.lower() == "ansys inc":
            return parent
    return None


def _ansys_root_from_version(version_root: Path | None) -> Path | None:
    return version_root.parent if version_root else None


def discover_ansys_family(deep: bool = False) -> dict[str, DiscoveryRecord]:
    env = os.environ
    ansys_config = configured_solver_paths(load_toolbox_config(), "ansys")
    fluent_config = configured_solver_paths(load_toolbox_config(), "fluent")
    workbench_config = configured_solver_paths(load_toolbox_config(), "ansys-workbench")
    root_candidates: list[tuple[str | Path | None, str]] = [
        (env.get("ANSYS_ROOT"), "env:ANSYS_ROOT"),
        (env.get("FLUENT_ROOT"), "env:FLUENT_ROOT"),
        (ansys_config.get("root"), "config:ansys.root"),
        (fluent_config.get("root"), "config:fluent.root"),
        (workbench_config.get("root"), "config:workbench.root"),
    ]
    fluent_candidates: list[tuple[str | Path | None, str]] = [
        (env.get("FLUENT_EXE"), "env:FLUENT_EXE"),
        (fluent_config.get("fluent_exe"), "config:fluent.fluent_exe"),
        (ansys_config.get("fluent_exe"), "config:ansys.fluent_exe"),
        (_which("fluent"), "PATH:fluent"),
    ]
    workbench_candidates: list[tuple[str | Path | None, str]] = [
        (env.get("WORKBENCH_EXE"), "env:WORKBENCH_EXE"),
        (env.get("ANSYS_WORKBENCH_EXE"), "env:ANSYS_WORKBENCH_EXE"),
        (workbench_config.get("workbench_exe"), "config:workbench.workbench_exe"),
        (ansys_config.get("workbench_exe"), "config:ansys.workbench_exe"),
    ]
    common_roots = _drive_patterns([r"Program Files\ANSYS Inc", r"ANSYS Inc"])
    for base in common_roots:
        root_candidates.append((base, f"common:{base}"))
        fluent_candidates.extend(_windows_glob([base + r"\v*\fluent\ntbin\win64\fluent.exe", base + r"\v*\fluent\bin\fluent"]))
        workbench_candidates.extend(_windows_glob([base + r"\v*\Framework\bin\Win64\RunWB2.exe", base + r"\v*\aisol\bin\winx64\AnsysWBU.exe"]))

    fluent, fluent_source = _first_existing(fluent_candidates)
    workbench, workbench_source = _first_existing(workbench_candidates)
    version_root = _ansys_version_root(fluent) or _ansys_version_root(workbench)
    root, root_source = _first_existing(root_candidates)
    if not root:
        root = _ansys_root_from_version(version_root)
        root_source = "derived:ansys-executable" if root else None

    ansys = _record("ansys", {"root": (root, root_source), "fluent_exe": (fluent, fluent_source), "workbench_exe": (workbench, workbench_source)}, required=[])
    if root and not (fluent or workbench):
        ansys.status = STATUS_PARTIAL
        ansys.messages.append("Ansys root found, but no Fluent or Workbench executable was found.")
    elif fluent or workbench:
        ansys.status = STATUS_OK
    else:
        ansys.status = STATUS_MISSING
    ansys = _attach_invalid_config(ansys, [*root_candidates, *fluent_candidates, *workbench_candidates])

    fluent_record = _record("fluent", {"root": (root, root_source), "fluent_exe": (fluent, fluent_source)}, required=["fluent_exe"])
    fluent_record = _attach_invalid_config(fluent_record, [*root_candidates, *fluent_candidates])
    workbench_record = _record("workbench", {"root": (root, root_source), "workbench_exe": (workbench, workbench_source)}, required=["workbench_exe"])
    workbench_record = _attach_invalid_config(workbench_record, [*root_candidates, *workbench_candidates])
    return {"ansys": ansys, "fluent": fluent_record, "workbench": workbench_record}


def discover_matlab(deep: bool = False) -> DiscoveryRecord:
    env = os.environ
    configured = configured_solver_paths(load_toolbox_config(), "matlab")
    exe_candidates: list[tuple[str | Path | None, str]] = [
        (env.get("MATLAB_EXE"), "env:MATLAB_EXE"),
        (configured.get("matlab_exe"), "config:matlab.matlab_exe"),
        (_which("matlab"), "PATH:matlab"),
    ]
    root_candidates: list[tuple[str | Path | None, str]] = [
        (env.get("MATLABROOT"), "env:MATLABROOT"),
        (configured.get("root"), "config:matlab.root"),
    ]
    root_candidates.extend(_registry_values([
        ("HKLM", r"SOFTWARE\MathWorks\MATLAB"),
        ("HKCU", r"SOFTWARE\MathWorks\MATLAB"),
    ], ["MATLABROOT", "Root", "InstallDir"]))
    patterns = _drive_patterns([
        r"Program Files\MATLAB\R*\bin\matlab.exe",
        r"MATLAB\R*\bin\matlab.exe",
        r"matlab\MATLAB\bin\matlab.exe",
    ])
    exe_candidates.extend(_windows_glob(patterns))
    exe, exe_source = _first_existing(exe_candidates)
    root, root_source = _first_existing(root_candidates)
    if not root and exe:
        root = exe.parent.parent
        root_source = "derived:matlab-executable"
    record = _record("matlab", {"root": (root, root_source), "matlab_exe": (exe, exe_source)}, required=["matlab_exe"])
    return _attach_invalid_config(record, [*exe_candidates, *root_candidates])


def discover_pcschematic(deep: bool = False) -> DiscoveryRecord:
    env = os.environ
    configured = configured_solver_paths(load_toolbox_config(), "pcschematic")
    exe_candidates: list[tuple[str | Path | None, str]] = [
        (env.get("PCSCHEMATIC_EXE"), "env:PCSCHEMATIC_EXE"),
        (configured.get("exe"), "config:pcschematic.exe"),
    ]
    exe_candidates.extend(_windows_glob(_drive_patterns([
        r"Program Files\PCSCHEMATIC\PCSELCAD\PCsELcad.exe",
        r"PCSCHEMATIC\PCSELCAD\PCsELcad.exe",
    ])))
    exe, exe_source = _first_existing(exe_candidates)
    root_candidates = [
        (env.get("PCSCHEMATIC_ROOT"), "env:PCSCHEMATIC_ROOT"),
        (configured.get("root"), "config:pcschematic.root"),
        (exe.parent if exe else None, "derived:PCSCHEMATIC_EXE"),
    ]
    root, root_source = _first_existing(root_candidates)
    tlb_candidates = [
        (env.get("PCSCHEMATIC_TLB"), "env:PCSCHEMATIC_TLB"),
        (configured.get("tlb"), "config:pcschematic.tlb"),
        (root / "PCSELCAD.TLB" if root else None, "derived:PCSCHEMATIC_ROOT"),
        (root / "PCsELcad.tlb" if root else None, "derived:PCSCHEMATIC_ROOT"),
    ]
    tlb, tlb_source = _first_existing(tlb_candidates)
    record = _record("pcschematic", {"root": (root, root_source), "exe": (exe, exe_source), "tlb": (tlb, tlb_source)}, required=["exe"])
    return _attach_invalid_config(record, [*exe_candidates, *root_candidates, *tlb_candidates])


def discover_toolchains(deep: bool = False) -> dict[str, Any]:
    ansys_family = discover_ansys_family(deep=deep)
    records = {
        "abaqus": discover_abaqus(deep=deep),
        **ansys_family,
        "comsol": discover_comsol(deep=deep),
        "matlab": discover_matlab(deep=deep),
        "pcschematic": discover_pcschematic(deep=deep),
    }
    return {
        "schema_version": "0.1",
        "discovered_at": utc_now(),
        "platform": platform.platform(),
        "deep": deep,
        "solvers": {name: asdict(record) for name, record in records.items()},
        "rules": [
            "Discovery checks executable presence and derived documentation paths; it does not launch heavy solver jobs.",
            "Use private/ai-cae.local.json or environment variables for machine-specific paths.",
            "Status partial means a root or related path was found, but a required executable is missing.",
        ],
    }


def local_config_from_discovery(discovery: dict[str, Any]) -> dict[str, Any]:
    solver_paths: dict[str, dict[str, str]] = {}
    for solver, record in discovery.get("solvers", {}).items():
        paths = record.get("paths", {}) if isinstance(record, dict) else {}
        if paths:
            solver_paths[solver] = {str(key): str(value) for key, value in paths.items()}
    return {
        "runs_root": "runs",
        "allow_model_writes": True,
        "solver_paths": solver_paths,
    }


def write_json(path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"path": str(target), "status": "written"}


def write_local_config(path: str | Path | None = None, deep: bool = False) -> dict[str, Any]:
    target = Path(path) if path else repo_root() / "private" / "ai-cae.local.json"
    discovery = discover_toolchains(deep=deep)
    payload = local_config_from_discovery(discovery)
    result = write_json(target, payload)
    result["discovery"] = discovery
    return result


def _ps_escape(value: str) -> str:
    return value.replace("'", "''")


def write_activation_script(config_path: str | Path | None = None, output_path: str | Path | None = None) -> dict[str, Any]:
    root = repo_root()
    config = Path(config_path) if config_path else root / "private" / "ai-cae.local.json"
    target = Path(output_path) if output_path else root / "private" / "activate-ai-cae.ps1"
    payload = json.loads(config.read_text(encoding="utf-8-sig")) if config.exists() else {"solver_paths": {}}
    solver_paths = payload.get("solver_paths", {})
    env_map = {
        "abaqus": {"command": "ABAQUS_COMMAND"},
        "fluent": {"fluent_exe": "FLUENT_EXE", "root": "FLUENT_ROOT"},
        "ansys": {"root": "ANSYS_ROOT"},
        "workbench": {"workbench_exe": "WORKBENCH_EXE"},
        "comsol": {"root": "COMSOL_ROOT", "batch": "COMSOL_BATCH", "exe": "COMSOL_EXE", "java": "COMSOL_JAVA", "compile": "COMSOL_COMPILE", "mphserver": "COMSOL_MPHSERVER"},
        "matlab": {"root": "MATLABROOT", "matlab_exe": "MATLAB_EXE"},
        "pcschematic": {"root": "PCSCHEMATIC_ROOT", "exe": "PCSCHEMATIC_EXE", "tlb": "PCSCHEMATIC_TLB"},
    }
    lines = [
        "# Generated by ai-cae-toolbox setup. Do not commit this file.",
        f"$env:AI_CAE_TOOLBOX_CONFIG = '{_ps_escape(str(config.resolve()))}'",
    ]
    for solver, mapping in env_map.items():
        values = solver_paths.get(solver, {})
        if not isinstance(values, dict):
            continue
        for key, env_name in mapping.items():
            value = values.get(key)
            if value:
                lines.append(f"$env:{env_name} = '{_ps_escape(str(value))}'")
    lines.append('Write-Host "AI CAE local environment activated."')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"path": str(target), "status": "written", "config_path": str(config)}


def write_codex_mcp_config(output_path: str | Path | None = None) -> dict[str, Any]:
    root = repo_root()
    target = Path(output_path) if output_path else root / "private" / "codex-mcp.local.toml"
    command = root / ".venv" / "Scripts" / "ai-cae-mcp-server.exe"
    if not command.exists():
        command = Path("ai-cae-mcp-server")
    config_path = root / "private" / "ai-cae.local.json"
    text = "\n".join(
        [
            "[mcp_servers.ai-cae-automation-lab]",
            f'command = "{str(command).replace(chr(92), chr(92) + chr(92))}"',
            "args = []",
            "",
            "[mcp_servers.ai-cae-automation-lab.env]",
            f'AI_CAE_TOOLBOX_CONFIG = "{str(config_path.resolve()).replace(chr(92), chr(92) + chr(92))}"',
            "",
        ]
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return {"path": str(target), "status": "written"}


def setup_local(deep: bool = False) -> dict[str, Any]:
    config = write_local_config(deep=deep)
    activation = write_activation_script(config_path=config["path"])
    mcp = write_codex_mcp_config()
    return {
        "status": "ok",
        "local_config": config["path"],
        "activation_script": activation["path"],
        "codex_mcp_config": mcp["path"],
        "discovery": config["discovery"],
    }
