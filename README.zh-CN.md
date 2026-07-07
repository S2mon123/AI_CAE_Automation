# AI CAE Automation Lab

这是一个面向公开 GitHub 的 AI 自动化仿真知识与工具仓库。它的目标不是堆教程链接，而是把 CAE 任务整理成可检查、可执行、可复盘、可持续扩展的工程流程。

核心闭环：

```text
任务目标 -> 环境检查 -> 建模/网格/求解 -> 真实软件证据 -> 后处理导出 -> 复盘入库
```

本仓库只放重写后的开源友好内容：工作流、清单、Prompt 模板、示例目录和轻量脚本。不放私有笔记原文、会员资料、商业软件工程文件、许可证信息、账号凭据和未脱敏结果。

## 仓库定位

- 建立 AI + CAE + MCP + Prompt + 证据链的一体化工作台。
- 支持 Abaqus、Fluent、Workbench/Mechanical、COMSOL、MATLAB/Simulink、OpenFOAM、ParaView 等方向的长期整理。
- 让每次仿真任务都先检查环境、再执行真实软件、最后导出日志/图像/CSV/工程文件等证据。
- 把“功能验证、视觉验证、工程初步、报告级结果”分开，避免把演示当成可信工程结果。

## 目录结构

| 路径 | 用途 |
|---|---|
| `docs/` | 架构、流程、软件矩阵、GitHub 发布计划 |
| `prompts/` | 可复制的 AI 仿真 Prompt 模板 |
| `checklists/` | smoke test、证据链、可信度检查 |
| `mcp/` | MCP 接入、桥接模式、配置说明 |
| `examples/` | 公开示例项目骨架，不包含私有模型和结果 |
| `scripts/` | 小型命令行辅助脚本 |
| `src/ai_cae_lab/` | 可复用 Python 工具 |

## 快速开始

```powershell
git clone <your-repo-url>
cd AI-CAE-Automation-Lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe scripts\env_check.py --json
```

环境检查脚本只做路径探测，不会启动商业软件，也不会修改工程文件。

## 最重要的工作原则

1. 不伪造求解成功。
2. 不把 viewer、截图、几何预览说成真实仿真结果。
3. 每次真实任务都导出日志、结果文件、图片、CSV/JSON 或报告。
4. 失败时记录失败步骤、错误日志和下一步最小修复动作。
5. 公开仓库只保留脱敏、重写、可复用的知识结构。

## 推荐阅读顺序

1. [`docs/architecture.md`](docs/architecture.md)
2. [`docs/workflow.md`](docs/workflow.md)
3. [`docs/software-matrix.md`](docs/software-matrix.md)
4. [`checklists/smoke-test.md`](checklists/smoke-test.md)
5. [`prompts/ai-cae-general.md`](prompts/ai-cae-general.md)
