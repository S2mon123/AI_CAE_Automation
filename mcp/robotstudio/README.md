# RobotStudio MCP Server

Local MCP integration for ABB RobotStudio 2025.3. It combines a Python FastMCP stdio server with an authenticated C# Add-In running inside RobotStudio.

Runtime prerequisite: ABB requires a RobotStudio Premium license to run an Add-In that references `ABB.Robotics.RobotStudio.dll`. The MCP stdio server can still start under the Free license, but its live bridge and Station tools will correctly report `RS_BRIDGE_OFFLINE` until RobotStudio is licensed and the Add-In is loaded.

This `0.1.0` release intentionally implements only design phases 0 and 1:

- local RobotStudio/SDK discovery and strict 25.3 version audit;
- an isolated project workspace with hashed imports and evidence checkpoints;
- live Add-In ping and fixed capability discovery;
- read-only Station, robots, ToolData, WorkObject, targets, and paths;
- read-only Virtual Controller status, program pointers, RAPID task/module metadata, Event Log, and I/O;
- MCP tools, resources, prompts, structured errors, and audit logs.

It does not expose Station writes, RAPID file transfer/load/write, I/O writes, program execution, program-pointer reset, arbitrary code, or real-controller connections.

## Architecture

```text
Codex --MCP stdio--> Python FastMCP server
                          |
                          | 127.0.0.1 + private token
                          | 4-byte network-order length + JSON
                          v
                 RobotStudio 2025.3 Add-In
                          |
                  Station SDK + PC SDK
                          v
                 Station / Virtual Controller
```

## Install on Windows

From this directory in PowerShell:

```powershell
.\scripts\install_python_server.ps1
.\robotstudio_extension\installer\install_extension.ps1
.\scripts\register_codex_mcp.ps1
.\scripts\install_codex_skill.ps1
```

Then start RobotStudio 2025.3, open or create a Station, and ensure its Virtual Controller is available. Restart Codex (or start a new Codex task) after MCP registration.

To create an ABB-compatible package for installation through **Add-Ins > Install Package**:

```powershell
.\robotstudio_extension\installer\build_package.ps1
```

Verify the non-live installation:

```powershell
.\scripts\verify_installation.ps1
```

Verify the live bridge while RobotStudio is running:

```powershell
.\.venv\Scripts\python.exe .\scripts\probe_bridge.py
```

Run all static, protocol, and build tests:

```powershell
.\scripts\run_all_smoke_tests.ps1
```

Add `-IncludeLive` only while RobotStudio and the Add-In are active.

## First calls from Codex

1. `get_environment`
2. `get_bridge_status`
3. `get_live_capabilities`
4. `get_safety_policy`
5. `get_active_station` and `get_station_summary`
6. Station or Virtual Controller read tools as needed

Every tool returns `ok`, operation/scope/side-effect metadata, a request ID, structured result or error, warnings, evidence, and elapsed time. An offline bridge is an explicit unavailable state, never mock Station data.

## Configuration

The installer creates user-private runtime files outside the repository:

- `%LOCALAPPDATA%\RobotStudioMCP\bridge-token`
- `%LOCALAPPDATA%\RobotStudioMCP\bridge-settings.json`
- `%USERPROFILE%\Documents\RobotStudioMCP\workspace`

The token is never stored in Codex configuration or logs. Codex receives only its file path.

See [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), [CAPABILITY_AUDIT.md](CAPABILITY_AUDIT.md), and [DEVELOPMENT.md](DEVELOPMENT.md).

## Uninstall

```powershell
.\scripts\unregister_codex_mcp.ps1
.\scripts\uninstall_codex_skill.ps1
.\robotstudio_extension\installer\uninstall_extension.ps1
```

The uninstaller retains the user token, shared settings, workspace, and evidence. Remove those manually only if their exact contents are no longer needed.
