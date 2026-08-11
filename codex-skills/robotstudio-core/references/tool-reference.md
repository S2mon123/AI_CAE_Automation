# RobotStudio Phase 0/1 Tool Reference

## Environment and bridge

- `get_environment`: installation, SDK assemblies, Python, workspace.
- `get_version_compatibility`: strict 2025.3 match.
- `get_bridge_status`: authenticated live Add-In ping.
- `get_live_capabilities`: declared and live fixed method sets.
- `get_safety_policy`: enforced absent/write boundaries.

## Isolated projects

- `create_project`, `get_project_summary`
- `import_project_file`, `list_project_files`
- `create_project_checkpoint`, `list_project_artifacts`

These write only to the configured MCP workspace. A Phase 0/1 checkpoint is evidence, not an automatic rollback point.

## Station reads

- `get_active_station`, `get_station_summary`, `list_station_components`
- `list_robots`, `get_robot_info`
- `list_tools`, `list_workobjects`
- `list_targets`, `get_target`
- `list_paths`, `get_path`

## Virtual Controller reads

- `scan_controllers`: classification only; no real-controller connection.
- `get_controller_status`, `get_program_pointer`
- `list_rapid_tasks`, `list_rapid_modules`
- `get_event_log`, `get_event_log_since`
- `list_io_signals`, `read_io_signal`

Module source export is intentionally absent because PC SDK local export needs a controller filesystem transfer workflow reviewed in Phase 3.

## Stable errors

- `RS_ENV_NOT_FOUND`, `RS_VERSION_MISMATCH`
- `RS_BRIDGE_OFFLINE`, `RS_BRIDGE_AUTH_FAILED`, `RS_BRIDGE_PROTOCOL_ERROR`
- `RS_NO_ACTIVE_STATION`, `RS_CONTROLLER_NOT_CONNECTED`, `RS_CONTROLLER_NOT_VIRTUAL`
- `RS_ENTITY_NOT_FOUND`, `RS_INVALID_ARGUMENT`
- `RS_CAPABILITY_NOT_AVAILABLE`, `RS_TIMEOUT`

Do not translate an error into success. Preserve its code, message, `retryable`, request ID, and relevant details.
