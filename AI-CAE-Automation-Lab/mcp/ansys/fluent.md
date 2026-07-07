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
