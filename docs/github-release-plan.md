# GitHub Release Plan

## Phase 1: Clean Public Skeleton

- README in English and Chinese.
- Architecture, workflow, and software matrix.
- Prompt templates for Abaqus, Fluent, and COMSOL.
- Smoke-test and evidence-chain checklists.
- Environment checker script.

## Phase 2: Verified Local Examples

- Add one tiny public example per solver.
- Each example must include inputs, script, logs, and expected outputs.
- Keep large solver artifacts out of Git. Use releases or external storage only when licensing permits.

## Phase 3: MCP Tooling

- Add minimal MCP server templates.
- Add client configuration examples.
- Add smoke tests for tool listing and no-op commands.

## Phase 4: Documentation Site

- Convert docs into a GitHub Pages site.
- Add diagrams, task cards, and reproducibility guides.

## Publishing Checklist

- No private source names.
- No credentials.
- No paid material copied verbatim.
- No proprietary geometry.
- No solver license files.
- No false claims of verified results.
