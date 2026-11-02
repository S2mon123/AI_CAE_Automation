# Changelog

## Unreleased - 2026-09-27

- Added `inspect_cube_task_context` for the Physical AI 200 mm cube application:
  expected VC entry, identity-consistent I/O snapshots, explicit missing evidence.
- Preserved virtual-only controller guards and the existing Add-In protocol.
- Added four scenario regression tests and routed PLC/real-ABB read-only work to
  the separate v4 `abb-physical-ai` component and Skill.
- This Python-only update does not add automatic simulation or physical execution.

## 0.1.0 - 2026-08-02

- Implemented design Phase 0 and Phase 1.
- Added Python FastMCP stdio server, resources, prompts, structured errors, audit records, and isolated projects.
- Added authenticated loopback C# Add-In bridge compiled against RobotStudio 2025.3 SDK.
- Added read-only Station and Virtual Controller/RAPID/Event Log/I/O adapters.
- Added install, build, register, verify, smoke, and uninstall workflows.
- Explicitly deferred all RobotStudio/controller write and execution capabilities.
