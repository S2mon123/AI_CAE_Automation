# Fluent MCP Notes

The current public adapter exposes `fluent_run_journal_file`, a conservative
batch journal runner. It is intended for repeatable smoke tests and evidence
collection before richer live PyFluent session management is added.

The adapter expects:

- a run folder created by `create_run_record`
- a journal under `runs/<run>/scripts/`
- `FLUENT_EXE` or `FLUENT_ROOT` configured locally

The journal should write case/data outputs, residual exports, force reports, and
visual evidence into the run folder.

<!-- AI-CAE:weld-pool:START -->
## Welding and Melt-Pool Runs

For transient welding tasks, keep the public adapter conservative:

- create a run folder first,
- place UDF source and Fluent journals/PyFluent scripts under `scripts/`,
- write all dense `.dat.h5` outputs under the run folder,
- export lightweight summaries, images, videos, and CSV evidence,
- do not claim calibrated weld-pool dimensions from coarse Stage A runs.

The example `examples/fluent-sinusoidal-weld-pool` shows a Stage A
thermal/Solidification-Melting workflow with a sinusoidal moving heat-source UDF.
<!-- AI-CAE:weld-pool:END -->
