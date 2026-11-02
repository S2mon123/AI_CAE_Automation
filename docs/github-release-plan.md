# GitHub Release Plan

## Phase 1: Clean Public Skeleton

- README in English and Chinese.
- Architecture, workflow, and software matrix.
- Prompt templates for AEDT, Abaqus, Fluent, Mechanical, HyperMesh, LAMMPS,
  OVITO, and COMSOL.
- Smoke-test and evidence-chain checklists.
- Environment checker script.

## Phase 2: Verified Local Examples

- Add one tiny public example per solver.
- Each example must include inputs, script, logs, and expected outputs.
- Keep large solver artifacts out of Git. Use releases or external storage only when licensing permits.

## Phase 3: MCP Tooling

- Maintain solver-scoped MCP packages and client configuration examples.
- Test aliases, tool isolation, smoke templates, failure signals, and evidence gates.
- Keep commercial executables, licenses, private projects, and large outputs external.

## Phase 4: Documentation Site

- Convert docs into a GitHub Pages site.
- Add diagrams, task cards, and reproducibility guides.

## Publishing Checklist

- No private source names.
- No credentials.
- No paid material copied verbatim.
- No proprietary geometry.
- No solver license files.
- No unreviewed interatomic potentials.
- No unredacted absolute local paths in public source.
- No large trajectory, video, project, or result database files.
- No false claims of verified results.

## Current Release Gate

- Code/unit tests and Skill validation must pass in CI.
- JSON/TOML examples must parse.
- Markdown links and referenced repository paths must resolve.
- `git diff --check`, secret/path scan, and large-file scan must pass.
- Real commercial-solver smoke status must be reported separately from code readiness.
