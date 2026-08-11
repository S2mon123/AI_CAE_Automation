# Security

## Enforced boundary

- Release level: `LEVEL_0_READ_ONLY` for RobotStudio and controllers.
- Controller scope: `virtual_only`.
- Real controllers: discovery classification only; no connection, reads, or writes.
- Network: IPv4 loopback only, never `0.0.0.0`.
- Authentication: 256-bit random token in a user-private file.
- Dispatch: fixed read-only registry; no reflection dispatch.
- Execution: no shell, PowerShell, Python, C#, DLL loading, macro, or `eval` tool.
- Logs: request metadata and error codes only; token/password/secret fields are redacted.

`controller.scan` may reveal real controllers visible to ABB PC SDK, but never connects to them. All other controller tools resolve the controller attached to the active Station and reject it unless `ControllerInfo.IsVirtual` and `Controller.IsVirtual` are both true.

## Files

Project paths are resolved and checked against the configured workspace. Imports require an explicit source file and a fixed input category. Existing destinations are not overwritten unless `overwrite=true` was explicitly supplied. Public source files contain no vendor DLLs, RobotWare, licenses, commercial manuals, private Stations, or machine-specific configuration.

## Deferred high-risk operations

Station mutation, RAPID upload/load/write, Mastership, Reset PP, Start/Stop, I/O writes, controller restart, and real-controller access require later design phases and are not registered. Their absence from `tools/list` and the Add-In method registry is the enforcement mechanism—not a prompt-only convention.

Report vulnerabilities without attaching proprietary Stations, controller backups, credentials, or licenses.
