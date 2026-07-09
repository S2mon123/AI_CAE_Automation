from __future__ import annotations

import os
from dataclasses import asdict
from typing import Any

from .adapters import known_adapters
from .adapters.abaqus import abaqus_run_no_gui, abaqus_submit_inp
from .adapters.ansys import ansys_check_install, ansys_run_workbench_journal
from .adapters.comsol import (
    comsol_check_install,
    comsol_compile_java,
    comsol_run_batch,
    comsol_run_compiled_class,
    comsol_run_java_model_to_mph,
    comsol_validate_mph_loadable,
    write_comsol_cube_java,
    write_comsol_mph_validator_java,
)
from .adapters.fluent import fluent_run_journal
from .adapters.matlab import matlab_check_install, matlab_run_script
from .adapters.openfoam import openfoam_check_install, openfoam_run_command
from .adapters.paraview import paraview_check_install, paraview_run_script
from .adapters.pcschematic import pcschematic_check_install
from .config import bridge_plan, toolchain_paths
from .context_scope import solver_context_scope as build_solver_context_scope
from .discovery import (
    discover_toolchains as discover_local_toolchains,
    setup_local as setup_local_toolchain_files,
    write_activation_script as write_activation_script_file,
    write_codex_mcp_config as write_codex_mcp_config_file,
    write_local_config as write_local_toolchain_config_file,
)
from .env_check import run_checks
from .evidence import scan_evidence
from .report import generate_report
from .runs import create_run
from .skills import list_skill_packs
from .templates import write_solver_smoke_template as write_solver_template

SOLVER_ALIASES = {
    "abaqus": {"abaqus"},
    "ansys": {"ansys", "fluent", "workbench"},
    "ansys-workbench": {"ansys", "workbench"},
    "workbench": {"ansys", "workbench"},
    "fluent": {"ansys", "fluent"},
    "comsol": {"comsol"},
    "matlab": {"matlab"},
    "openfoam": {"openfoam"},
    "paraview": {"paraview"},
    "pcschematic": {"pcschematic"},
    "pc-schematic": {"pcschematic"},
}


def _load_fastmcp() -> Any:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise SystemExit(
            "The MCP server extra is not installed. Run: python -m pip install -e .[mcp]"
        ) from exc
    return FastMCP


def normalize_active_solvers(value: str | list[str] | tuple[str, ...] | set[str] | None) -> set[str] | None:
    """Return normalized solver profile names.

    `None`, empty, `all`, or `*` means the full toolbox server.
    """
    if value is None:
        return None
    if isinstance(value, str):
        raw_items = [item.strip().lower() for item in value.replace(";", ",").split(",")]
    else:
        raw_items = [str(item).strip().lower() for item in value]
    raw_items = [item for item in raw_items if item]
    if not raw_items or any(item in {"all", "*"} for item in raw_items):
        return None
    normalized: set[str] = set()
    for item in raw_items:
        normalized.update(SOLVER_ALIASES.get(item, {item}))
    return normalized


def _env_active_solvers() -> set[str] | None:
    return normalize_active_solvers(os.environ.get("AI_CAE_MCP_SOLVERS"))


def _solver_enabled(active: set[str] | None, *names: str) -> bool:
    if active is None:
        return True
    requested = normalize_active_solvers(list(names))
    return bool(requested and active.intersection(requested))


def _server_name(active: set[str] | None) -> str:
    if active is None:
        return "ai-cae-automation-lab"
    return "ai-cae-automation-lab-" + "-".join(sorted(active))


def build_server(active_solvers: str | list[str] | tuple[str, ...] | set[str] | None = None) -> Any:
    FastMCP = _load_fastmcp()
    active = normalize_active_solvers(active_solvers) if active_solvers is not None else _env_active_solvers()
    server = FastMCP(_server_name(active))

    @server.tool()
    def env_check(deep: bool = False) -> list[dict[str, Any]]:
        """Check local CAE automation paths without starting commercial solvers."""
        return [asdict(item) for item in run_checks(deep=deep)]

    @server.tool()
    def discover_toolchains(deep: bool = False) -> dict[str, Any]:
        """Discover local CAE toolchains from environment variables, PATH, registry, and common install roots."""
        return discover_local_toolchains(deep=deep)

    @server.tool()
    def setup_local_toolchain(deep: bool = False) -> dict[str, Any]:
        """Run first-time setup and write ignored private local config, activation script, and Codex MCP TOML."""
        return setup_local_toolchain_files(deep=deep)

    @server.tool()
    def write_local_toolchain_config(path: str | None = None, deep: bool = False) -> dict[str, Any]:
        """Write private/ai-cae.local.json from current discovery results."""
        return write_local_toolchain_config_file(path=path, deep=deep)

    @server.tool()
    def write_toolchain_activation_script(
        config_path: str | None = None,
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """Write a PowerShell script that exports discovered solver paths as environment variables."""
        return write_activation_script_file(config_path=config_path, output_path=output_path)

    @server.tool()
    def write_codex_mcp_config(output_path: str | None = None) -> dict[str, Any]:
        """Write a local Codex MCP TOML snippet for this toolbox server."""
        return write_codex_mcp_config_file(output_path=output_path)

    @server.tool()
    def list_codex_skills() -> list[dict[str, Any]]:
        """List public Codex skill packs shipped by this repository."""
        return list_skill_packs()

    @server.tool()
    def list_solver_adapters() -> list[dict[str, Any]]:
        """List planned and implemented solver adapter capabilities."""
        return [asdict(item) for item in known_adapters()]

    @server.tool()
    def create_run_record(
        solver: str,
        case_name: str,
        objective: str = "",
        root: str = "runs",
        tags_csv: str = "",
    ) -> dict[str, Any]:
        """Create a traceable local run directory with run.json and run.log."""
        tags = [tag.strip() for tag in tags_csv.split(",") if tag.strip()]
        return create_run(root=root, solver=solver, case_name=case_name, objective=objective, tags=tags)

    @server.tool()
    def solver_context_scope(
        solver: str,
        include_common: bool = True,
    ) -> dict[str, Any]:
        """Return the minimal repo context an agent should read for one solver task."""
        return build_solver_context_scope(solver=solver, include_common=include_common)

    @server.tool()
    def solver_toolchain_paths(
        solver: str,
        config_path: str | None = None,
    ) -> dict[str, Any]:
        """Explain how executable paths should be resolved on the current user's machine."""
        return toolchain_paths(solver=solver, config_path=config_path)
    @server.tool()
    def solver_bridge_plan(
        solver: str,
        objective: str = "",
        config_path: str | None = None,
    ) -> dict[str, Any]:
        """Return a structured bridge plan for a solver without launching it."""
        return bridge_plan(solver=solver, objective=objective, config_path=config_path)

    @server.tool()
    def write_solver_smoke_template(
        solver: str,
        run_dir: str,
        case_name: str = "smoke-test",
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Write a small solver-native smoke template into a run directory."""
        return write_solver_template(solver, run_dir, case_name, overwrite)

    @server.tool()
    def scan_run_evidence(run_dir: str) -> dict[str, Any]:
        """Scan logs, scripts, solver outputs, exported data, and reports in a run directory."""
        return scan_evidence(run_dir, write=True)

    @server.tool()
    def generate_run_report(run_dir: str) -> dict[str, Any]:
        """Generate report.md for a run directory based on its evidence inventory."""
        return generate_report(run_dir)

    if _solver_enabled(active, "abaqus"):
        @server.tool()
        def abaqus_run_no_gui_script(
            script_path: str,
            run_dir: str,
            abaqus_command: str | None = None,
            timeout_sec: int = 3600,
        ) -> dict[str, Any]:
            """Run an Abaqus/CAE Python script with noGUI and write a run log."""
            return abaqus_run_no_gui(script_path, run_dir, abaqus_command, timeout_sec)

        @server.tool()
        def abaqus_submit_input_deck(
            input_path: str,
            run_dir: str,
            job_name: str,
            abaqus_command: str | None = None,
            timeout_sec: int = 7200,
        ) -> dict[str, Any]:
            """Submit an Abaqus input deck and write command output to logs."""
            return abaqus_submit_inp(input_path, run_dir, job_name, abaqus_command, timeout_sec)

    if _solver_enabled(active, "fluent"):
        @server.tool()
        def fluent_run_journal_file(
            journal_path: str,
            run_dir: str,
            fluent_command: str | None = None,
            dimension: str = "3ddp",
            timeout_sec: int = 7200,
        ) -> dict[str, Any]:
            """Run a Fluent journal in batch mode and write command output to logs."""
            return fluent_run_journal(journal_path, run_dir, fluent_command, dimension, timeout_sec)

    if _solver_enabled(active, "ansys", "fluent", "workbench"):
        @server.tool()
        def ansys_check_installation(
            ansys_root: str | None = None,
            fluent_exe: str | None = None,
            workbench_exe: str | None = None,
        ) -> dict[str, Any]:
            """Check configured Ansys root, Fluent, and Workbench paths without launching products."""
            return ansys_check_install(ansys_root, fluent_exe, workbench_exe)

    if _solver_enabled(active, "workbench"):
        @server.tool()
        def ansys_run_workbench_journal_file(
            journal_path: str,
            run_dir: str,
            workbench_command: str | None = None,
            timeout_sec: int = 7200,
        ) -> dict[str, Any]:
            """Run an Ansys Workbench journal in batch mode and write command output to logs."""
            return ansys_run_workbench_journal(journal_path, run_dir, workbench_command, timeout_sec)

    if _solver_enabled(active, "comsol"):
        @server.tool()
        def comsol_check_installation(
            comsol_root: str | None = None,
            comsol_batch: str | None = None,
            java_path: str | None = None,
        ) -> dict[str, Any]:
            """Check COMSOL batch, Java, and local API docs without launching COMSOL."""
            return comsol_check_install(comsol_root, comsol_batch, java_path)

        @server.tool()
        def comsol_run_batch_file(
            run_dir: str,
            input_file: str | None = None,
            output_file: str | None = None,
            comsol_batch: str | None = None,
            extra_args: list[str] | None = None,
            timeout_sec: int = 7200,
        ) -> dict[str, Any]:
            """Run a configured COMSOL batch command and write command output to logs."""
            return comsol_run_batch(run_dir, input_file, output_file, comsol_batch, extra_args, timeout_sec)

        @server.tool()
        def comsol_compile_java_file(
            java_file: str,
            run_dir: str,
            comsol_compile: str | None = None,
            timeout_sec: int = 1800,
        ) -> dict[str, Any]:
            """Compile a COMSOL Java API file with comsolcompile and capture logs."""
            return comsol_compile_java(java_file, run_dir, comsol_compile, timeout_sec)

        @server.tool()
        def comsol_run_compiled_java_class(
            class_file: str,
            run_dir: str,
            output_file: str | None = None,
            comsol_batch: str | None = None,
            extra_args: list[str] | None = None,
            timeout_sec: int = 7200,
        ) -> dict[str, Any]:
            """Run a compiled COMSOL Java class through comsolbatch and capture logs."""
            return comsol_run_compiled_class(class_file, run_dir, output_file, comsol_batch, extra_args, timeout_sec)

        @server.tool()
        def comsol_write_cube_smoke_java(
            target_path: str,
            class_name: str = "ComsolCube10mm",
            output_file: str = "../outputs/comsol_cube_10mm.mph",
            overwrite: bool = False,
        ) -> dict[str, Any]:
            """Write a 10 mm COMSOL Java API cube smoke model without launching COMSOL."""
            return write_comsol_cube_java(target_path, class_name, output_file, overwrite)

        @server.tool()
        def comsol_run_java_model_to_mph_file(
            java_file: str,
            run_dir: str,
            output_file: str | None = None,
            comsol_compile: str | None = None,
            comsol_batch: str | None = None,
            timeout_sec: int = 7200,
        ) -> dict[str, Any]:
            """Compile a COMSOL Java API model and run it through COMSOL batch to create an MPH file."""
            return comsol_run_java_model_to_mph(
                java_file,
                run_dir,
                output_file=output_file,
                comsol_compile=comsol_compile,
                comsol_batch=comsol_batch,
                timeout_sec=timeout_sec,
            )

        @server.tool()
        def comsol_write_mph_validator_java(
            target_path: str,
            class_name: str = "ValidateMphLoadable",
            overwrite: bool = False,
        ) -> dict[str, Any]:
            """Write a small COMSOL Java API validator that loads an MPH file and optionally saves a checked copy."""
            return write_comsol_mph_validator_java(target_path, class_name, overwrite)

        @server.tool()
        def comsol_validate_mph_loadable_file(
            mph_file: str,
            run_dir: str,
            validated_copy: str | None = None,
            comsol_compile: str | None = None,
            comsol_batch: str | None = None,
            timeout_sec: int = 3600,
        ) -> dict[str, Any]:
            """Compile and run a COMSOL Java validator that loads an MPH file through the COMSOL API."""
            return comsol_validate_mph_loadable(
                mph_file,
                run_dir,
                validated_copy=validated_copy,
                comsol_compile=comsol_compile,
                comsol_batch=comsol_batch,
                timeout_sec=timeout_sec,
            )

    if _solver_enabled(active, "matlab"):
        @server.tool()
        def matlab_check_installation(
            matlab_command: str | None = None,
            matlab_root: str | None = None,
        ) -> dict[str, Any]:
            """Check configured MATLAB paths without launching MATLAB."""
            return matlab_check_install(matlab_command, matlab_root)

        @server.tool()
        def matlab_run_script_file(
            script_path: str,
            run_dir: str,
            matlab_command: str | None = None,
            timeout_sec: int = 3600,
        ) -> dict[str, Any]:
            """Run a MATLAB script in batch mode and capture logs."""
            return matlab_run_script(script_path, run_dir, matlab_command, timeout_sec)

    if _solver_enabled(active, "openfoam"):
        @server.tool()
        def openfoam_check_installation(openfoam_root: str | None = None) -> dict[str, Any]:
            """Check OpenFOAM command paths or WSL availability without running a case."""
            return openfoam_check_install(openfoam_root)

        @server.tool()
        def openfoam_run_case_command(
            command_name: str,
            case_dir: str,
            run_dir: str,
            timeout_sec: int = 3600,
        ) -> dict[str, Any]:
            """Run a selected OpenFOAM command against a case directory."""
            return openfoam_run_command(command_name, case_dir, run_dir, timeout_sec)

    if _solver_enabled(active, "paraview"):
        @server.tool()
        def paraview_check_installation(
            pvpython: str | None = None,
            paraview_root: str | None = None,
        ) -> dict[str, Any]:
            """Check pvpython or ParaView root paths without launching the GUI."""
            return paraview_check_install(pvpython, paraview_root)

        @server.tool()
        def paraview_run_pvpython_script(
            script_path: str,
            run_dir: str,
            pvpython: str | None = None,
            timeout_sec: int = 3600,
        ) -> dict[str, Any]:
            """Run a pvpython postprocessing script and capture logs."""
            return paraview_run_script(script_path, run_dir, pvpython, timeout_sec)

    if _solver_enabled(active, "pcschematic"):
        @server.tool()
        def pcschematic_check_installation(
            exe_path: str | None = None,
            root_path: str | None = None,
            tlb_path: str | None = None,
        ) -> dict[str, Any]:
            """Check PCSCHEMATIC configured paths without launching or modifying the installation."""
            return pcschematic_check_install(exe_path, root_path, tlb_path)

    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
