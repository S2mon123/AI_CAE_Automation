# Development

## Build and test

```powershell
.\scripts\install_python_server.ps1
.\scripts\run_all_smoke_tests.ps1
```

The C# build script discovers RobotStudio 2025 and Visual Studio 2022 Build Tools. It verifies that RobotStudio.exe and all referenced ABB SDK assemblies share the audited `25.3` version prefix. If the .NET Framework 4.8 developer pack is absent, it downloads Microsoft's reference-assembly NuGet package into `%LOCALAPPDATA%\RobotStudioMCP\build-cache`; it does not copy ABB DLLs into the repository.

## Test levels in 0.1.0

- L0: Ruff and manifest/schema checks.
- L1: Python settings, path traversal, project, authentication, timeout/offline, and MCP surface tests.
- L2: C# authentication and framing contract executable.
- L3: Python mock TCP bridge contract.
- L4: a subprocess FastMCP stdio smoke test.
- L5-L8: require RobotStudio, an active Station, and a Virtual Controller; never mark these passed when unavailable.

## Adding a bridge method

Add a concrete adapter method, register it with an explicit side effect in C# `MethodRegistry`, mirror it in Python `bridge/contracts.py`, add a typed MCP tool, and add tests. Do not add generic object paths, reflection, commands, source evaluation, or controller identifiers supplied by the model. Keep real-controller access absent.
