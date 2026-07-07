# AI CAE Automation Lab

这是一个面向公开 GitHub 的 AI 辅助 CAE 自动化知识与工具仓库。它的目标不是堆教程链接，而是把仿真任务整理成可检查、可执行、可复盘、可持续扩展的工程流程。

核心闭环：

```text
任务目标 -> 环境检查 -> 运行记录 -> 求解器桥接 -> 证据导出 -> 可信度评级 -> 复盘报告
```

本仓库只保留重写后的开源友好内容：工作流、清单、Prompt 模板、示例目录和轻量脚本。不放私人笔记原文、会员资料、商业软件工程文件、许可证信息、账号凭据和未脱敏结果。

## 仓库定位

- 建立 AI + CAE + MCP + Prompt + 证据链的一体化工作台。
- 支持 Abaqus、Ansys Fluent、Workbench/Mechanical、COMSOL、MATLAB/Simulink、OpenFOAM、ParaView、PCSCHEMATIC Automation 等方向的长期整理。
- 让每次仿真或电气 CAD 自动化任务先检查环境，再执行真实软件，最后导出日志、图像、CSV、工程文件等证据。
- 把“功能验证、视觉验证、工程初稿、报告级结果”分开，避免把演示当成可信工程结果。

## 目录结构

| 路径 | 用途 |
|---|---|
| `docs/` | 架构、流程、软件矩阵、GitHub 发布计划、MCP 工具箱路线 |
| `prompts/` | 可复制的 AI 仿真 Prompt 模板 |
| `checklists/` | smoke test、证据链、可信度检查 |
| `mcp/` | MCP 接入、桥接模式、工具说明 |
| `codex-skills/` | 可安装到 Codex 的 CAE 技能包 |
| `configs/` | 可公开的配置示例，不含本机私有路径 |
| `examples/` | 公开示例项目骨架，不包含私有模型和结果 |
| `scripts/` | 小型命令行辅助脚本 |
| `src/ai_cae_lab/` | 可复用 Python 工具 |

## 快速开始

```powershell
git clone <your-repo-url>
cd AI-CAE-Automation-Lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
.\.venv\Scripts\ai-cae-toolbox.exe env-check --json
```

## Codex 一键接入

从 GitHub clone 后，可以把 MCP 工具箱和 skills 安装进本机 Codex：

```powershell
.\.venv\Scripts\python.exe scripts\install_codex_assets.py --install-skills --force
.\.venv\Scripts\python.exe scripts\install_codex_assets.py --write-mcp-toml .\private\codex-mcp.local.toml
```

然后把生成的 TOML 片段加入本机 Codex `config.toml`，把可选求解器路径替换为真实路径。完整步骤见 [`docs/codex-mcp-skill-setup.md`](docs/codex-mcp-skill-setup.md)。

当前可安装技能包：

- `ai-cae-run-manager`
- `abaqus-evidence-simulation`
- `fluent-evidence-cfd`
- `pcschematic-evidence-cad`

## MCP 自动化工具箱

第一版 MCP 工具箱先做通用底座，不直接启动商业求解器：

```powershell
.\.venv\Scripts\ai-cae-toolbox.exe list-skills --json
.\.venv\Scripts\ai-cae-toolbox.exe list-adapters --json
.\.venv\Scripts\ai-cae-toolbox.exe create-run --solver fluent --case sinusoidal-welding-smoke --objective "验证求解器桥接流程"
.\.venv\Scripts\ai-cae-toolbox.exe scan-evidence runs\<run-id>
.\.venv\Scripts\ai-cae-toolbox.exe generate-report runs\<run-id>
.\.venv\Scripts\ai-cae-mcp-server.exe
```

当前 MCP server 暴露四个工具：

| 工具 | 作用 |
|---|---|
| `env_check` | 检查本机 Python、Git 和常见求解器路径候选，不启动商业软件 |
| `create_run_record` | 创建一次可追溯任务的运行目录 |
| `scan_run_evidence` | 扫描日志、脚本、求解器输出、图像、表格和报告 |
| `generate_run_report` | 根据证据生成 `report.md` 和可信度评级 |
| `list_codex_skills` | 列出仓库提供的 Codex 技能包 |
| `list_solver_adapters` | 列出求解器适配器计划和能力 |
| `abaqus_run_no_gui_script` | 调用 Abaqus/CAE noGUI 脚本并写入日志 |
| `abaqus_submit_input_deck` | 提交 Abaqus `.inp` 输入文件并写入日志 |
| `fluent_run_journal_file` | 批处理运行 Fluent journal 并写入日志 |
| `pcschematic_check_installation` | 检查 PCSCHEMATIC 路径配置，不启动软件 |

Abaqus、Fluent、PCSCHEMATIC 已有最小适配器；COMSOL、MATLAB/Simulink、OpenFOAM、ParaView 会继续扩展。

## 工作原则

1. 不伪造求解成功。
2. 不把预览器、截图、几何预览说成真实仿真结果。
3. 每次真实任务都导出日志、结果文件、图片、CSV/JSON 或报告。
4. 失败时记录失败步骤、错误日志和下一步最小修复动作。
5. 公开仓库只保留脱敏、重写、可复用的知识结构。
6. 电气 CAD 任务必须追溯真实元件、符号、数据库字段、图纸页和导出清单。

## 推荐阅读顺序

1. [`docs/architecture.md`](docs/architecture.md)
2. [`docs/workflow.md`](docs/workflow.md)
3. [`docs/software-matrix.md`](docs/software-matrix.md)
4. [`docs/mcp-toolbox-roadmap.md`](docs/mcp-toolbox-roadmap.md)
5. [`mcp/solver-bridge-toolbox.md`](mcp/solver-bridge-toolbox.md)
6. [`docs/codex-mcp-skill-setup.md`](docs/codex-mcp-skill-setup.md)
7. [`docs/electrical-cad-automation.md`](docs/electrical-cad-automation.md)
8. [`checklists/smoke-test.md`](checklists/smoke-test.md)
9. [`prompts/ai-cae-general.md`](prompts/ai-cae-general.md)
10. [`prompts/pcschematic-direct-motor-starter.md`](prompts/pcschematic-direct-motor-starter.md)

## 状态

当前处于早期公开结构搭建阶段。第一阶段目标是形成一个干净的文档与本地工具箱版本：环境检查、Prompt 模板、运行记录、证据扫描、报告生成和示例项目骨架。

## 许可证

MIT。见 [`LICENSE`](LICENSE)。
