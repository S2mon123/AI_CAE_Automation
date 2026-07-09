# Fluent Weld-Pool Evidence Checklist

## Environment

- [ ] Fluent executable path recorded.
- [ ] Ansys version recorded.
- [ ] PyFluent import path or Ansys Python path recorded.
- [ ] UDF compiler route checked.
- [ ] FFmpeg route checked when exporting MP4.
- [ ] Working directory recorded.

## Geometry and Mesh

- [ ] Plate dimensions recorded.
- [ ] X/Y/Z coordinate definition recorded.
- [ ] Top heat-flux boundary identified.
- [ ] No unjustified symmetry boundary used.
- [ ] Cell count recorded.
- [ ] Minimum size recorded.
- [ ] Maximum skewness recorded.
- [ ] Maximum aspect ratio recorded.

## Physics

- [ ] Energy model enabled.
- [ ] Solidification/Melting enabled for Stage A.
- [ ] Mushy-zone parameter recorded.
- [ ] Material properties listed with source or marked as estimates.
- [ ] VOF disabled for Stage A unless explicitly upgraded.
- [ ] Gravity direction audited before Stage B.

## UDF

- [ ] UDF source committed or archived.
- [ ] UDF compile/load log saved.
- [ ] Heat-source power, efficiency, speed, amplitude, frequency, and radius recorded.
- [ ] Trajectory evidence exported.

## Solve

- [ ] Time step recorded.
- [ ] Total simulated time recorded.
- [ ] Save interval recorded.
- [ ] Fluent transcript/log saved.
- [ ] Warnings/errors searched for divergence, floating point, temperature limiting, and failed status.

## Outputs

- [ ] Case/data or input seed files saved locally.
- [ ] Temperature image exported.
- [ ] Liquid-fraction image exported.
- [ ] Temperature-cloud MP4 exported.
- [ ] Melt-pool section MP4 exported.
- [ ] Melt-depth CSV exported.
- [ ] Melt-pool parameter curve exported.
- [ ] Summary JSON exported.
- [ ] Final report written.

## Credibility

- [ ] Current grade stated: dry-run, functional validation, visual validation, engineering draft, or report-grade.
- [ ] Mesh/time-step limitations stated.
- [ ] Material-property limitations stated.
- [ ] Next minimal improvement stated.
