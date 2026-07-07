# Local MCP Source Audit

This note records how local Abaqus, Ansys, and COMSOL MCP material was handled
before public release.

## Local Sources Found

- Local prompt notes for Abaqus 2026 drilling and modal workflows.
- Local prompt notes for Ansys Fluent external-flow and welding workflows.
- Local prompt notes for COMSOL Java API and batch-driven multiphysics tasks.
- Third-party CAE MCP folders under local Codex/Obsidian paths.

## Public Handling Decision

The public repository does not copy third-party MCP server source code or local
private prompt notes verbatim. Instead it provides:

- project-owned minimal MCP tools in `src/ai_cae_lab/adapters/`
- installable Codex skills in `codex-skills/`
- public-safe MCP documentation in `mcp/abaqus`, `mcp/ansys`, and `mcp/comsol`
- environment-variable based configuration examples

## Why

This avoids:

- publishing private machine paths,
- publishing paid or local-only material,
- copying third-party project structure too closely,
- committing solver outputs, vendor documentation, or proprietary model data.

The resulting public surface is intentionally evidence-first: every solver call
must write logs, scan artifacts, and produce a credibility-graded report.
