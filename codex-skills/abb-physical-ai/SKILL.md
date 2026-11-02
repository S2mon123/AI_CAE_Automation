---
name: abb-physical-ai
description: Develop and commission the ABB IRC5/IRB6700, TwinCAT 2 PLC and RobotStudio 2025 Physical AI cube workflow. Use for signed Win7 read-only bridge setup, PLC/ABB state inspection, frozen-context RAPID drafts, TSM link proposals and evidence-gated task preparation. Distinguish offline development from physical execution.
---

# ABB Physical AI

Use `abb-physical-ai` MCP for PLC/ABB read-only commissioning and local task artifacts.
Use `robotstudio` MCP for Station/Virtual Controller inspection. These are separate
servers: the new Win7 RPC is `physical-ai/4.0`, not the RobotStudio Add-In protocol
and not the retired v0.2 bridge. Check installed tools before assuming availability.

## Start with the actual task

For development, work in the user's repository; preserve existing uncommitted work
and take a scoped backup before replacing files. Do not translate a request to
develop control software into permission to move the robot or change PLC runtime.
Read [references/site-and-signals.md](references/site-and-signals.md) for the reported
baseline and distinctions between Start, Done, Stop and task entry selection.

1. Read `system_get_capabilities` and `system_discover`. Treat implementation,
   local Windows tests, VC observations and field commissioning as different states.
2. Use existing local environment probes and explicit project roots to find SDK,
   RDP/VM clues and `.tsm` candidates. Do not guess AMS, choose the newest project,
   scan unknown networks or reconfigure working PLC network adapters.
3. If Win7 has no authorized execution channel, give the operator the one local
   discovery command in the project's deployment guide. Report it as not run.
4. With confirmed target configuration, read `system_get_status`, `plc_read_alias`
   and `abb_read`. Reading start/done must not toggle, clear, force or write them.
5. In RobotStudio, inspect Station/VC capabilities and use
   `inspect_cube_task_context` with the actual expected module and routine.
   Entry mismatch, a J6 program, missing source or stale evidence remains a blocker.

## Offline task development

Read [references/tasks-and-evidence.md](references/tasks-and-evidence.md) before
creating or validating a task. Use `task_create` with full frozen context. Unknown
Tool/Load/WObj, source or installation geometry must remain unknown; never invent
hashes for a real task. Synthetic examples belong in explicitly marked demo runs.

`task_render` writes additive local drafts for B/C; A registers existing code and
must not render a replacement. `task_validate` checks geometry and supplied
evidence structure. It does not compile RAPID or execute a simulation. Every
validation binding and expiry must still match when read back. A structural PASS
does not authenticate the report author or authorize deployment/motion.

`tc2_inspect` reads disk XML. `tc2_stage_link_proposal` saves a source snapshot and
an **unapplied** proposal, not a COM-edited `.tsm`. Never claim a bit is free without
PLC byte/array overlap and ABB DI/DO/GI/GO range evidence.

## Execution boundary of this release

The current implementation intentionally exposes no PLC write, activation, RAPID
deployment, PP movement, Motor On, Start, Resume or approval-creation tool.
`task_prepare_execute` explains blockers. `task_simulate` reports unavailable
automation. `robot_request_process_stop` returns `STOP_UNAVAILABLE` and sends no
request. Do not advertise these as implemented physical actions.

If the user asks for physical execution, explain the actual missing capabilities
and commissioning evidence. Do not substitute shell/UI writes or generate a fake
approval. Future execution work must implement the separate authorization,
persistent supervision and verified Stop architecture described in
[references/stop-and-release.md](references/stop-and-release.md).

## Report precisely

Report what was read, generated, compiled, loaded, triggered and observed separately.
Use `DOCUMENT_REPORTED`, `IMPLEMENTED`, `OFFLINE_TESTED`, `WINDOWS_TESTED`,
`FIELD_VERIFIED`, `UNKNOWN` and `BLOCKED` with a source and timestamp where applicable.
Never promote mocks, generated files or host compilation to `FIELD_VERIFIED`.
Include exact changed files, test results, rollback location and remaining physical
facts that could not be obtained automatically. Keep vendor DLLs, credentials,
production projects and controller backups out of public source.
