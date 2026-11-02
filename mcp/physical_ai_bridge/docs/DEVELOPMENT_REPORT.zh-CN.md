# Physical AI v4 首轮开发与差异报告

日期：2026-09-27。设计基线 v4.0；本次软件版本 0.4.0。

## 结论与方案要点

已在现有仓库中完成首轮**只读接入代码、离线任务层和配套 Skill**，并为旧
RobotStudio MCP 增加正方体场景检查。尚未完成 PLC/ABB/虚拟控制器现场接通，
也尚未实现真实运动执行。不能把本报告解释为 P1/P2 现场退出条件已满足。

两份用户提供的 v4 文件已完整审阅。聊天分享链接两次读取均超时，因此未声称
读到了该聊天全文。用户随后明确不再采用 v0.2，故没有等待旧压缩包，也没有
编造旧包测试结果或宣称协议兼容；新协议明确标为 `physical-ai/4.0`。

v4 的关键决定：

1. 保留 PLC→EL6631→ABB 的既有控制链。Codex/MCP 负责任务和工程流程，
   PLC/RAPID 承担确定性时序和运动，模型不参与毫秒级控制。
2. A 为既有 Routine，B 为参数化路径，C 为新增独立模块；类别不是风险等级。
   Start bit 只能触发当前等待代码，不能选择任意新模块。
3. 先以 200 mm 正方体建立场景：16 段、12 条棱、回到起点、保持 TCP 姿态。
   v50 配 30% 倍率的名义时间约 213.33 s，不能固定 120 s 完成超时。
4. 先冻结起点、配置和 Tool/Load/WObj，再生成和验证。未知、过期或不匹配
   的证据不得放行；静态几何检查不能冒充编译、可达性和碰撞仿真。
5. Start TRUE/FALSE 都可能触发运动，Done 只读，Start 清零不是 Stop。
   独立 Stop、持续 Supervisor、命令账本和人工批准必须先于实际自动运动。
6. 新模块采用增量部署与回读验证，保留原 main/生产代码；AI_ 前缀不构成所有权。

## 1. 现有代码与 v4 的差异

原 `mcp/robotstudio` 具备环境、项目文件、Station 和 VC 只读工具，保留了
Python `virtual_only` 与 C# `IsVirtual` 检查。原代码不具备 PLC/ADS 桥接、
真实控制器独立读取、任务生成、真实仿真或执行闭环。原 Skill 围绕通用检查，
缺少当前正方体场景。本次基线回归为 11 项通过。

本次没有通过删除虚拟控制器限制来扩展真机权限，而是增加独立只读组件：

| 范围 | 新增/修改 | 状态与实际边界 |
|---|---|---|
| 新 MCP | `mcp/physical_ai_bridge`，15 个工具，官方 MCP SDK 1.29.0 | IMPLEMENTED / OFFLINE_TESTED；STDIO 实际启动和调用通过 |
| Win7 bridge | C# x86，HMAC、请求/响应绑定、nonce、客户端白名单、BOOL 元数据读取 | IMPLEMENTED / WINDOWS_TESTED（编译与契约）；实际 Win7/ADS 为 UNKNOWN |
| ABB proxy | 独立 PC SDK x64 进程，GUID/IP/虚实类型锁定，读取状态、PP、模块元数据和指定 I/O | IMPLEMENTED / WINDOWS_TESTED（编译）；实际 IRC5 读取为 UNKNOWN |
| Task core | A 登记，B/C 本地 RAPID、冻结上下文、唯一命名、SHA-256 manifest | IMPLEMENTED / OFFLINE_TESTED；未编译/加载到 VC 或真机 |
| Evidence gate | 所有关键项 PASS、时间和任务/代码/上下文绑定检查 | IMPLEMENTED / OFFLINE_TESTED；提交者真实性未认证，永不发运动凭据 |
| TC2 | 读取 TSM XML、保留原始字节副本、输出未应用 Link proposal | IMPLEMENTED / OFFLINE_TESTED；没有 COM 修改副本或激活功能 |
| 旧 MCP | `inspect_cube_task_context`、场景测试与说明 | IMPLEMENTED / OFFLINE_TESTED；入口相符不等于等待协议成立 |
| Skill | 新 `abb-physical-ai` 与修订 `robotstudio-core` | 两份结构校验通过；仓库索引已更新 |

## 2. 实际检测的环境

- `WINDOWS_TESTED`：Windows 11，Python 3.12.7，RobotStudio 25.3.11371.0。
- `WINDOWS_TESTED`：已安装的 RobotStudio、Stations、Controllers、PC SDK、Math
  五个 SDK 程序集版本均为 25.3.11371.0。
- `WINDOWS_TESTED`：本机存在 .NET Framework 编译器，桥接 x86 与 ABB 代理 x64
  实际编译成功；未复制厂商 DLL。
- `DOCUMENT_REPORTED`：IRC5/RW6.16、CX9020、EL6631、616-1、现场信号映射。
  没有把这些报送值升级为本轮现场观测。
- `UNKNOWN`：AMS、实际活动 TSM/PLC 工程、允许符号拼写、实际控制器 GUID、
  Tool/Load/WObj、起点、停止通道和当前许可证。
- 主机找到了 VMware 网络和既有 RDP 目标线索；具体私网地址只留在本地报告。
  检查时未看到 RobotStudio/VMware VM 运行进程，未启动它们或变更网络。

## 3. 真实读通的接口

本轮已读通本机环境/SDK信息、两个 MCP 的本地 STDIO，以及 Python↔C# 的
离线签名协议契约。**没有读通 PLC ADS、真实 ABB、Station 或 VC。**
实际探测旧 Add-In 返回 `RS_BRIDGE_OFFLINE`。

历史仓库记录曾将 Add-In 离线归因于 Free 许可；本轮没有重新读取许可证，
不能断言当前仍是同一原因。PC Interface 控制器选项与 Add-In Premium 许可
确实是不同条件，见 [ABB PC SDK 安装要求](https://developercenter.robotstudio.com/api/pcsdk/articles/Manual/Installation-and-development-environment/Installation-overview.html)
和 [RobotStudio SDK 许可要求](https://developercenter.robotstudio.com/api/robotstudio/articles/Introduction/Installation.html)。
官网当前包含 2026/.NET 10 信息；本次构建采用实际已安装 25.3 程序集。

## 4. 测试与构建结果

| 检查 | 结果 | 不代表什么 |
|---|---|---|
| 新 Physical AI Python 测试 | **82 passed** | 不代表真实 ADS、ABB 或运动验收 |
| RobotStudio 全量回归 | **15 passed**，一个原有 Authlib 弃用警告 | 不代表 Add-In 已加载 |
| C# Bridge 拒绝策略检查 | **13 passed**，未加载 ADS DLL | 不代表现场权限/网络已验收 |
| Python↔C# HMAC 契约 | 成功；错误密钥拒绝，测试包含在 82 项内 | 不代表 VM HTTP 端口已开通 |
| 新 MCP STDIO | 15 工具；建任务→生成→验证缺失→执行 BLOCKED 实际调用通过 | 不代表部署/执行工具已实现 |
| 旧 MCP STDIO | 33 工具、14 resources、4 prompts | 不代表实时 Station 能用 |
| 两个 C# 程序 | 编译成功：Win7 bridge x86、ABB proxy x64 | 未在 Win7/IRC5 上运行 |
| 两份 Skill | quick_validate 通过 | 不代表所有现场行为已验证 |
| Python lint | 新组件与旧组件新增部分通过 | 不替代测试或现场验收 |
| Python wheel | `abb_physical_ai_mcp-0.4.0-py3-none-any.whl` 构建成功 | 不含厂商 DLL，也不含第三方依赖离线包 |

重点覆盖：几何闭合和不同棱数、无效数值、RAPID 标识符注入、不可覆盖已有
文件、任务上下文变化、报告过期、未知验证项、XML DTD、路径越界、写接口
拒绝、签名错误、重放、响应 nonce/目标不符、超时不重试、旧 J6 入口、
读取期间控制器身份变化。测试替身明确不产出 FIELD_VERIFIED。

## 5. 未实现和未验证

以下不是已经工作的能力：实际 Stop、统一运动审批发行、持久运动 Supervisor/
命令账本、PLC 写入、COM Link 修改/激活/重启、RAPID 源码在线导出、完整
RobotStudio 自动编译/整段可达性/碰撞验证、真机增量部署/回读、执行/恢复、HMI。

`task_simulate` 明确未实现；`task_prepare_execute` 明确 BLOCKED；
`robot_request_process_stop` 明确 STOP_UNAVAILABLE。提供这些状态工具不等于
实现对应现场动作。Link proposal 也没有修改 TSM 内的 Link。

TC2 不能照搬 TC3 的 `ProduceMappingInfo`：厂商方法表注明其自 TC3.1 起
可用，参见 [Beckhoff ITcSysManager](https://infosys.beckhoff.com/content/1031/tcautomationinterface/12425792395.html)。
ADS 元数据查询依据 [Beckhoff 变量声明读取示例](https://infosys.beckhoff.com/content/1033/tcadsdll2/12470798475.html)，
实际本站 BOOL/符号仍需首次读通核对。

## 6. 文件和回滚

新增主要目录：`mcp/physical_ai_bridge/`、`codex-skills/abb-physical-ai/`。
修改旧 `mcp/robotstudio` 的 Python 工具注册、指令及新增场景工具/测试，
修改旧 Skill；仓库 MCP/Skill 索引同步增加入口。
没有修改 C# Add-In 的虚实控制器限制，也没有覆盖生产文件。

原有相关文件已外部备份，记录 SHA-256、Git 基线与未提交修改。精确本机路径
见私有交付报告。按 [ROLLBACK.md](ROLLBACK.md) 仅恢复本次修改，避免清空
原有其他未提交工作。没有执行提交、推送或向公开仓库上传。

## 7. 下一阶段最少所需信息

优先运行 [DEPLOYMENT.md](DEPLOYMENT.md) 中的一条 Win7 本地只读探测命令，
提供生成报告；再依据实际候选确认活动 PLC/Runtime/符号与已有文件传输通道。
ABB 侧需实际 GUID/IP、允许只读账号和信号；Station 侧需 Add-In 可用、VC 与
模型/工具/工作对象。不要要求用户凭记忆填写 AMS 或凭资料猜路径。

这些条件具备后才能做真实 P1/P2 读取与交叉核对。物理动作阶段还需完成上述
执行组件开发和独立 Stop 现场验收。本次未写现场 PLC、未加载真机 RAPID、
未移动 PP、未请求 Motor On/Start/Resume，也未执行实体 Stop 测试。
