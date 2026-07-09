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


TEMPLATE_BUILDERS = {
    "abaqus": _abaqus_template,
    "fluent": _fluent_template,
    "ansys-workbench": _workbench_template,
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
