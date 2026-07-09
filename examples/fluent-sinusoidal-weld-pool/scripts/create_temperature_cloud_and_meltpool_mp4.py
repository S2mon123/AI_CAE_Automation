from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def add_pyfluent_core(path_value: str | None) -> None:
    if path_value:
        path = Path(path_value)
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))


def clean_frame_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for frame in path.glob("frame_*.png"):
        frame.unlink()


def udf_center(t_s: float) -> tuple[float, float]:
    return 3.0 * t_s, 3.0 * math.sin(2.0 * math.pi * 2.0 * t_s)


def time_from_name(path: Path) -> float:
    match = re.search(r"_t(\d+)p(\d+)\.dat\.h5$", path.name)
    if not match:
        raise ValueError(f"Cannot parse time from {path.name}")
    return float(f"{int(match.group(1))}.{match.group(2)}")


def read_cell_fields(case_reader, data_file_cls, data_path: Path, nx: int, ny: int, nz: int) -> tuple[np.ndarray, np.ndarray]:
    df = data_file_cls(data_file_name=str(data_path), case_file_handle=case_reader)
    phase = df.get_phases()[0]
    temperature = np.asarray(df._field_data[phase]["cells"]["SV_T"]["1"][:], dtype=float)
    liquid_fraction = np.asarray(df._field_data[phase]["cells"]["SV_LIQF"]["1"][:], dtype=float)
    return temperature.reshape((nx, ny, nz), order="C"), liquid_fraction.reshape((nx, ny, nz), order="C")


def interp_list(t_s: float, times: np.ndarray, fields: list[np.ndarray], ambient_value: float) -> np.ndarray:
    if t_s <= times[0]:
        alpha = max(0.0, t_s / times[0])
        return np.full_like(fields[0], ambient_value) * (1.0 - alpha) + fields[0] * alpha
    if t_s >= times[-1]:
        return fields[-1]
    right = int(np.searchsorted(times, t_s, side="right"))
    left = right - 1
    alpha = float((t_s - times[left]) / (times[right] - times[left]))
    return fields[left] * (1.0 - alpha) + fields[right] * alpha


def y_section(field_xyz: np.ndarray, y_mm: float, y_centers: np.ndarray) -> np.ndarray:
    if y_mm <= y_centers[0]:
        return field_xyz[:, 0, :]
    if y_mm >= y_centers[-1]:
        return field_xyz[:, -1, :]
    hi = int(np.searchsorted(y_centers, y_mm, side="right"))
    lo = hi - 1
    alpha = float((y_mm - y_centers[lo]) / (y_centers[hi] - y_centers[lo]))
    return field_xyz[:, lo, :] * (1.0 - alpha) + field_xyz[:, hi, :] * alpha


def melt_depth_mm(liq_xz: np.ndarray, z_centers: np.ndarray, threshold: float = 0.5) -> float:
    mask = liq_xz >= threshold
    if not mask.any():
        return 0.0
    deepest_z = float(z_centers[np.where(mask)[1].min()])
    return max(0.0, -deepest_z)


def run_ffmpeg(ffmpeg: Path, frame_dir: Path, out_mp4: Path, fps: int) -> dict:
    tmp = out_mp4.with_suffix(".tmp.mp4")
    if tmp.exists():
        tmp.unlink()
    if out_mp4.exists():
        out_mp4.unlink()
    codec = "libopenh264"
    cmd = [
        str(ffmpeg), "-y", "-framerate", str(fps), "-i", str(frame_dir / "frame_%04d.png"),
        "-c:v", codec, "-b:v", "8M", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(tmp),
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-4000:])
    shutil.move(str(tmp), str(out_mp4))
    return {"returncode": proc.returncode, "stderr_tail": proc.stderr[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create temperature-cloud and melt-pool section MP4s from dense Fluent data.")
    parser.add_argument("--workdir", default=os.environ.get("WELD_POOL_WORKDIR", "runs/stageA3c"))
    parser.add_argument("--case", default="stageA3c_dense_q1000.cas.h5")
    parser.add_argument("--data-glob", default="stageA3c_dense_q1000_t*.dat.h5")
    parser.add_argument("--pyfluent-core", default=os.environ.get("PYFLUENT_CORE"))
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG_EXE", "ffmpeg"))
    parser.add_argument("--nx", type=int, default=60)
    parser.add_argument("--ny", type=int, default=40)
    parser.add_argument("--nz", type=int, default=12)
    parser.add_argument("--lx-mm", type=float, default=30.0)
    parser.add_argument("--ly-mm", type=float, default=20.0)
    parser.add_argument("--lz-mm", type=float, default=6.0)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--duration", type=float, default=10.0)
    args = parser.parse_args()

    add_pyfluent_core(args.pyfluent_core)
    from ansys.fluent.core.filereader.case_file import CaseFile  # noqa: PLC0415
    from ansys.fluent.core.filereader.data_file import DataFile  # noqa: PLC0415

    workdir = Path(args.workdir).resolve()
    case_path = (workdir / args.case).resolve()
    data_paths = sorted(workdir.glob(args.data_glob), key=time_from_name)
    if not case_path.exists():
        raise FileNotFoundError(case_path)
    if not data_paths:
        raise FileNotFoundError(f"No data files found: {workdir / args.data_glob}")

    times = np.asarray([time_from_name(path) for path in data_paths], dtype=float)
    case_reader = CaseFile(case_file_name=str(case_path))
    temp_fields: list[np.ndarray] = []
    liq_fields: list[np.ndarray] = []
    for path in data_paths:
        temp, liq = read_cell_fields(case_reader, DataFile, path, args.nx, args.ny, args.nz)
        temp_fields.append(temp)
        liq_fields.append(liq)

    frame_count = int(args.fps * args.duration)
    frame_times = np.linspace(0.0, args.duration, frame_count)
    temp_frame_dir = workdir / "stageA3c_dense_temperature_cloud_frames"
    melt_frame_dir = workdir / "stageA3c_dense_melt_pool_depth_frames"
    clean_frame_dir(temp_frame_dir)
    clean_frame_dir(melt_frame_dir)

    x_edges = np.linspace(0.0, args.lx_mm, args.nx + 1)
    y_edges = np.linspace(-args.ly_mm / 2.0, args.ly_mm / 2.0, args.ny + 1)
    x_centers = (np.arange(args.nx) + 0.5) * (args.lx_mm / args.nx)
    y_centers = -args.ly_mm / 2.0 + (np.arange(args.ny) + 0.5) * (args.ly_mm / args.ny)
    z_centers = -args.lz_mm + (np.arange(args.nz) + 0.5) * (args.lz_mm / args.nz)
    x_grid, z_grid = np.meshgrid(x_centers, z_centers, indexing="ij")
    path_t = np.linspace(0.0, args.duration, 2500)
    path_x = 3.0 * path_t
    path_y = 3.0 * np.sin(2.0 * np.pi * 2.0 * path_t)
    all_top = np.concatenate([field[:, :, args.nz - 1].ravel() for field in temp_fields])
    all_temp = np.concatenate([field.ravel() for field in temp_fields])
    top_vmax = float(max(2600.0, np.percentile(all_top, 99.8)))
    temp_levels = np.linspace(300.0, float(max(2600.0, np.percentile(all_temp, 99.8))), 24)
    lf_levels = np.linspace(0.0, 1.0, 11)
    depth_rows = []

    for idx, t_s in enumerate(frame_times):
        temp_xyz = interp_list(float(t_s), times, temp_fields, 300.0)
        liq_xyz = interp_list(float(t_s), times, liq_fields, 0.0)
        cx, cy = udf_center(float(t_s))

        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        mesh = ax.pcolormesh(x_edges, y_edges, temp_xyz[:, :, args.nz - 1].T, cmap="inferno", shading="flat", vmin=300.0, vmax=top_vmax)
        passed = path_t <= t_s
        ax.plot(path_x, path_y, color="#6bbcff", linewidth=1.1, alpha=0.45)
        ax.plot(path_x[passed], path_y[passed], color="#00e5ff", linewidth=3.0)
        ax.scatter([cx], [cy], c="#39ff14", s=150, edgecolors="black", linewidths=1.2, zorder=5)
        ax.set_xlim(0, args.lx_mm)
        ax.set_ylim(-args.ly_mm / 2.0, args.ly_mm / 2.0)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("X travel / mm", fontsize=18)
        ax.set_ylabel("Y weave / mm", fontsize=18)
        ax.set_title(f"Near-top temperature cloud | t = {t_s:5.2f} s", fontsize=24, pad=18)
        ax.grid(True, color="white", alpha=0.35, linewidth=0.7)
        cbar = fig.colorbar(mesh, ax=ax, fraction=0.035, pad=0.03)
        cbar.set_label("Near-top cell temperature / K", fontsize=16)
        fig.savefig(temp_frame_dir / f"frame_{idx:04d}.png")
        plt.close(fig)

        temp_mid = y_section(temp_xyz, 0.0, y_centers)
        liq_mid = y_section(liq_xyz, 0.0, y_centers)
        temp_src = y_section(temp_xyz, cy, y_centers)
        liq_src = y_section(liq_xyz, cy, y_centers)
        depth_mid = melt_depth_mm(liq_mid, z_centers)
        depth_src = melt_depth_mm(liq_src, z_centers)
        depth_rows.append({
            "time_s": float(t_s),
            "source_x_mm": cx,
            "source_y_mm": cy,
            "midplane_depth_mm_lf_ge_0p5": depth_mid,
            "source_plane_depth_mm_lf_ge_0p5": depth_src,
        })

        fig, axes = plt.subplots(1, 2, figsize=(19.2, 10.8), dpi=100, constrained_layout=True)
        last_temp = None
        last_lf = None
        panels = [
            (axes[0], temp_mid, liq_mid, "Fixed section: Y = 0 mm", depth_mid),
            (axes[1], temp_src, liq_src, f"Source-following section: Y = {cy:+.2f} mm", depth_src),
        ]
        for ax, temp_xz, liq_xz, title, depth in panels:
            last_temp = ax.contourf(x_grid, z_grid, temp_xz, levels=temp_levels, cmap="inferno", extend="max")
            last_lf = ax.contourf(x_grid, z_grid, liq_xz, levels=lf_levels, cmap="Blues", alpha=0.32, vmin=0.0, vmax=1.0)
            if float(np.nanmin(liq_xz)) <= 0.5 <= float(np.nanmax(liq_xz)):
                ax.contour(x_grid, z_grid, liq_xz, levels=[0.5], colors="#00ffff", linewidths=2.2)
            ax.axvline(cx, color="#39ff14", linewidth=2.0, linestyle="--")
            ax.set_xlim(0, args.lx_mm)
            ax.set_ylim(-args.lz_mm, 0)
            ax.set_xlabel("X travel / mm", fontsize=16)
            ax.set_ylabel("Depth Z / mm", fontsize=16)
            ax.set_title(title, fontsize=17)
            ax.grid(True, color="white", linewidth=0.7, alpha=0.35)
            ax.text(0.02, 0.04, f"Estimated melt depth (LF >= 0.5): {depth:.2f} mm", transform=ax.transAxes,
                    ha="left", va="bottom", fontsize=13,
                    bbox={"facecolor": "white", "edgecolor": "0.25", "alpha": 0.86, "boxstyle": "round,pad=0.35"})
        fig.suptitle(f"Melt-pool depth section evolution | t = {t_s:5.2f} s", fontsize=23)
        cbar_t = fig.colorbar(last_temp, ax=axes, fraction=0.025, pad=0.02)
        cbar_t.set_label("Temperature / K", fontsize=14)
        cbar_lf = fig.colorbar(last_lf, ax=axes, fraction=0.025, pad=0.08)
        cbar_lf.set_label("Liquid fraction", fontsize=14)
        fig.savefig(melt_frame_dir / f"frame_{idx:04d}.png")
        plt.close(fig)

    depth_csv = workdir / "stageA3c_dense_melt_pool_depth_sections_timeseries.csv"
    with depth_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(depth_rows[0].keys()))
        writer.writeheader()
        writer.writerows(depth_rows)

    temp_mp4 = workdir / "stageA3c_dense_realtime_temperature_cloud_top_surface.mp4"
    melt_mp4 = workdir / "stageA3c_dense_melt_pool_depth_sections.mp4"
    ffmpeg = Path(args.ffmpeg)
    temp_encode = run_ffmpeg(ffmpeg, temp_frame_dir, temp_mp4, args.fps)
    melt_encode = run_ffmpeg(ffmpeg, melt_frame_dir, melt_mp4, args.fps)
    summary = {
        "status": "ok",
        "source_snapshot_count": len(data_paths),
        "fps": args.fps,
        "duration_s": args.duration,
        "temperature_cloud_video": str(temp_mp4),
        "melt_pool_section_video": str(melt_mp4),
        "depth_csv": str(depth_csv),
        "encoding": {"temperature": temp_encode, "melt_pool": melt_encode},
    }
    (workdir / "stageA3c_dense_temperature_cloud_and_meltpool_mp4_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
