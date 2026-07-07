from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AdapterCapability:
    name: str
    description: str


@dataclass(frozen=True)
class SolverAdapterInfo:
    name: str
    maturity: str
    env_vars: tuple[str, ...] = field(default_factory=tuple)
    capabilities: tuple[AdapterCapability, ...] = field(default_factory=tuple)
    notes: str = ""


def known_adapters() -> list[SolverAdapterInfo]:
    return [
        SolverAdapterInfo(
            name="abaqus",
            maturity="minimal",
            env_vars=("ABAQUS_COMMAND",),
            capabilities=(
                AdapterCapability("run_no_gui", "Run an Abaqus/CAE Python script with noGUI."),
                AdapterCapability("submit_job", "Run an Abaqus job from an input deck."),
                AdapterCapability("read_status", "Read status files and logs."),
            ),
            notes="Public adapter should keep user models and ODB files out of git.",
        ),
        SolverAdapterInfo(
            name="fluent",
            maturity="minimal",
            env_vars=("FLUENT_EXE", "FLUENT_ROOT"),
            capabilities=(
                AdapterCapability("run_journal", "Run a Fluent journal in batch mode."),
                AdapterCapability("export_plots", "Export images and numeric summaries."),
            ),
            notes="Start with journal execution before GUI automation.",
        ),
        SolverAdapterInfo(
            name="ansys-workbench",
            maturity="minimal",
            env_vars=("ANSYS_ROOT", "WORKBENCH_EXE", "ANSYS_WORKBENCH_EXE"),
            capabilities=(
                AdapterCapability("check_install", "Verify configured Ansys root, Fluent, and Workbench paths."),
                AdapterCapability("run_workbench_journal", "Run a Workbench journal in batch mode."),
            ),
            notes="Workbench adapters should write logs and avoid modifying original project files.",
        ),
        SolverAdapterInfo(
            name="comsol",
            maturity="minimal",
            env_vars=("COMSOL_ROOT", "COMSOL_BATCH", "COMSOL_EXE", "COMSOL_JAVA"),
            capabilities=(
                AdapterCapability("check_install", "Verify COMSOL batch, Java, and local API docs."),
                AdapterCapability("run_batch", "Run a configured COMSOL batch command."),
            ),
            notes="Java API scripts should be treated as setup evidence until COMSOL logs and MPH exports exist.",
        ),
        SolverAdapterInfo(
            name="pcschematic",
            maturity="minimal",
            env_vars=("PCSCHEMATIC_EXE", "PCSCHEMATIC_ROOT", "PCSCHEMATIC_TLB"),
            capabilities=(
                AdapterCapability("check_install", "Verify configured local files exist."),
                AdapterCapability("check_com", "Verify COM/OLE registration and local files."),
                AdapterCapability("export_lists", "Export component, terminal, and cable evidence."),
            ),
            notes="Never publish proprietary symbol libraries, databases, or generated customer projects.",
        ),
    ]
