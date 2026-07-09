from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def read_rows(path: Path) -> dict[str, np.ndarray]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError(f"No data rows in {path}")
    data: dict[str, list[float]] = {col: [] for col in rows[0].keys()}
    for row in rows:
        for col in data:
            data[col].append(float(row[col]))
    return {col: np.asarray(values, dtype=float) for col, values in data.items()}


def max_with_time(values: np.ndarray, times: np.ndarray) -> dict[str, float]:
    idx = int(np.nanargmax(values))
    return {"value_mm": float(values[idx]), "time_s": float(times[idx])}


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot melt-pool parameters from exported depth CSV.")
    parser.add_argument("--csv", default="sample-outputs/stageA3c_dense_melt_pool_depth_sections_timeseries.csv")
    parser.add_argument("--out", default=None, help="Output PNG path.")
    parser.add_argument("--svg", default=None, help="Output SVG path.")
    args = parser.parse_args()

    input_csv = Path(args.csv)
    out_png = Path(args.out) if args.out else input_csv.with_name("stageA3c_dense_meltpool_parameter_curves.png")
    out_svg = Path(args.svg) if args.svg else input_csv.with_name("stageA3c_dense_meltpool_parameter_curves.svg")
    data = read_rows(input_csv)
    t = data["time_s"]
    x = data["source_x_mm"]
    y = data["source_y_mm"]
    mid_depth = data["midplane_depth_mm_lf_ge_0p5"]
    source_depth = data["source_plane_depth_mm_lf_ge_0p5"]

    fig, axes = plt.subplots(3, 1, figsize=(14.5, 12.0), dpi=180, constrained_layout=True)
    ax = axes[0]
    ax.plot(t, source_depth, color="#d62728", linewidth=2.5, label="source-following section depth, LF>=0.5")
    ax.plot(t, mid_depth, color="#1f77b4", linewidth=2.0, linestyle="--", label="fixed centerline depth Y=0, LF>=0.5")
    ax.fill_between(t, 0.0, source_depth, color="#d62728", alpha=0.14)
    ax.set_title("Melt-pool depth versus time", fontsize=18, pad=12)
    ax.set_xlabel("Time / s")
    ax.set_ylabel("Depth / mm")
    ax.grid(True, alpha=0.32)
    ax.legend(loc="upper left")

    src_max = max_with_time(source_depth, t)
    ax.scatter([src_max["time_s"]], [src_max["value_mm"]], color="#d62728", s=45, zorder=5)
    ax.annotate(
        f"max source-section depth {src_max['value_mm']:.2f} mm @ {src_max['time_s']:.2f} s",
        xy=(src_max["time_s"], src_max["value_mm"]),
        xytext=(src_max["time_s"] + 0.25, src_max["value_mm"] + 0.08),
        arrowprops={"arrowstyle": "->", "color": "#333333", "lw": 1.0},
        fontsize=10,
        bbox={"facecolor": "white", "edgecolor": "#999999", "alpha": 0.88},
    )

    ax = axes[1]
    ax.plot(t, x, color="#2ca02c", linewidth=2.2, label="heat-source X")
    ax.set_title("Heat-source position versus time", fontsize=18, pad=12)
    ax.set_xlabel("Time / s")
    ax.set_ylabel("X / mm", color="#2ca02c")
    ax.tick_params(axis="y", labelcolor="#2ca02c")
    ax.grid(True, alpha=0.32)
    ax2 = ax.twinx()
    ax2.plot(t, y, color="#9467bd", linewidth=2.0, label="heat-source Y")
    ax2.set_ylabel("Y / mm", color="#9467bd")
    ax2.tick_params(axis="y", labelcolor="#9467bd")
    lines = ax.get_lines() + ax2.get_lines()
    ax.legend(lines, [line.get_label() for line in lines], loc="upper left")

    ax = axes[2]
    sc = ax.scatter(x, source_depth, c=t, cmap="viridis", s=24, edgecolors="none")
    ax.plot(x, source_depth, color="#444444", linewidth=1.0, alpha=0.55)
    ax.set_title("Melt depth along welding travel", fontsize=18, pad=12)
    ax.set_xlabel("Heat-source X / mm")
    ax.set_ylabel("Source-section depth / mm")
    ax.grid(True, alpha=0.32)
    cbar = fig.colorbar(sc, ax=ax, fraction=0.025, pad=0.015)
    cbar.set_label("Time / s")

    fig.suptitle("Stage A3c sinusoidal moving heat source: melt-pool parameter curves", fontsize=20)
    fig.savefig(out_png)
    fig.savefig(out_svg)
    plt.close(fig)

    summary = {
        "status": "ok",
        "input_csv": str(input_csv),
        "output_png": str(out_png),
        "output_svg": str(out_svg),
        "sample_count": int(len(t)),
        "time_range_s": [float(t.min()), float(t.max())],
        "max_source_plane_depth": src_max,
        "max_midplane_depth": max_with_time(mid_depth, t),
        "notes": [
            "Depth is estimated from liquid_fraction >= 0.5.",
            "Depth precision is limited by through-thickness mesh spacing.",
        ],
    }
    summary_path = out_png.with_name(out_png.stem + "_summary.json")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
