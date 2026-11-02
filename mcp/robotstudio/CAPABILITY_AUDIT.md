# Capability Audit

## Audited target

- RobotStudio: 2025.3, file/API build `25.3.11371.0`
- Add-In runtime: .NET Framework 4.8, x64
- SDK assemblies: RobotStudio core, Stations, Controllers integration, PC SDK, and ABB Math from the same RobotStudio installation
- MCP: FastMCP 2.x over stdio

Exact APIs were checked against installed 2025.3 assembly metadata. Public documentation links and the audited signatures are recorded in `docs/API_AUDIT_2025.3.md`.

## Local verification record (2026-08-03)

- Environment probe: compatible; RobotStudio executable and all five required SDK assemblies report `25.3.11371.0`.
- Python: Ruff clean; Pytest `11 passed`; a real stdio subprocess handshake exposed `32 tools`, and `get_bridge_status` returned a structured `RS_BRIDGE_OFFLINE` result with request ID `7cb9c4606cbf43d18b65dddc947e4e39`.
- C#: Release/x64 build against the installed SDK completed with `0 warnings` and `0 errors`; bridge contract tests `4 passed`.
- Deployment: RobotStudio accepted the correctly rooted `.rspak`, installed it as `AICAEAutomationLab.RobotStudioMcpBridge-0.1.0`, and its own extension scanner reports compatible, no errors, Add-In component present. The installed `.rsaddin` passed the RobotStudio 2025.3 XSD and the deployed assembly reports `0.1.0.0`.
- Codex: the `robotstudio` stdio server and the `robotstudio-core` skill were installed and their configured targets were resolved.
- UI acceptance: RobotStudio `25.3.11371.0` was started successfully after restoring the standard Windows process environment inherited by the Codex launcher. Keyboard navigation, Add-Ins, package installation, Options, and creation of a blank Station all remained responsive.
- Live bridge acceptance: blocked by the installed RobotStudio `Free` runtime license. RobotStudio does not load this third-party Add-In because it references `ABB.Robotics.RobotStudio.dll`; the DLL is absent from the process, port `127.0.0.1:47625` is closed, and Station calls correctly return `RS_BRIDGE_OFFLINE`. ABB documents RobotStudio Premium as the runtime requirement for this Add-In class. No license check was bypassed.

## Phase 0/1 status

| Capability | Implementation | Static/contract verification | Live verification requirement |
|---|---|---|---|
| Installation and SDK discovery | Implemented | Python tests + local probe | None |
| Add-In load manifest | Implemented | 2025.3 XSD validation + RobotStudio package scan | Premium license, then restart and confirm load |
| Authenticated bridge ping | Implemented | Python framing/auth tests + C# contract tests | Premium-licensed RobotStudio must load the Add-In |
| Station summary/components | Implemented | Compiles against 25.3 SDK | Active Station comparison with UI |
| Robots/tools/workobjects/targets/paths | Implemented | Compiles against 25.3 SDK | Active Station comparison with UI |
| Controller scan/classification | Implemented | Compiles against 25.3 PC SDK | PC SDK scan |
| Virtual Controller status/pointers | Implemented | Compiles against 25.3 PC SDK | Active VC comparison with UI |
| RAPID tasks/modules metadata | Implemented | Compiles against 25.3 PC SDK | Active VC comparison with RAPID view |
| Event Log | Implemented | Compiles against 25.3 PC SDK | Active VC comparison with Event Log |
| I/O reads | Implemented | Compiles against 25.3 PC SDK | Active VC comparison with I/O view |
| RAPID module text export | Capability-gated | Not exposed | Phase 3 file-transfer design |
| Station/controller writes | Not exposed | Absence tests | Later phases only |
| Real-controller connection | Not exposed | Guarded by both Station and PC SDK virtual checks | Separate future review |

The project must not be called fully complete until the live rows have been exercised against an actual Station and Virtual Controller and later write phases are separately implemented and accepted.
