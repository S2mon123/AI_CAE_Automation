# HyperMesh Skill 与 MCP 总结

本文总结 AI CAE Automation Lab 中 HyperMesh Skill 与 MCP Profile 的定位、
能力边界、切分逻辑、质量控制和推荐使用流程。

## 1. 总体定位

这套能力不是用一个大工具直接声称“完成划网格”，而是把 HyperMesh
自动化拆成可审计的步骤：

1. 选择壳单元、映射/扫掠六面体或四面体路线。
2. 检查 CAD 导入、拓扑和需要保留的物理特征。
3. 在切割几何前设计二维 patch 或三维 block 拓扑。
4. 计算孔、圆柱、圆角、边界及尺寸过渡的局部控制。
5. 通过显式 Tcl 和 `hmbatch -tcl` 执行。
6. 按求解器标准检查并修复网格质量。
7. 保存模型、求解器网格、质量统计、日志和报告。

Skill 负责告诉代理如何判断和组织流程；MCP 负责提供结构化规划工具、
本地 HyperMesh 调用、路径约束和证据接口。

```mermaid
flowchart LR
    A["用户目标与几何"] --> B["Skill 选择网格路线"]
    B --> C["MCP 生成切分与局部控制计划"]
    C --> D["编写并审核 Tcl"]
    D --> E["hmbatch 执行"]
    E --> F["质量检查与原因诊断"]
    F -->|"不合格"| C
    F -->|"合格"| G["HM、求解器网格、统计与报告"]
```

## 2. HyperMesh Skill

Skill 路径：
[`codex-skills/hypermesh-evidence-meshing/`](../codex-skills/hypermesh-evidence-meshing/)

### 2.1 触发范围

Skill 用于以下任务：

- CAD 导入、几何清理、中面或直接中面网格。
- 二维四边形网格流向设计和局部渐变。
- Solid Map、drag、line drag、linear solid 等六面体路线规划。
- 四面体边界面准备和四面体失败诊断。
- 球体、球壳、穹顶、法兰盘、轮毂、PCD/螺栓孔阵列及辅助线切分。
- 圆柱、圆孔、槽孔、washer、圆角、台阶、交叉体及周期结构。
- 材料、厚度、接触、载荷、约束和对称边界保护。
- skew、Jacobian、warpage、aspect、角度、tet collapse 等质量修复。
- BatchMesher、Tcl、hmbatch、求解器网格导出和证据报告。

### 2.2 核心工作流

Skill 要求按照以下顺序执行：

1. 创建独立 run 目录并保护原始 CAD。
2. 确认导入器状态和非零曲面/实体数量。
3. 定义求解器、单元类型/阶次、目标尺寸及质量标准。
4. 检查自由边、共享边、非流形边、重复面、相交面和法向。
5. 将特征分类为保留、seed、washer/局部控制或删除。
6. 先写切分计划，再逐组切割并复查拓扑和可映射性。
7. 设置边密度、偏置、曲率、washer、扫掠层及尺寸过渡。
8. 先划分困难 source/末端区域，再处理依赖区域。
9. 按失败原因修复，不用全局 smooth 掩盖拓扑问题。
10. 导出网格、质量统计、切分摘要、日志和报告。

### 2.3 切分与分块逻辑

详细规则见
[`references/partition-strategy.md`](../codex-skills/hypermesh-evidence-meshing/references/partition-strategy.md)。

二维切分的目标是得到流向稳定、边数兼容的 patch：

- 优先构造四边形友好的四边 patch。
- 将模型分成特征区、过渡区和远场规则区。
- 抑制没有物理意义且破坏网格流向的内部线。
- 保留材料、厚度、接触、载荷、约束和对称边界。
- 把不可避免的三角形或奇异点放在低梯度区域。

三维六面体分块的目标是得到基本可扫掠 block：

- 每个 block 明确 source、target、path、扫掠方向和共享面。
- 利用对称性先完成最小有效扇区。
- 从末端 block 向中心倒推依赖关系，再按反向顺序划网格。
- 在扫掠方向改变的位置设置三方向可映射连接 block。
- 分支或相贯结构先隔离支路，再解决中心连接区。
- 可映射状态仅代表拓扑允许，不代表 Jacobian 等质量合格。

不应为了“多切几刀”而切分。产生短边、薄片面、尖锐楔形、冲突扫掠
方向或最终不可映射残余块的切分必须撤销或重做。

### 2.4 特征网格策略

详细规则见
[`references/feature-meshing.md`](../codex-skills/hypermesh-evidence-meshing/references/feature-meshing.md)。

主要策略包括：

- 使用目标尺寸和每单元最大圆心角共同确定圆周分段数。
- 将分段数向上调整为对称扇区、周期结构或配合圆边所需倍数。
- 孔区按用途选择 radial washer、corner-quad washer、seed 或无 washer。
- 对螺栓孔、轴承孔设置固定/最少圆周单元数和更高优先级。
- washer 冲突时调整低优先级孔或建立共享过渡区。
- 槽孔明确圆头/矩形端处理并保持两侧边密度兼容。
- 圆角根据物理作用选择删除、保留曲率、沿中线切分或强制行数。
- 台阶和厚度变化使用显式过渡带，避免单排网格突变。
- 周期齿、叶片、辐条只在几何及工况确实周期一致时复制扇区网格。

尺寸渐变满足：

```text
n_transition >= ceil(log(h_coarse / h_fine) / log(growth_max))
growth_actual = (h_coarse / h_fine) ** (1 / n_transition)
```

### 2.5 球体与法兰盘专用分块

详细规则见
[`references/shape-partition-patterns.md`](../codex-skills/hypermesh-evidence-meshing/references/shape-partition-patterns.md)。

球体/球壳先测量圆心、三条局部轴、内外半径、厚度、开口、接触、载荷、
约束与对称面，再建立辅助线：

- 三个过圆心正交平面可用于验证 1/8 几何分区，但只有工况也对称时才能缩减分析模型。
- 经纬线式网格会在极点汇聚；全四边形球壳优先采用六个立方体投影四边 patch。
- 实心球的全六面体分块采用有限尺寸的立方体状中心核和六个外围曲面 block，禁止把所有径向线收敛到一个中心节点。
- 外球面、中心核界面、四分之一圆弧和复制接缝的节点数必须兼容；重点检查极点、奇异点、核过渡和接缝质量。

法兰盘先测量中心轴、外径/内孔、轮毂与台阶半径、PCD、孔径、孔数与初始相位、
盘厚/轮毂厚度、圆角、垫片及接触区，再建立：

- 内孔、轮毂/台阶、washer/接触、过渡和外缘所需的同心辅助圆；
- 穿过每个孔中心的径向线以及相邻孔之间的中分线；
- 从孔四分点/切点连接到 washer 或过渡圆的四边形友好分区；
- 轮毂、颈部、台阶和圆角的独立 source-target block，再进行轴向 Solid Map。

法兰规划同时计算孔间弦长净距、内侧净距、外缘净距、孔圆周分段、PCD 分段和
厚度层数。washer 与内孔、轮毂、相邻孔、垫片边界或外缘重叠时，必须建立共享过渡
或修改方案，不能靠 smooth 掩盖。只有几何、材料、接触、预紧、载荷和约束全部周期
一致时，才允许把一个螺距扇区作为循环对称分析模型。

### 2.6 质量诊断与修复

详细规则见
[`references/quality-remediation.md`](../codex-skills/hypermesh-evidence-meshing/references/quality-remediation.md)
和
[`references/quality-gates.md`](../codex-skills/hypermesh-evidence-meshing/references/quality-gates.md)。

修复顺序为：

1. 修复重复、重叠、自由边、法向和拓扑问题。
2. 修改几何特征、partition、边密度和过渡带。
3. 局部重新划分 patch 或 block。
4. 使用 split、swap、combine 调整连接关系。
5. 在固定特征/接口节点的前提下 smooth 或移动节点。
6. 只有具备求解器证据时才接受局部质量例外。

QI 是综合指标，不能代替各个求解器质量指标。报告必须保留每项指标的
失败数量、比例、最差值、位置及修复前后变化。

四面体专项规则见
[`references/tetra-quality-optimization.md`](../codex-skills/hypermesh-evidence-meshing/references/tetra-quality-optimization.md)。
它新增 `hm_getelemcheckvalues` 准确最差值/单元位置取证、Minimum Height 与
Tet Collapse/Aspect/Volume Skew 失败集合交集和空间聚类、几何特征与质量门槛
可实现性检查，以及“先表面三角形、后体网格”的修复闭环。当优化器改善不足
1% 或仅重编号失败单元时，方案必须返回短边、窄面、圆角、局部尺寸和边界
三角形处理，不再重复无效的节点优化。

## 3. HyperMesh MCP

MCP 路径：[`mcp/hypermesh/`](../mcp/hypermesh/)

主要实现：

- [`server.py`](../mcp/hypermesh/server.py)：HyperMesh Profile 入口和 stdio 启动。
- [`hypermesh_profile.py`](../mcp/hypermesh/hypermesh_profile.py)：资源、Prompt、规划工具、路径策略和增强 Tcl 执行。
- [`README.md`](../mcp/hypermesh/README.md)：安装、组件、研究来源和协议说明。
- [`tests/test_profile.py`](../mcp/hypermesh/tests/test_profile.py)：协议和规划逻辑测试。

### 3.1 HyperMesh 专用工具

| 工具 | 用途 |
| --- | --- |
| `hypermesh_mcp_manifest` | 查看 MCP 原语、SDK 责任及路径策略 |
| `hypermesh_check_installation` | 检查 `hmbatch`，不启动求解流程 |
| `hypermesh_validate_workspace_paths` | 验证 Tcl 和 run 目录是否位于授权工作区 |
| `hypermesh_plan_partition_strategy` | 为 quad shell、mapped hex 或 tetra 路线生成切分顺序、block contract、风险和验收条件 |
| `hypermesh_plan_size_transition` | 根据细/粗尺寸和最大增长率计算过渡层数及实际增长率 |
| `hypermesh_plan_circular_feature_mesh` | 计算圆周、曲率角、轴向和 washer/radial 分段 |
| `hypermesh_plan_fillet_chamfer_mesh` | 对圆角、倒角进行保留/抑制判定，计算行数、弦长、弦高误差和过渡 |
| `hypermesh_plan_tetra_quality_remediation` | 根据准确最差值、失败率/交集、最小几何特征与优化历史，输出四面体表面优先修复方案 |
| `hypermesh_plan_sphere_mesh` | 计算球体大圆/四分之一圆弧分段、非退化中心核、径向 block、壳厚层数和辅助切分顺序 |
| `hypermesh_plan_flange_mesh` | 计算法兰 PCD、孔分段、孔间/内外侧净距、同心辅助圆、孔中心径向线和轴向层数 |
| `hypermesh_list_client_roots` | 兼容查询客户端声明的旧版 MCP roots |
| `hypermesh_run_tcl_file` | 通过 `hmbatch -tcl` 运行显式 Tcl，记录日志、进度和路径策略 |

MCP 还继承 15 个通用 CAE 工具，包括环境检查、工具链发现、创建 run、
上下文收窄、bridge plan、smoke 模板、证据扫描及报告生成。因此服务器
当前共暴露 27 个工具。

### 3.2 Resources

MCP 暴露 9 个资源：

| URI | 内容 |
| --- | --- |
| `hypermesh://guidance/workflow` | Skill 主工作流 |
| `hypermesh://guidance/partition-strategy` | 二维 patch 与三维 block 切分策略 |
| `hypermesh://guidance/feature-meshing` | 孔、圆柱、圆角、过渡及边界局部控制 |
| `hypermesh://guidance/fillet-chamfer-meshing` | 圆角/倒角测量、保留/简化判定、行数与过渡控制 |
| `hypermesh://guidance/shape-partition-patterns` | 球体/球壳、法兰/轮毂、测量合同和辅助线分块模式 |
| `hypermesh://guidance/quality-remediation` | 网格质量原因诊断和修复顺序 |
| `hypermesh://guidance/tetra-quality-optimization` | 四面体准确质量取证、几何可行性、失败聚类、表面优先重划与验收规则 |
| `hypermesh://guidance/quality-gates` | 最终验收与阻断条件 |
| `hypermesh://server/manifest` | MCP Profile 组件清单 |

### 3.3 Prompt

`hypermesh_meshing_plan` 接收目标、几何特征、求解器、单元类型、目标尺寸
和质量标准，要求代理先读取上述资源，再输出可审计的切分、局部控制、
网格顺序和质量验证方案。

### 3.4 Roots 与路径安全

MCP Roots 是客户端能力，不是服务端必备模块，也不是文件访问沙箱。
Profile 保留 `hypermesh_list_client_roots` 作为协议兼容工具，但实际执行
边界使用：

- 工具参数 `workspace_root`；或
- 环境变量 `AI_CAE_HYPERMESH_WORKSPACE_ROOTS`。

配置路径边界后，Tcl 文件和 run 目录都必须解析到授权根目录内部。

## 4. Skill 与 MCP 的推荐调用顺序

1. 调用 `solver_context_scope("hypermesh")` 收窄上下文。
2. 调用 `hypermesh_mcp_manifest` 查看当前 Profile。
3. 调用 `hypermesh_check_installation` 检查 hmbatch。
4. 创建 run 目录并复制输入 CAD/Tcl，不覆盖原始文件。
5. 调用 `hypermesh_plan_partition_strategy` 选择切分和网格顺序。
6. 对圆孔/圆柱调用 `hypermesh_plan_circular_feature_mesh`。
7. 对球体/球壳调用 `hypermesh_plan_sphere_mesh`。
8. 对法兰/轮毂/螺栓孔阵列调用 `hypermesh_plan_flange_mesh`。
9. 对细粗网格区域调用 `hypermesh_plan_size_transition`。
10. 根据 Skill 资源编写并审核版本匹配的 Tcl。
11. 调用 `hypermesh_validate_workspace_paths`。
12. 调用 `hypermesh_run_tcl_file`。
13. 调用 `scan_run_evidence` 和 `generate_run_report`。
14. 按 quality gates 判断通过、修复或阻断。

## 5. 成功判据

必须同时满足：

- CAD 导入成功且预期几何实体非零。
- 切分后没有未解决的拓扑缺陷、薄片面、短边和不可映射残余块。
- 节点、二维和三维单元数量非零。
- 球体中心核/patch 或法兰径向区/扇区的共享边计数、接缝和分块顺序符合计划。
- 特征选择、washer、过渡层及 block 创建数量符合计划。
- 求解器相关质量指标通过，或例外已局部化并有工程依据。
- `.hm` 和目标求解器网格存在且非空。
- Tcl、命令行、hmbatch/BatchMesher 日志、质量统计和报告完整。

进程返回码为零或文件存在，单独都不能证明网格成功。

## 6. 当前边界

- MCP 不包含 HyperMesh、商业许可证或厂商手册。
- MCP 不假设未公开的 Python API。
- 新旧 HyperMesh 的 Ribbon、Classic UI 和 Tcl 命令可能不同；规划资源
  描述的是拓扑意图，实际命令必须按本机版本确认。
- 当前 MCP 执行用户提供的显式 Tcl，不会凭空生成并执行未经审核的
  版本相关命令。
- 规划公式和切分启发式是初始方案，最终必须通过求解器质量标准、
  网格收敛性和工程物理验证。

## 7. 本次球体/法兰补充的网络依据

社区资料用于发现常见操作模式，Altair 官方文档用于核对 HyperMesh 能力和边界：

- [哔哩哔哩：HyperMesh 球体结构化网格划分](https://www.bilibili.com/video/BV1TB421r7t9/)；
- [技术邻：HyperMesh 球体网格案例](https://www.jishulink.com/post/1818472)，明确使用 1/8 对称几何；
- [哔哩哔哩：HyperMesh 学习笔记](https://www.bilibili.com/opus/1035259234909945926)，包含控制点、贴面辅助线和共享边切分逻辑；
- [Altair：Measures](https://www.help.altair.com/2021/hwdesktop/hwx/topics/chapter_heads/measures_r.htm)，核对长度、角度、半径、面积、体积、重心和包围盒测量；
- [Altair：Features](https://help.altair.com/hwdesktop/hwx/topics/pre_processing/model_setup/features_r.htm)，核对孔、法兰和圆角的识别与关联；
- [Altair：Split with Lines](https://2025.help.altair.com/2025/hwdesktop/hwx/topics/pre_processing/geometry/surface_split_line_t.htm)，核对投影线、offset/washer split、图形线及切分预览；
- [Altair：Solid Map](https://2021.help.altair.com/2021/hwdesktop/hwx/topics/pre_processing/meshing/meshing_solid_map_unity_c.htm)，核对复杂实体必须分解为简单可映射块且仍需分阶段质量验证。

其中“中心核比例”等参数是 MCP 输出的可审计初始值，不是厂商固定规则；必须根据
实际几何尺寸、质量指标和网格收敛性调整。

## 8. 验证状态

当前实现已经通过：

- Skill 结构校验；
- HyperMesh MCP 专用测试；
- Ruff 静态检查；
- 仓库原有测试；
- 真实 stdio MCP 初始化、工具调用、资源读取和 Prompt 获取。

上述自动测试不启动商业 HyperMesh，因此不能代替本机 hmbatch smoke、
真实模型划分和求解器侧质量/收敛验证。
