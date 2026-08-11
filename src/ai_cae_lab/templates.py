from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters.comsol import comsol_cube_java_source
from .runs import slugify


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def _abaqus_template(case_name: str) -> dict[str, str]:
    job = slugify(case_name, "abaqus_smoke").replace("-", "_")
    return {
        "scripts/abaqus_smoke.py": f"""
from abaqus import *
from abaqusConstants import *

model_name = "SmokeModel"
job_name = "{job}"

model = mdb.Model(name=model_name)
sketch = model.ConstrainedSketch(name="beam_profile", sheetSize=0.1)
sketch.rectangle(point1=(0.0, 0.0), point2=(0.08, 0.01))
part = model.Part(name="beam_2d", dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
part.BaseShell(sketch=sketch)

model.Material(name="steel_placeholder")
model.materials["steel_placeholder"].Elastic(table=((210e9, 0.3),))
model.HomogeneousSolidSection(name="section", material="steel_placeholder", thickness=0.001)
region = (part.faces,)
part.SectionAssignment(region=region, sectionName="section")

assembly = model.rootAssembly
assembly.Instance(name="beam_2d-1", part=part, dependent=ON)

mdb.Job(name=job_name, model=model_name)
mdb.saveAs(pathName=job_name + ".cae")
print("Abaqus smoke model written:", job_name + ".cae")
""",
        "inputs/README.md": """
# Abaqus Smoke Inputs

This smoke template checks whether Abaqus/CAE can run a noGUI Python script and
write a small CAE file. It is not an engineering validation case.
""",
    }


def _fluent_template(case_name: str) -> dict[str, str]:
    return {
        "scripts/fluent_connection_probe.jou": """
/file/set-batch-options yes
/report/system/proc-stats
/file/write-transcript logs/fluent_transcript.log
/file/stop-transcript
/exit yes
""",
        "inputs/README.md": """
# Fluent Smoke Inputs

The journal is a conservative connection probe. Replace it with a solver-native
journal that reads a mesh, sets models, initializes, iterates, and exports data.
""",
    }


def _workbench_template(case_name: str) -> dict[str, str]:
    return {
        "scripts/workbench_connection_probe.wbjn": """
import os
print("Workbench connection probe")
print("cwd=" + os.getcwd())
""",
        "inputs/README.md": """
# Workbench Smoke Inputs

This journal only validates batch journal execution. Add project import, update,
solve, and archive commands for real workflows.
""",
    }


def _comsol_template(case_name: str) -> dict[str, str]:
    class_name = "".join(part.capitalize() for part in slugify(case_name, "comsol-smoke").split("-"))
    class_name = class_name if class_name and class_name[0].isalpha() else "ComsolSmoke"
    output_name = slugify(case_name, "comsol-smoke") + ".mph"
    return {
        f"scripts/{class_name}.java": comsol_cube_java_source(class_name=class_name, output_file=f"../outputs/{output_name}"),
        "inputs/README.md": """
# COMSOL Smoke Inputs

This template builds a real 10 mm cube with the COMSOL Java API, assigns a
simple material, generates a mesh, and saves an `.mph` file. It is a connection
and model-construction smoke test, not an engineering validation case.
""",
    }


def _matlab_template(case_name: str) -> dict[str, str]:
    return {
        "scripts/matlab_connection_probe.m": """
disp("MATLAB connection probe");
disp(version);
exit;
""",
        "inputs/README.md": "# MATLAB Smoke Inputs\n\nReplace the probe with a Simulink or MATLAB model script.",
    }


def _openfoam_template(case_name: str) -> dict[str, str]:
    return {
        "scripts/openfoam_probe.sh": """
#!/usr/bin/env bash
set -euo pipefail
echo "OpenFOAM connection probe"
command -v blockMesh || true
command -v checkMesh || true
""",
        "inputs/README.md": """
# OpenFOAM Smoke Inputs

Add a minimal case folder with `system`, `constant`, and `0` directories before
running blockMesh/checkMesh.
""",
    }


def _paraview_template(case_name: str) -> dict[str, str]:
    return {
        "scripts/paraview_connection_probe.py": """
import paraview.simple as pv
print("ParaView connection probe")
print("active view:", pv.GetActiveView())
""",
        "inputs/README.md": "# ParaView Smoke Inputs\n\nUse pvpython to load a result file and export screenshots.",
    }


def _aedt_template(case_name: str) -> dict[str, str]:
    return {
        "scripts/aedt_connection_probe.py": """
from ansys.aedt.core import Desktop

desktop = Desktop(new_desktop=True, non_graphical=True, close_on_exit=True)
print("AEDT_PYAEDT_SMOKE_OK")
print("version=" + str(desktop.aedt_version_id))
desktop.release_desktop(close_projects=True, close_desktop=True)
""",
        "inputs/README.md": """
# AEDT Smoke Inputs

This imports PyAEDT and starts a disposable AEDT session. It does not build or
solve an electromagnetic model. A real workflow must record the design type,
solution setup, mesh/adaptive passes, field plots, tables, and project file.
""",
    }


def _mechanical_template(case_name: str) -> dict[str, str]:
    return {
        "scripts/mechanical_probe.py": """
import json
from ansys.mechanical.core import launch_mechanical

mechanical = launch_mechanical(batch=True, cleanup_on_exit=True)
try:
    result = mechanical.run_python_script(
        'import json\\n'
        'print(json.dumps({"application_version": str(ExtAPI.ApplicationVersion), '
        '"analysis_count": len(Model.Analyses)}))'
    )
    print("PYMECHANICAL_SMOKE_OK")
    print(result)
finally:
    mechanical.exit(force=True)
""",
        "inputs/README.md": """
# Mechanical Smoke Inputs

This checks a disposable PyMechanical gRPC session. It is not structural solve
evidence. A solved workflow must additionally prove Mechanical `Solved` state,
MAPDL normal termination, reaction balance, mesh metrics, RST, numeric exports,
and result images.
""",
    }


def _hypermesh_template(case_name: str) -> dict[str, str]:
    return {
        "scripts/hypermesh_smoke.tcl": """
puts "HYPERMESH_MCP_SMOKE_TEST_BEGIN"
puts "HYPERMESH_MCP_SMOKE_TEST_OK"
puts "HYPERMESH_MCP_SMOKE_TEST_END"
""",
        "inputs/README.md": """
# HyperMesh Smoke Inputs

Run this explicit Tcl file with `hmbatch -tcl`. It checks the batch bridge only;
it does not prove CAD import, mesh creation, quality acceptance, or solver-deck export.
""",
    }


def _lammps_template(case_name: str) -> dict[str, str]:
    return {
        "scripts/in.lammps_smoke": """
units metal
atom_style atomic
lattice fcc 3.615
region box block 0 2 0 2 0 2
create_box 1 box
create_atoms 1 box
mass 1 63.546
pair_style zero 8.0
pair_coeff * *
thermo 1
run 0
print "LAMMPS_SMOKE_TEST_OK"
""",
        "inputs/README.md": """
# LAMMPS Smoke Inputs

This zero-potential run checks parser and executable availability without an
external interatomic-potential file. It is not a calibrated materials simulation.
""",
    }


def _ovito_template(case_name: str) -> dict[str, str]:
    return {
        "scripts/ovito_connection_probe.py": """
import ovito
from ovito.io import import_file

pipeline = import_file.__module__
print("OVITO_PYTHON_SMOKE_OK")
print("version=" + str(getattr(ovito, "version_string", "version-unavailable")))
print("pipeline_module=" + pipeline)
""",
        "inputs/README.md": """
# OVITO Smoke Inputs

This imports the OVITO Python package. OVITO Basic GUI installations may not
include `ovitos`; configure an external compatible Python environment when needed.
""",
    }


TEMPLATE_BUILDERS = {
    "aedt": _aedt_template,
    "abaqus": _abaqus_template,
    "fluent": _fluent_template,
    "ansys-workbench": _workbench_template,
    "ansys-mechanical": _mechanical_template,
    "hypermesh": _hypermesh_template,
    "lammps": _lammps_template,
    "ovito": _ovito_template,
    "comsol": _comsol_template,
    "matlab": _matlab_template,
    "openfoam": _openfoam_template,
    "paraview": _paraview_template,
}


def write_solver_smoke_template(
    solver: str,
    run_dir: str | Path,
    case_name: str = "smoke-test",
    overwrite: bool = False,
) -> dict[str, Any]:
    solver_key = solver.strip().lower()
    builder = TEMPLATE_BUILDERS.get(solver_key)
    if builder is None:
        return {
            "status": "unsupported",
            "solver": solver_key,
            "message": f"No smoke template is registered for {solver_key}.",
        }

    root = Path(run_dir)
    written: list[str] = []
    skipped: list[str] = []
    for relative, text in builder(case_name).items():
        target = root / relative
        if target.exists() and not overwrite:
            skipped.append(str(target))
            continue
        _write(target, text)
        written.append(str(target))

    return {
        "status": "ok",
        "solver": solver_key,
        "run_dir": str(root),
        "written": written,
        "skipped": skipped,
    }
