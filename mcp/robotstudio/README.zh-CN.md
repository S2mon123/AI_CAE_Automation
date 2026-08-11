# RobotStudio MCP Server

运行时许可要求：ABB 规定，引用 `ABB.Robotics.RobotStudio.dll` 的 Add-In 必须在 RobotStudio Premium 许可下运行。Free 许可下 MCP stdio 服务仍可启动，但进程内 Bridge 和 Station 工具会明确返回 `RS_BRIDGE_OFFLINE`，不会伪造实时数据，也不会绕过许可检查。

面向 ABB RobotStudio 2025.3 的本地 MCP 集成。工程由 Codex 启动的 Python FastMCP stdio 服务和 RobotStudio 进程内 C# Add-In 组成。

`0.1.0` 严格只实现总体设计的 Phase 0 与 Phase 1：

- 本机 RobotStudio/SDK 探测，并严格核对 25.3 小版本；
- 隔离项目工作区、文件哈希与证据检查点；
- Add-In 实时 Ping 与固定能力表；
- Station、机器人、ToolData、WorkObject、Target、Path 只读；
- Virtual Controller 状态、程序指针、RAPID 任务/模块元数据、Event Log、I/O 只读；
- MCP Tools、Resources、Prompts、结构化错误与审计日志。

本版本不暴露 Station 写入、RAPID 传输/加载/写入、I/O 写入、程序执行、Reset PP、任意代码执行或真实控制器连接。

## 安装

在本目录打开 PowerShell：

```powershell
.\scripts\install_python_server.ps1
.\robotstudio_extension\installer\install_extension.ps1
.\scripts\register_codex_mcp.ps1
.\scripts\install_codex_skill.ps1
```

随后启动 RobotStudio 2025.3，打开或创建 Station，并准备 Virtual Controller。MCP 注册后重启 Codex 或新建 Codex 任务。

非实时验证：

```powershell
.\scripts\verify_installation.ps1
```

RobotStudio 运行时验证 Bridge：

```powershell
.\.venv\Scripts\python.exe .\scripts\probe_bridge.py
```

运行静态、协议、MCP 与 C# 构建测试：

```powershell
.\scripts\run_all_smoke_tests.ps1
```

仅在 RobotStudio 和 Add-In 已运行时追加 `-IncludeLive`。

## Codex 首次调用顺序

1. `get_environment`
2. `get_bridge_status`
3. `get_live_capabilities`
4. `get_safety_policy`
5. `get_active_station`、`get_station_summary`
6. 按需调用 Station 或 Virtual Controller 只读工具

Bridge 离线时会返回明确的不可用状态，不返回模拟 Station 数据。

## 运行时文件

安装器在仓库外生成：

- `%LOCALAPPDATA%\RobotStudioMCP\bridge-token`
- `%LOCALAPPDATA%\RobotStudioMCP\bridge-settings.json`
- `%USERPROFILE%\Documents\RobotStudioMCP\workspace`

Token 不写入 Codex 配置和日志，Codex 配置只保存 Token 文件路径。

参见 [ARCHITECTURE.md](ARCHITECTURE.md)、[SECURITY.md](SECURITY.md)、[CAPABILITY_AUDIT.md](CAPABILITY_AUDIT.md) 和 [DEVELOPMENT.md](DEVELOPMENT.md)。

## 卸载

```powershell
.\scripts\unregister_codex_mcp.ps1
.\scripts\uninstall_codex_skill.ps1
.\robotstudio_extension\installer\uninstall_extension.ps1
```

卸载器保留用户 Token、共享设置、工作区和证据，只有确认不再需要后才应手动删除。
