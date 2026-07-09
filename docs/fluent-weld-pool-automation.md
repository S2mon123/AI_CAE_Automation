# Fluent Weld-Pool Automation Notes

This note captures the workflow behind the sinusoidal moving heat-source
welding example in `examples/fluent-sinusoidal-weld-pool`.

## Recommended Evidence Loop

1. **Environment check**
   - Fluent executable path.
   - PyFluent import path or Ansys Python path.
   - UDF compiler availability.
   - FFmpeg availability for MP4 export.

2. **Geometry and axis audit**
   - X is welding travel.
   - Y is sinusoidal weave.
   - Z is thickness.
   - Top surface receives heat flux.
   - Gravity is not enabled until the coordinate system is confirmed.

3. **Stage A first**
   - Thermal + Solidification/Melting.
   - No VOF.
   - No free-surface deformation.
   - Use liquid fraction as a diagnostic melt-pool indicator.

4. **UDF verification**
   - Confirm `x_center(t)=v*t`.
   - Confirm `y_center(t)=A*sin(2*pi*freq*t)`.
   - Export a trajectory plot before interpreting weld-pool results.

5. **Dense output for animation**
   - Save transient data at a fixed interval, for example `0.10 s`.
   - Build videos from actual cell-field data, not from manually drawn frames.

6. **Postprocess**
   - Temperature cloud MP4.
   - Melt-depth section MP4.
   - Melt-depth time-series CSV.
   - Melt-pool parameter curve PNG/SVG.
   - JSON run summary with solver settings and warnings.

## Credibility Boundaries

Stage A is a functional and visual validation workflow. It should not be sold as
a calibrated weld-pool prediction. Report-grade welding CFD needs at least:

- traceable temperature-dependent material properties,
- mesh and time-step sensitivity,
- heat-source calibration against experiment,
- Stage B flow modeling,
- Stage C free-surface modeling only after A/B are stable.

## Public Repository Policy

Keep reusable scripts, prompts, UDF source, small seed inputs, and representative
sample outputs. Do not commit large time-series `.dat.h5` bundles, commercial
project files from private jobs, license files, or vendor documentation.
