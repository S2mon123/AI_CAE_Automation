# Local MCP Source Audit

This note records how local Abaqus, Ansys, COMSOL, open-toolchain, and
electrical CAD automation material was handled before public release.

## Local Sources Found

- Local prompt notes for Abaqus 2026 drilling and modal workflows.
- Local prompt notes for Ansys Fluent external-flow and welding workflows.
- Local prompt notes for COMSOL Java API and batch-driven multiphysics tasks.
- A local COMSOL EHD ion-wind soybean drying run folder with Java files, logs,
  reports, and solver artifacts.
- Local notes for MATLAB/Simulink, OpenFOAM, and ParaView MCP-style workflows.
- Third-party CAE MCP folders under local Codex/Obsidian paths.

## Public Handling Decision

The public repository does not copy third-party MCP server source code or local
private prompt notes verbatim. Instead it provides:

- project-owned minimal MCP tools in `src/ai_cae_lab/adapters/`
- installable Codex skills in `codex-skills/`
- public-safe MCP documentation in `mcp/abaqus`, `mcp/ansys`, and `mcp/comsol`
- public-safe MCP documentation for MATLAB, OpenFOAM, and ParaView
- rewritten public prompts and checklists, including the COMSOL EHD soybean
  drying prompt
- environment-variable based configuration examples

## Why

This avoids:

- publishing private machine paths,
- publishing paid or local-only material,
- copying third-party project structure too closely,
- committing solver outputs, vendor documentation, or proprietary model data.

The resulting public surface is intentionally evidence-first: every solver call
must write logs, scan artifacts, and produce a credibility-graded report.
