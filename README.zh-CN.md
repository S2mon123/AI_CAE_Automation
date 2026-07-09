# AI CAE Automation Lab

这是一个面向公开 GitHub 的 AI 辅助 CAE 自动化知识与工具仓库。它的目标不是堆教程链接，而是把仿真任务整理成可检查、可执行、可复盘、可持续扩展的工程流程。

核心闭环：

```text
任务目标 -> 环境检查 -> 运行记录 -> 求解器桥接 -> 证据导出 -> 可信度评级 -> 复盘报告
```

仓库只保留重写后的开源友好内容：工作流、清单、Prompt 模板、示例目录、轻量脚本和 MCP 工具箱。不放私人笔记原文、非公开资料、商业软件工程文件、许可证信息、账号凭据和未脱敏结果。

## 仓库定位

- 建立 AI + CAE + MCP + Prompt + 证据链的一体化工作台。
- 覆盖 Abaqus、Ansys Fluent、Workbench/Mechanical、COMSOL、MATLAB/Simulink、OpenFOAM、ParaView、PCSCHEMATIC Automation 等方向。
- 让每次仿真或电气 CAD 自动化任务先检查环境，再执行真实软件，最后导出日志、图片、CSV、工程文件等证据。
- 区分预览、dry-run、功能验证、工程初稿和报告级结果，避免把演示当作可信工程结论。

## 目录结构

| 路径 | 用途 |
| --- | --- |
| `docs/` | 架构、流程、软件矩阵、GitHub 发布计划、MCP 工具箱路线 |
| `prompts/` | 可复制的 AI 仿真 Prompt 模板 |
| `checklists/` | smoke test、证据链、可信度检查 |
| `mcp/` | MCP 接入、桥接模式、工具说明 |
| `codex-skills/` | 可安装到 Codex 的 CAE 技能包 |
| `configs/` | 可公开的配置示例，不含本机私有路径 |
| `examples/` | 公开示例项目骨架，包含 COMSOL 10mm 立方体 smoke，不包含私有模型和结果 |
| `tests/` | 桥接计划、smoke 模板和证据评级的单元测试 |
| `scripts/` | 小型命令行辅助脚本 |
| `src/ai_cae_lab/` | 可复用 Python 工具和 MCP server |

## 快速开始

```powershell
git clone <your-repo-url>
cd AI-CAE-Automation-Lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
.\.venv\Scripts\ai-cae-toolbox.exe setup
.\.venv\Scripts\ai-cae-toolbox.exe doctor
```

`setup` 会在首次运行时自动发现 Abaqus、COMSOL、MATLAB、Ansys、Fluent、Workbench、PCSCHEMATIC，检查真实可执行文件，生成 `private/ai-cae.local.json`、`private/activate-ai-cae.ps1` 和 `private/codex-mcp.local.toml`。`private/` 已被 git 忽略，本机路径不会提交到公开仓库。

## Codex 接入

从 GitHub clone 后，建议先完成本机发现和私有配置生成，再把 MCP 工具箱和 skills 接入 Codex：

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
.\.venv\Scripts\ai-cae-toolbox.exe setup
. .\private\activate-ai-cae.ps1
.\.venv\Scripts\python.exe scripts\install_codex_assets.py --install-skills --force
```

然后把 `private/codex-mcp.local.toml` 中的 TOML 片段加入本机 Codex `config.toml`。生成的 MCP 配置会指向 `private/ai-cae.local.json`，不需要修改公开仓库文件，也不会继承作者电脑上的安装路径。完整步骤见 [`docs/codex-mcp-skill-setup.md`](docs/codex-mcp-skill-setup.md)。

当前可安装技能包：

- `ai-cae-run-manager`
- `abaqus-evidence-simulation`
- `fluent-evidence-cfd`
- `comsol-evidence-multiphysics`
- `open-toolchain-evidence`
- `pcschematic-evidence-cad`

## 按求解器限定上下文

普通建模任务不要扫描整个仓库。建议先运行：

```powershell
.\.venv\Scripts\ai-cae-toolbox.exe context-scope --solver comsol
.\.venv\Scripts\ai-cae-toolbox.exe toolchain-paths --solver comsol
```

对应 MCP 工具是 `solver_context_scope` 和 `solver_toolchain_paths`。它们会告诉 AI
只读取哪些文件，以及如何从用户本机环境变量或私有配置解析 `.exe` 路径，不假设作者电脑上的安装目录存在。首次运行建议先用 `ai-cae-toolbox setup` 或 MCP 工具 `setup_local_toolchain` 生成私有路径配置。
## MCP 自动化工具箱

```powershell
.\.venv\Scripts\ai-cae-toolbox.exe setup
.\.venv\Scripts\ai-cae-toolbox.exe discover --json
.\.venv\Scripts\ai-cae-toolbox.exe doctor
.\.venv\Scripts\ai-cae-toolbox.exe list-skills --json
.\.venv\Scripts\ai-cae-toolbox.exe list-adapters --json
.\.venv\Scripts\ai-cae-toolbox.exe bridge-plan --solver comsol --objective "验证 COMSOL Java 桥接"
.\.venv\Scripts\ai-cae-toolbox.exe create-run --solver comsol --case comsol-smoke --objective "验证求解器桥接流程"
.\.venv\Scripts\ai-cae-toolbox.exe write-smoke-template --solver comsol --run-dir runs\<run-id> --case comsol-smoke
.\.venv\Scripts\ai-cae-toolbox.exe scan-evidence runs\<run-id>
.\.venv\Scripts\ai-cae-toolbox.exe generate-report runs\<run-id>
.\.venv\Scripts\ai-cae-mcp-server.exe
```

当前 MCP server 暴露的关键工具包括首次发现/配置、上下文裁剪、运行记录、证据扫描和求解器桥接：

| 工具 | 作用 |
| --- | --- |
| `env_check` | 检查本机 Python、Git 和常见求解器路径候选，不启动商业软件 |
| `list_codex_skills` | 列出仓库提供的 Codex 技能包 |
| `list_solver_adapters` | 列出求解器适配器计划和能力 |
| `create_run_record` | 创建一次可追溯任务的运行目录 |
| `solver_context_scope` | 返回某个求解器任务需要读取的最小仓库上下文 |
| `solver_toolchain_paths` | 说明本机 `.exe` 路径解析顺序，避免使用作者机器路径 |
| `solver_bridge_plan` | 生成求解器桥接计划和推荐 MCP 工具 |
| `write_solver_smoke_template` | 写入最小求解器 smoke 模板 |
| `scan_run_evidence` | 扫描日志、脚本、求解器输出、图像、表格和报告 |
| `generate_run_report` | 根据证据生成 `report.md` 和可信度评级 |
| `abaqus_run_no_gui_script` | 调用 Abaqus/CAE noGUI 脚本并写入日志 |
| `abaqus_submit_input_deck` | 提交 Abaqus `.inp` 输入文件并写入日志 |
| `fluent_run_journal_file` | 批处理运行 Fluent journal 并写入日志 |
| `ansys_check_installation` | 检查 Ansys/Fluent/Workbench 配置路径 |
| `ansys_run_workbench_journal_file` | 批处理运行 Workbench journal 并写入日志 |
| `comsol_check_installation` | 检查 COMSOL 可执行文件、batch、compile、Java、mphserver 和 API 文档路径 |
| `comsol_write_cube_smoke_java` | 写入 10mm 立方体 COMSOL Java API smoke 模型 |
| `comsol_compile_java_file` | 使用 `comsolcompile` 编译 COMSOL Java API 脚本 |
| `comsol_run_compiled_java_class` | 通过 COMSOL batch 运行编译后的 Java class |
| `comsol_run_java_model_to_mph_file` | 一键编译 Java API 模型并输出 `.mph` 文件 |
| `comsol_run_batch_file` | 运行 COMSOL batch 命令并写入日志 |
| `matlab_check_installation` | 检查 MATLAB 路径 |
| `matlab_run_script_file` | 批处理运行 MATLAB 脚本 |
| `openfoam_check_installation` | 检查 OpenFOAM 或 WSL 可用性 |
| `openfoam_run_case_command` | 对 OpenFOAM case 运行指定命令 |
| `paraview_check_installation` | 检查 ParaView/pvpython 路径 |
| `paraview_run_pvpython_script` | 运行 ParaView 后处理脚本 |
| `pcschematic_check_installation` | 检查 PCSCHEMATIC 路径配置 |

## 重点示例

- [`examples/fluent-sinusoidal-weld-pool`](examples/fluent-sinusoidal-weld-pool/README.md)：正弦轨迹焊接熔池 Fluent 工作流。
- [`examples/comsol-cube-10mm`](examples/comsol-cube-10mm/README.md)：COMSOL Java API 10mm 立方体 smoke，验证从零建模、网格和 `.mph` 保存链路。
- [`examples/comsol-ehd-soybean-drying`](examples/comsol-ehd-soybean-drying/README.md)：COMSOL 等效 EHD 离子风黄豆干燥工作流。
- [`examples/mcp-smoke-workflows`](examples/mcp-smoke-workflows/README.md)：别人 clone 后验证 MCP 工具箱层的最小流程。

## 测试

```powershell
python -m unittest discover -s tests
```

这些测试验证桥接计划、COMSOL cube 模板生成、run 状态流转、日志信号解析和证据分类，不需要商业 CAE 软件许可证。

## 工作原则

1. 不伪造求解成功。
2. 不把预览、截图、几何预览说成真实仿真结果。
3. 每次真实任务都导出日志、结果文件、图片、CSV/JSON 或报告。
4. 失败时记录失败步骤、错误日志和下一步最小修复动作。
5. 公开仓库只保留脱敏、重写、可复用的知识结构。
6. 电气 CAD 任务必须追溯真实元件、符号、数据库字段、图纸页和导出清单。

## 推荐阅读顺序

1. [`docs/architecture.md`](docs/architecture.md)
2. [`docs/workflow.md`](docs/workflow.md)
3. [`docs/software-matrix.md`](docs/software-matrix.md)
4. [`docs/deep-solver-bridge-mcp.md`](docs/deep-solver-bridge-mcp.md)
5. [`docs/mcp-toolbox-roadmap.md`](docs/mcp-toolbox-roadmap.md)
6. [`mcp/solver-bridge-toolbox.md`](mcp/solver-bridge-toolbox.md)
7. [`docs/codex-mcp-skill-setup.md`](docs/codex-mcp-skill-setup.md)
8. [`docs/local-mcp-source-audit.md`](docs/local-mcp-source-audit.md)
9. [`prompts/ai-cae-general.md`](prompts/ai-cae-general.md)
10. [`prompts/comsol-ehd-soybean-drying.md`](prompts/comsol-ehd-soybean-drying.md)

## 状态

当前处于 bridge-preview 阶段。项目已经具备本地工具箱、MCP server、运行记录、日志信号解析、证据扫描、报告生成、基础求解器适配器，以及第一个 COMSOL Java API 真实建模 smoke；后续重点是继续增加 Abaqus、Fluent、Workbench 等 solver-native 可运行最小案例。

## 许可证

MIT。见 [`LICENSE`](LICENSE)。
