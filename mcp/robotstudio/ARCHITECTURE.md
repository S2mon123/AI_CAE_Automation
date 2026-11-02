# Architecture

## Process boundaries

The Codex host starts `robotstudio_mcp` over stdio. The Python server owns MCP lifecycle, schemas, project isolation, errors, audit records, and the authenticated bridge client. The C# Add-In owns all ABB SDK calls inside RobotStudio 2025.3.

The bridge listens only on `127.0.0.1`. Each connection carries one UTF-8 JSON request and one response, framed by a four-byte unsigned network-order length. Every request includes a random token loaded from a current-user-only file. Payload and timeout limits are enforced on both sides.

Socket worker threads never call Station SDK objects. Requests are validated and authenticated first, then marshalled through a Windows Forms control created by `AddinMain` on RobotStudio's UI thread. Method dispatch is a fixed dictionary of typed handlers; method names never become reflection, shell, or script calls.

## Data boundaries

All managed project writes stay below `ROBOTSTUDIO_MCP_WORKSPACE/projects/{project_id}`. Explicit external imports accept one file, copy its basename into a fixed category, and record SHA-256. Runtime token/configuration and local evidence are outside the public repository.

Station data comes from `Station.ActiveStation` and its actual project objects. Controller data comes from PC SDK only after the active Station's `RsIrc5Controller.SystemId` resolves to a scanned `ControllerInfo` with `IsVirtual=true`. Controller sessions log on, perform one read workflow, log off, and dispose.

## Failure model

Unavailable components return stable `RS_*` codes. Bridge failure does not terminate the MCP server. The server never substitutes fixture data for a live result. Phase 0/1 project checkpoints are immutable evidence snapshots and deliberately report `rollback_available=false`.
