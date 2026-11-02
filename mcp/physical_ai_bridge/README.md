# ABB Physical AI MCP — v4 development release (software 0.4.0)

This implements the read-only and offline-development portion of the v4 design
for TwinCAT 2 / VMware Win7 / CX9020 / EL6631 / ABB IRC5 / RobotStudio 2025.3.
The first application is a frozen-context 200 mm cube path. It is **not a completed
physical-motion controller**. No device write, Start, deployment, activation or
working Process Stop is provided in this release.

The user selected v4 as the implementation baseline and retired the v0.2 package.
The new `physical-ai/4.0` signed RPC is therefore explicitly **not v0.2 compatible**.
Keep the existing RobotStudio Add-In protocol and `virtual_only` checks unchanged.

## What works in source

| Component | Implemented behavior | Verification boundary |
|---|---|---|
| MCP host | 15 tools, official MCP SDK 1.29.0, stdio | Real subprocess handshake and calls tested |
| Task core | A registration; B/C additive RAPID drafts; frozen context and manifests | Geometry/file/evidence tests, not RAPID compiler validation |
| Evidence evaluator | Exact binding, expiry and every required PASS | Structural assessment; never issues deployment/motion approval |
| Win7 bridge | Signed read-only RPC, client allowlist, nonce window, exact BOOL symbol metadata | x86 build and cross-language tests on Windows host; Win7/ADS unverified |
| ABB proxy | Explicit controller GUID/IP/type, credentials, status, pointers/module metadata, named I/O | x64 build against installed 25.3 SDK; controller connection unverified |
| TC2 drafts | TSM XML inspection, byte-exact snapshot and unapplied link proposal | No COM edit, occupancy proof or activation |
| RobotStudio extension | Existing VC reads plus `inspect_cube_task_context` in sibling MCP | Python tests; live Add-In currently unavailable in this run |

The ABB proxy is separate from RobotStudio's GUI/Add-In and references PC SDK only.
It does not request Mastership. Source-text export and controller option inspection
remain unavailable; module metadata does not prove a loaded cube program.

## Run locally

Use a dedicated Python 3.11+ environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
$env:PHYSICAL_AI_WORKSPACE = '<private-workspace>'
.\.venv\Scripts\python.exe -m physical_ai.server
```

Without `PHYSICAL_AI_CONFIG`, all physical adapters stay unconfigured. Use
[examples/codex-config.example.toml](examples/codex-config.example.toml) to register
the separate `abb-physical-ai` server. The old `robotstudio` server remains available.
Installing source in a repository does not automatically update the running Codex
MCP process or its installed Skill copy.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/offline_demo.py --workspace '<private-demo-workspace>'
```

The demo labels all context as synthetic, generates RAPID and a manifest, reports
missing simulation evidence, and leaves execution BLOCKED. Never use its hashes,
tool, pose or controller ID as site facts.

Read [deployment](docs/DEPLOYMENT.md), [protocol](docs/PROTOCOL.md),
[development summary and remaining work](docs/DEVELOPMENT_REPORT.zh-CN.md), and
[rollback](docs/ROLLBACK.md). The companion Skill is
[abb-physical-ai](../../codex-skills/abb-physical-ai/SKILL.md).

## Key physical distinctions

Start FALSE is not Stop. Done is read-only. One Start bit cannot choose a new RAPID
module. A matching PP does not prove a waiting handshake. File generation is not
RAPID compilation; checking endpoints is not checking every MoveL segment.
At 200 mm, 16 segments and v50/30%, nominal time is 213.33 seconds before fine-point
stops; the example 600-second completion timeout is not a stopping requirement.

`task_prepare_execute` only returns blockers. `task_simulate` explicitly returns
`SIMULATION_AUTOMATION_NOT_IMPLEMENTED`. `robot_request_process_stop` returns
`STOP_UNAVAILABLE`, with no request delivered and no standstill observed.
Future execution requires an authenticated operator approval mechanism, commissioned
independent Stop, persistent Supervisor/command ledger, verified current entry/pose,
and deployment/readback transactions. Skill text and MCP annotations enforce none
of these by themselves; this release enforces its boundary by having no writer.
