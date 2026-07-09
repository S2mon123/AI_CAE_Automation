# COMSOL MCP Package

This package starts the shared AI CAE MCP server with the `comsol` profile. It
is the recommended entry point for COMSOL-only modeling and smoke testing.

## Tools

- `comsol_check_installation`
- `comsol_write_cube_smoke_java`
- `comsol_compile_java_file`
- `comsol_run_compiled_java_class`
- `comsol_run_java_model_to_mph_file`
- `comsol_write_mph_validator_java`
- `comsol_validate_mph_loadable_file`
- `comsol_run_batch_file`
- common discovery, run-record, evidence, and report tools

## Start

From the repository root:

```powershell
.\.venv\Scripts\python.exe mcp\comsol\server.py
```

Before the first real COMSOL run:

```powershell
.\.venv\Scripts\ai-cae-toolbox.exe setup
.\.venv\Scripts\ai-cae-toolbox.exe doctor
```

The setup command writes local paths to `private/ai-cae.local.json`. Those paths
are ignored by git and should never be committed.

## Smoke Workflow

The first solver-native smoke case is in
`examples/comsol-cube-10mm`. It creates a real 10 mm cube with the COMSOL Java
API, saves an `.mph` file, and validates that the `.mph` can be loaded again.

Use this package when asking Codex to run only COMSOL tasks, so it does not need
to inspect Abaqus, Fluent, MATLAB, or other solver bridge files.
