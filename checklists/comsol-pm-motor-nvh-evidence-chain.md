# COMSOL PM Motor NVH Evidence Chain

Use this checklist before claiming that a permanent-magnet motor NVH workflow completed.

## Environment and provenance

- [ ] COMSOL batch, Java compiler, Java runtime, modules, and license checkout verified by execution.
- [ ] Run directory is new or resume evidence is valid.
- [ ] Reference models were opened read-only and never saved as targets.
- [ ] Public files contain no local paths, identities, credentials, or license-server details.

## Build

- [ ] Target begins with `ModelUtil.create()`.
- [ ] Geometry topology, finalization method, identity pairs, and selections verified.
- [ ] Materials and nonlinear tables are source-backed or clearly marked assumptions.
- [ ] Magnet polarity, winding sequence, reverse-current sets, force selection, fixed boundaries, PML, EFC, and acoustic-structure boundaries verified.
- [ ] User-controlled mesh builds with no invalid elements; statistics exported.
- [ ] Built checkpoint and build log exist and agree.

## Study 1: modes

- [ ] Requested positive eigenmodes solved and exported.
- [ ] No unintended rigid-body near-zero mode.
- [ ] Mode shapes are physically interpretable.
- [ ] Modes checkpoint, log, CSV, and validation agree.

## Study 2: electromagnetics

- [ ] Complete periodic solution exists.
- [ ] Flux density and force harmonics are finite.
- [ ] Speed-reuse assumptions are explicit and valid, or electromagnetics is solved per speed.
- [ ] Electromagnetic checkpoint, log, and exports agree.

## Study 3: NVH

- [ ] Mandatory reduced SMOKE matrix passed before FULL.
- [ ] Structural displacement, acoustic pressure, PML, EFC, and far-field SPL are finite.
- [ ] Full speed and harmonic definitions match the run request.
- [ ] Campbell rows have no duplicates or NaN/Inf.
- [ ] Unsolved cells remain missing rather than `0 dB`.
- [ ] Resonance peaks are linked to traceable modal/excitation evidence.

## Final evidence

- [ ] Checkpoints are loadable.
- [ ] Geometry, mesh, modes, electromagnetic, directivity, and Campbell exports exist.
- [ ] Export validator passes.
- [ ] Evidence scan and final report completed.
- [ ] Assumptions, repair attempts, limitations, and optional reference audit are separated.
- [ ] Final status is one of `PASSED`, `PASSED_WITH_LIMITATIONS`, `FAILED`, or `BLOCKED`.
