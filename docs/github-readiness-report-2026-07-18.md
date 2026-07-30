# GitHub Readiness Report - 2026-07-18

## Scope

This review covers the public-source organization for:

- Ansys Electronics Desktop (AEDT/PyAEDT)
- Ansys Fluent
- Ansys Mechanical and Workbench
- Altair HyperMesh
- LAMMPS
- OVITO

The repository was not committed or pushed during this pass.

## Public Architecture

Each new software direction now follows the repository contract:

```text
adapter -> solver-scoped MCP profile -> Codex skill -> prompt -> checklist -> example -> tests
```

The shared toolbox also provides discovery, private path configuration, run
records, smoke templates, evidence scans, credibility grades, and reports.

## Completed Modules

### AEDT

- Added AEDT/PyAEDT discovery and import probes.
- Added a solver-scoped MCP package and Skill.
- Added design/solution-type, Maxwell reciprocity, and HFSS acceptance gates.
- Added a public wireless-power example skeleton.

### Ansys Mechanical

- Added independent RunWB2/ExtAPI and PyMechanical routes.
- Added a machine-readable result-summary validator.
- Requires Solved state, MAPDL normal termination, reaction balance, accepted
  mesh evidence, `.rst`, numeric export, image export, and solve log.

### HyperMesh

- Added `hmbatch -tcl` discovery and execution.
- Added blocking gates for CAD import, zero entities/elements, severe quality
  failures, and empty solver-deck export.

### LAMMPS And OVITO

- Added LAMMPS executable/input execution and MD log signals.
- Added a potential-free parser smoke; no interatomic potential is bundled.
- Added OVITO GUI-versus-batch-Python capability reporting.
- Kept upstream LAMMPS solve evidence separate from OVITO render evidence.

### Fluent

- Extended the Skill with external-flow and weld-pool claim gates.
- Distinguishes thermal, liquid fraction, melt flow, VOF free surface, spatter,
  and structural-coupling claims.

## Validation Results

- Python compile check: passed.
- Pytest: 24 tests passed.
- Unittest: 24 tests passed.
- Codex Skill validation: 11 of 11 passed.
- JSON parse check: 36 files passed.
- TOML parse check: 29 files passed.
- Solver context scopes: 13 checked, no missing referenced paths.
- Public repository audit: 0 errors.
- Markdown local-link audit: passed.
- Secret/private-key pattern audit: passed.
- Absolute Windows path audit: passed.
- Blocked solver-result extension audit: passed.
- `git diff --check`: passed.

## Remaining Warning

One existing public Fluent seed mesh is approximately 1.73 MB:

`examples/fluent-sinusoidal-weld-pool/inputs/stageA_plate_ansys.msh`

It is below the 10 MB blocking threshold and is intentionally included as a
public example input. If repository size becomes a priority, move it to a
release asset or regenerate it from the included mesh script.

## Credibility Boundary

This pass validates repository code, schemas, Skills, documentation, and public
safety. It does not claim that every commercial solver was launched and solved
again during this repository-organization pass.

Real solver claims still require the user's own installation, API packages,
license checkout, model inputs, native logs, and solver-specific evidence gates.

## Release Decision

The repository is ready for a review commit as a `0.3.0` bridge-preview release.
Before publishing:

1. Review `git diff` for editorial preference.
2. Decide whether to retain the 1.73 MB Fluent mesh in Git.
3. Create a commit only after that review.
4. Push or tag only when explicitly approved.
