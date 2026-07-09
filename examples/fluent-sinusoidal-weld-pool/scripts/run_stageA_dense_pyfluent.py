from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path


def add_pyfluent_core(path_value: str | None) -> None:
    if path_value:
        path = Path(path_value)
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))


def stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def center_at_time(t_s: float, v: float = 0.003, amp: float = 0.003, freq: float = 2.0) -> dict:
    y = amp * math.sin(2.0 * math.pi * freq * t_s)
    return {"time_s": t_s, "x_mm": v * t_s * 1000.0, "y_mm": y * 1000.0}


def step(result: dict, label: str, func, required: bool = True):
    print(f"\n--- {label} ---", flush=True)
    entry = {"label": label, "status": "not-started"}
    result["steps"].append(entry)
    try:
        value = func()
        entry["status"] = "ok"
        entry["value"] = value
        print(f"{label}: OK", flush=True)
        return value
    except Exception as exc:
        entry["status"] = "failed"
        entry["error"] = repr(exc)
        entry["traceback"] = traceback.format_exc()
        print(f"{label}: FAILED {exc!r}", flush=True)
        if required:
            raise
        return None


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Stage A dense sinusoidal weld-pool validation with PyFluent.")
    parser.add_argument("--workdir", default=os.environ.get("WELD_POOL_WORKDIR", "runs/stageA3c"))
    parser.add_argument("--fluent-exe", default=os.environ.get("FLUENT_EXE"))
    parser.add_argument("--pyfluent-core", default=os.environ.get("PYFLUENT_CORE"))
    parser.add_argument("--product-version", default="25.2.0")
    parser.add_argument("--base-case", default="stageA_probe_volume_only.cas.h5")
    parser.add_argument("--udf-source", default="moving_heat_source_sinusoidal.c")
    parser.add_argument("--udf-library", default="libudf_stageA3")
    parser.add_argument("--udf-profile", default="moving_heat_source_sinusoidal")
    parser.add_argument("--compile-udf", action="store_true")
    parser.add_argument("--wall-name", default="default_exterior-1")
    parser.add_argument("--cell-zone", default="fluid-1")
    parser.add_argument("--time-step", type=float, default=0.05)
    parser.add_argument("--save-interval", type=float, default=0.10)
    parser.add_argument("--total-time", type=float, default=10.0)
    parser.add_argument("--max-iter-per-step", type=int, default=3)
    parser.add_argument("--processors", type=int, default=2)
    args = parser.parse_args()

    add_pyfluent_core(args.pyfluent_core)
    import ansys.fluent.core as pyfluent  # noqa: PLC0415

    workdir = Path(args.workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    base_case = (workdir / args.base_case).resolve()
    udf_source = (workdir / args.udf_source).resolve()
    case_out = workdir / "stageA3c_dense_q1000.cas.h5"
    summary_json = workdir / "stageA3c_dense_q1000_run_summary.json"
    summary_csv = workdir / "stageA3c_dense_q1000_summary.csv"

    total_steps = int(round(args.total_time / args.time_step))
    save_every = max(1, int(round(args.save_interval / args.time_step)))
    checkpoint_steps = list(range(save_every, total_steps + 1, save_every))

    result = {
        "status": "not-started",
        "started": stamp(),
        "pyfluent_version": getattr(pyfluent, "__version__", "unknown"),
        "workdir": str(workdir),
        "base_case": str(base_case),
        "steps": [],
        "snapshots": [],
        "time_step_s": args.time_step,
        "save_interval_s": args.save_interval,
        "total_steps": total_steps,
        "max_iter_per_step": args.max_iter_per_step,
        "heat_source": {"Q_W": 1000.0, "v_m_per_s": 0.003, "A_m": 0.003, "freq_Hz": 2.0, "r_beam_m": 0.003},
    }
    rows: list[dict] = []
    solver = None
    current_step = 0
    try:
        if not base_case.exists():
            raise FileNotFoundError(f"Base case not found: {base_case}")
        if args.compile_udf and not udf_source.exists():
            raise FileNotFoundError(f"UDF source not found: {udf_source}")

        launch_kwargs = {
            "product_version": args.product_version,
            "dimension": 3,
            "precision": "double",
            "processor_count": args.processors,
            "mode": "solver",
            "cwd": str(workdir),
            "start_transcript": True,
            "additional_arguments": "-g",
            "start_timeout": 120,
            "start_watchdog": False,
        }
        if args.fluent_exe:
            launch_kwargs["fluent_path"] = args.fluent_exe
        solver = pyfluent.launch_fluent(**launch_kwargs)

        step(result, "read base case", lambda: solver.settings.file.read_case(file_name=str(base_case)))
        step(result, "mesh check", solver.settings.mesh.check)
        step(result, "mesh quality", solver.settings.mesh.quality)
        step(result, "set unsteady first order", lambda: setattr(solver.settings.setup.general.solver, "time", "unsteady-1st-order"))
        step(result, "enable energy", lambda: setattr(solver.settings.setup.models.energy, "enabled", True))
        step(result, "set laminar model", lambda: setattr(solver.settings.setup.models.viscous, "model", "laminar"))
        step(result, "create steel material", lambda: solver.settings.setup.materials.fluid.create("aisi_1045_steel"), required=False)
        steel = solver.settings.setup.materials.fluid["aisi_1045_steel"]
        step(result, "set steel base properties", lambda: steel.set_state({
            "density": {"option": "value", "value": 7850.0},
            "specific_heat": {"option": "value", "value": 475.0},
            "thermal_conductivity": {"option": "value", "value": 50.0},
            "viscosity": {"option": "value", "value": 0.006},
        }))
        step(result, "enable solidification melting", lambda: solver.tui.define.models.solidification_melting("yes"))
        step(result, "set steel melting properties", lambda: steel.set_state({
            "melting_heat": {"option": "value", "value": 250000.0},
            "tsolidus": {"option": "value", "value": 1693.15},
            "tliqidus": {"option": "value", "value": 1733.15},
        }))
        step(result, "assign steel material", lambda: solver.settings.setup.cell_zone_conditions.fluid[args.cell_zone].general.set_state({"material": "aisi_1045_steel"}))

        if args.compile_udf:
            step(result, "compile UDF", lambda: solver.settings.setup.user_defined.compiled_udf(
                library_name=args.udf_library,
                source_files=[str(udf_source)],
                header_files=[],
                use_built_in_compiler=True,
            ))
        step(result, "load UDF library", lambda: solver.settings.setup.user_defined.manage.load(udf_library_name=args.udf_library))
        wall = solver.settings.setup.boundary_conditions.wall[args.wall_name]
        step(result, "hook moving heat source UDF", lambda: wall.thermal.heat_flux.set_state({"option": "udf", "value": args.udf_profile}))
        step(result, "write configured case", lambda: solver.settings.file.write_case(file_name=str(case_out)))

        tc = solver.settings.solution.run_calculation.transient_controls
        step(result, "set time step size", lambda: setattr(tc, "time_step_size", args.time_step))
        step(result, "set max iter per time step", lambda: setattr(tc, "max_iter_per_time_step", args.max_iter_per_step))
        step(result, "hybrid initialize", solver.settings.solution.initialization.hybrid_initialize)

        for target_step in checkpoint_steps:
            chunk = target_step - current_step
            step(result, f"run to dense step {target_step}", lambda n=chunk: solver.settings.solution.run_calculation.dual_time_iterate(
                time_step_count=n,
                max_iter_per_step=args.max_iter_per_step,
            ))
            current_step = target_step
            t_s = current_step * args.time_step
            tag = f"t{t_s:05.2f}".replace(".", "p")
            data_path = workdir / f"stageA3c_dense_q1000_{tag}.dat.h5"
            step(result, f"write dense data {tag}", lambda p=data_path: solver.settings.file.write_data(file_name=str(p)))
            center = center_at_time(t_s)
            result["snapshots"].append({"step": current_step, "time_s": t_s, "center": center, "data": str(data_path)})
            if current_step == checkpoint_steps[0] or current_step % max(save_every * 10, 1) == 0:
                rows.append({"step": current_step, **center, "data": str(data_path)})

        result["status"] = "ok"
        result["finished"] = stamp()
        return 0
    except Exception as exc:
        result["status"] = "failed"
        result["error"] = repr(exc)
        result["traceback"] = traceback.format_exc()
        print(traceback.format_exc(), flush=True)
        return 1
    finally:
        write_csv(summary_csv, rows)
        summary_json.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        if solver is not None:
            try:
                solver.exit()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
