# Fluent Sinusoidal Weld Pool Example

This example packages a public-safe, evidence-first Ansys Fluent workflow for a
sinusoidal moving heat-source weld-pool validation case.

The local validation run used:

- AISI 1045 steel plate, Stage A short-track domain: `30 mm x 20 mm x 6 mm`
- structured hex mesh: `60 x 40 x 12 = 28,800` cells
- transient thermal + Solidification/Melting model
- moving Gaussian surface heat flux UDF
- trajectory: `x = 0.003 t`, `y = 0.003 sin(2*pi*2*t)`
- dense output: `0.10 s` data interval, `0-10 s`

The goal is not to publish a calibrated welding benchmark. The goal is to show
how an AI agent should build a real Fluent evidence chain: environment checks,
mesh and axis audit, UDF compilation, controlled transient solve, solver logs,
postprocessing images/videos, CSV/JSON summaries, and a credibility statement.

## Directory Layout

```text
inputs/
  stageA_plate_ansys.msh
  stageA_mesh_meta.json
scripts/
  generate_stageA_mesh.py
  moving_heat_source_sinusoidal.c
  run_stageA_dense_pyfluent.py
  create_temperature_cloud_and_meltpool_mp4.py
  plot_meltpool_parameter_curves.py
sample-outputs/
  stageA3c_dense_meltpool_parameter_curves.png
  stageA3c_dense_melt_pool_depth_sections_timeseries.csv
  *.json / *.csv summaries
```

## How to Run Locally

1. Install or activate an Ansys Fluent 2025 R2 / PyFluent-capable environment.

2. Set local paths. Replace these with your installation:

```powershell
$env:FLUENT_EXE = "<path-to-fluent.exe>"
$env:PYFLUENT_CORE = "<path-to-PyFluentCore>"
$env:FFMPEG_EXE = "<path-to-ffmpeg.exe>"
```

3. Create a working copy so generated `.dat.h5`, UDF DLLs, frames, and logs do
   not pollute the repository:

```powershell
cd examples\fluent-sinusoidal-weld-pool
New-Item -ItemType Directory -Force runs\stageA3c
# Put your local .cas.h5 seed case in runs\stageA3c\ if you have one.
Copy-Item scripts\moving_heat_source_sinusoidal.c runs\stageA3c\
```

4. Run the dense Stage A validation:

```powershell
python scripts\run_stageA_dense_pyfluent.py `
  --workdir runs\stageA3c `
  --base-case <your-local-seed-case.cas.h5> `
  --udf-source moving_heat_source_sinusoidal.c `
  --compile-udf `
  --total-time 10 `
  --time-step 0.05 `
  --save-interval 0.10
```

5. Generate videos and curves:

```powershell
python scripts\create_temperature_cloud_and_meltpool_mp4.py --workdir runs\stageA3c
python scripts\plot_meltpool_parameter_curves.py --csv runs\stageA3c\stageA3c_dense_melt_pool_depth_sections_timeseries.csv
```

## What the Sample Outputs Show

- `stageA3c_dense_realtime_temperature_cloud_top_surface.mp4`: near-top
  temperature field over time with the moving sinusoidal heat-source trajectory.
- `stageA3c_dense_melt_pool_depth_sections.mp4`: two longitudinal X-Z sections:
  fixed `Y=0` and source-following `Y=y_source(t)`, with temperature,
  liquid-fraction overlay, `LF=0.5` contour, and estimated melt depth.
- `stageA3c_dense_meltpool_parameter_curves.png`: melt depth, heat-source
  position, and depth along travel direction.

## Credibility

Current public evidence grade: `visual validation / functional validation`.

Important limitations:

- The Stage A model is thermal + Solidification/Melting only.
- VOF/free-surface deformation is intentionally not enabled.
- Melt depth is estimated from `liquid_fraction >= 0.5`.
- The through-thickness cell size is about `0.5 mm`, so melt depth is a
  diagnostic curve, not a report-grade dimension.
- Material properties are engineering estimates unless replaced with a
  traceable temperature-dependent material dataset.

## Next Upgrade

1. Refine the melt-pool region to `0.05-0.1 mm`.
2. Reduce time step and perform a time-step sensitivity check.
3. Add temperature-dependent AISI 1045 properties.
4. Stage B: enable buoyancy and melt-pool flow.
5. Stage C: only after A/B are stable, add gas region, VOF, surface tension, and
   Marangoni physics.
