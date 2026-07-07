from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .adapters import known_adapters
from .adapters.abaqus import abaqus_run_no_gui, abaqus_submit_inp
from .adapters.ansys import ansys_check_install, ansys_run_workbench_journal
from .adapters.comsol import comsol_check_install, comsol_run_batch
from .adapters.fluent import fluent_run_journal
from .adapters.pcschematic import pcschematic_check_install
from .env_check import run_checks
from .evidence import scan_evidence
from .report import generate_report
from .runs import create_run
from .skills import list_skill_packs


def _load_fastmcp() -> Any:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise SystemExit(
            "The MCP server extra is not installed. Run: python -m pip install -e .[mcp]"
        ) from exc
    return FastMCP


def build_server() -> Any:
    FastMCP = _load_fastmcp()
    server = FastMCP("ai-cae-automation-lab")

    @server.tool()
    def env_check() -> list[dict[str, Any]]:
        """Check local CAE automation paths without starting commercial solvers."""
        return [asdict(item) for item in run_checks()]

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
    def scan_run_evidence(run_dir: str) -> dict[str, Any]:
        """Scan logs, scripts, solver outputs, exported data, and reports in a run directory."""
        return scan_evidence(run_dir, write=True)

    @server.tool()
    def generate_run_report(run_dir: str) -> dict[str, Any]:
        """Generate report.md for a run directory based on its evidence inventory."""
        return generate_report(run_dir)

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

    @server.tool()
    def ansys_check_installation(
        ansys_root: str | None = None,
        fluent_exe: str | None = None,
        workbench_exe: str | None = None,
    ) -> dict[str, Any]:
        """Check configured Ansys root, Fluent, and Workbench paths without launching products."""
        return ansys_check_install(ansys_root, fluent_exe, workbench_exe)

    @server.tool()
    def ansys_run_workbench_journal_file(
        journal_path: str,
        run_dir: str,
        workbench_command: str | None = None,
        timeout_sec: int = 7200,
    ) -> dict[str, Any]:
        """Run an Ansys Workbench journal in batch mode and write command output to logs."""
        return ansys_run_workbench_journal(journal_path, run_dir, workbench_command, timeout_sec)

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
