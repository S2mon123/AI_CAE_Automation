# Design Traceability

| Design requirement | 0.1.0 implementation |
|---|---|
| MCP stdio | `robotstudio_mcp.server`, explicit `transport="stdio"` |
| Loopback + token bridge | Python `BridgeClient`; C# `LocalBridgeServer`, `AuthenticationService` |
| Payload/timeout limits | Both bridge endpoints |
| Fixed methods, no eval/reflection | Python capability allowlist + C# `MethodRegistry` |
| UI-thread Station SDK | `UiThreadDispatcher` |
| Environment and version audit | `EnvironmentProbe`, build/install scripts |
| Workspace isolation | `WorkspaceGuard`, `ProjectService` |
| Structured results/errors | `result_models.py`, C# envelopes |
| Tools/resources/prompts | dedicated registration modules |
| Station reads | `StationAdapter` |
| VC/RAPID/Event Log/I/O reads | `ControllerAdapter` with double virtual check |
| Audit without secrets | Python `AuditLogger`, C# `BridgeLogger` |
| Phase boundary | no write or execution method registered |

Phase 2 and later requirements remain deliberately unimplemented.
