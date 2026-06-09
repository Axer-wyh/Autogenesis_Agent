# Autogenesis Agent 产品规划文档

日期：2026-06-09

## 1. 产品定位

Autogenesis Agent 是一款面向开发者和企业团队的“受控自演化 Agent Runtime”。它不是单纯的聊天机器人，而是一个能执行任务、记录轨迹、提出自我改进方案，并在评估通过后安全更新自身资源的 Agent 平台。

核心定位：

- 借鉴 Hermes 的统一 Agent 执行核心：CLI、Gateway、Cron、API 复用同一套运行时。
- 借鉴 OpenClaw 的本地优先控制面：多入口接入、会话隔离、队列、中断、事件流、沙箱。
- 基于 Autogenesis 协议补齐演化治理：RSPL 管可演化资源，SEPL 管反思、改进、评估、提交和回滚。

第一版产品不追求“Agent 自动改所有代码”，而是聚焦可审计、可评估、可回滚的受控演化。

## 2. 目标用户与使用场景

### 2.1 目标用户

- AI 应用开发者：需要构建稳定、可调优的工具调用 Agent。
- 企业内部自动化团队：需要 Agent 有持续改进能力，但必须可审计、可回滚。
- Agent 研究/评测团队：需要采集执行轨迹、做 prompt/skill/memory 策略实验。

### 2.2 首批场景

- 编程 Agent：优化仓库阅读策略、工具选择、错误恢复流程。
- 研究 Agent：优化搜索、引用检查、摘要流程。
- 企业知识助手：优化检索提示词、FAQ 处理策略、记忆沉淀策略。

## 3. 核心产品假设

1. 企业和专业用户更需要“可控变好”，而不是“不可控自治”。
2. Agent 最早可安全演化的对象是 Prompt、Skill、Memory Policy 和 Tool Routing，不是核心代码。
3. 自演化能力必须绑定评估集、版本血缘、审计日志和回滚机制，否则无法进入生产。
4. Gateway、Session、Runtime、Resource、Evolution 必须分层，否则系统会快速变成不可维护的单体。

## 4. 产品功能架构

Canva 主架构图：

- 编辑链接：[Autogenesis Agent 精确产品功能架构图](https://www.canva.com/d/UlzjPCxsZDXQ0cS)
- 查看链接：[架构图预览](https://www.canva.com/d/Ewh8B_ljCO6LiGS)

本地精确版图片：

- [autogenesis_agent_architecture.png](/Users/zappa/Documents/Autogenesis_Agent/docs/product/autogenesis_agent_architecture.png)

Canva 备选竖版图：

- 编辑链接：[信息图表 - 用户入口](https://www.canva.com/d/1hDb5vh_tiGd9O2)
- 查看链接：[备选图预览](https://www.canva.com/d/_XtZ-aVUskRbJ1B)

说明：Canva AI 自动生成的横向图出现过术语泛化和中文乱码问题，因此最终采用“本地精确绘制 -> Canva 转可编辑设计”的方式，确保架构图文字与规划文档一致。

### 4.1 分层结构

```text
用户入口层
  CLI / Web 控制台 / API / IM Gateway

控制面
  Gateway / Auth / Session Router / Queue / Interrupt / Event Stream

Agent 执行核心
  Prompt Builder / Model Router / Runtime Loop / Tool Dispatcher / Context Compressor

RSPL 资源层
  Resource Registry / Version Manager / Prompts / Skills / Tools / Environments / Memory / Agent Config

SEPL 自演化层
  Reflect / Select / Improve / Evaluate / Commit / Rollback

数据与治理层
  Trace Store / Eval Suite / Audit Log / Sandbox / Policy Guard / Secret Redaction / Human Approval
```

## 5. 主要模块设计

### 5.1 Gateway 与入口层

职责：

- 统一接入 CLI、Web 控制台、API、IM 平台。
- 做用户鉴权、设备/渠道配对、请求限流。
- 将输入路由到正确的 agent、workspace 和 session。
- 提供流式事件：任务开始、模型输出、工具调用、评估结果、演化提交。

MVP 阶段只实现 CLI + 本地 API。IM Gateway 和 Web 控制台放到第二阶段。

### 5.2 Session Manager

职责：

- 每个 session 拥有独立 history、workspace、memory scope 和 execution lane。
- 同一 session 内任务串行执行，避免工具调用和 transcript 写入冲突。
- 支持 interrupt、follow-up、queue、retry。
- 支持 session lineage：压缩、分叉、演化前后对比。

关键规则：

- 同一 session 同时只能有一个活跃执行循环。
- 工具调用结果必须和触发它的 assistant message 保持顺序关系。
- 历史压缩不能拆散 tool call 与 tool result。

### 5.3 Agent Runtime

职责：

- 从 session、resource registry、memory、context files 组装 prompt。
- 解析模型返回，调度工具，处理重试、fallback、压缩和中断。
- 将执行结果写入 transcript、trace store、memory。

核心执行流：

```text
receive_task
→ authorize
→ resolve_session
→ load_resources
→ build_prompt
→ call_model
→ dispatch_tools
→ persist_trace
→ return_response
```

### 5.4 Tool Runtime

职责：

- 工具注册、schema 暴露、权限声明和执行。
- 对危险工具做审批和沙箱隔离。
- 对输出做长度控制、敏感信息过滤、结构化归档。
- 支持 MCP 工具接入，但 MCP 只作为工具连接层，不承载自演化治理。

工具分级：

| 等级 | 示例 | 默认策略 |
|---|---|---|
| L0 只读 | read file, search, web extract | 允许 |
| L1 低风险写入 | write memory, create note | 记录审计 |
| L2 工作区修改 | edit file, run shell | 用户审批或策略审批 |
| L3 外部副作用 | send message, deploy, payment | 默认禁止 |
| L4 核心自修改 | 修改 runtime/core code | MVP 禁止 |

### 5.5 RSPL Resource Registry

职责：

- 把可演化对象注册为资源，而不是散落在代码里。
- 为每个资源维护状态、版本、血缘、diff、owner、权限和评估记录。

资源类型：

- Prompt：system prompt、任务 prompt、few-shot 示例。
- Skill：可复用流程、操作手册、脚本、模板。
- Tool：工具 schema、权限、实现引用、启用策略。
- Environment：workspace、sandbox、browser、filesystem。
- Memory：用户记忆、任务记忆、工具轨迹记忆、策略记忆。
- Agent Config：模型、temperature、工具集、上下文策略。

资源基础字段：

```text
id
type
name
description
version
owner
trainable
input_schema
output_schema
safety_policy
created_at
updated_at
lineage_parent_id
```

### 5.6 SEPL Evolution Engine

职责：

- 从执行轨迹和反馈中识别失败。
- 选择要修改的资源。
- 生成候选改进。
- 通过评估集和安全规则判断是否提交。
- 记录版本血缘并支持回滚。

演化闭环：

```text
Reflect
→ Select
→ Improve
→ Evaluate
→ Commit or Rollback
```

MVP 可演化范围：

- 允许：Prompt、Skill、Memory Policy、Tool Routing Policy。
- 只读观察：Tool implementation、Environment implementation。
- 禁止：核心 runtime 代码、鉴权逻辑、审计逻辑、安全策略本身。

### 5.7 Evaluator

职责：

- 每个候选变更必须经过评估。
- 评估结果必须可复现、可比较、可审计。

评估维度：

- 任务成功率：是否完成目标。
- 回归测试：旧任务是否退化。
- 安全不变式：是否绕过权限、泄露敏感信息、扩大工具权限。
- 成本指标：token、调用次数、耗时。
- 用户体验：是否更清晰、更少打扰、更少幻觉。

提交规则：

- 性能提升且无安全违规：可自动提交到 staging。
- 轻微提升但涉及行为边界：需要人工审批。
- 安全违规或回归失败：丢弃候选并记录原因。

## 6. 数据模型草案

### 6.1 主要表

- `sessions`：会话、渠道、用户、workspace、状态。
- `messages`：OpenAI-compatible message history。
- `resources`：RSPL 资源元数据。
- `resource_versions`：版本内容、diff、父版本。
- `traces`：任务执行轨迹。
- `tool_calls`：工具调用参数、结果、耗时、错误。
- `evolution_runs`：SEPL 每次演化过程。
- `eval_results`：候选版本的评估结果。
- `approvals`：人工审批记录。
- `audit_logs`：安全、治理、版本操作日志。

### 6.2 存储选择

MVP：

- SQLite：session、resource、trace、eval、audit。
- 本地文件：workspace、skill、prompt 文件。
- FTS5：session search、trace search。

第二阶段：

- Postgres：多用户、多环境。
- Object Store：大文件、截图、日志归档。
- Vector DB：长期记忆和语义检索。

## 7. MVP 范围

### 7.0 功能优先级

| 优先级 | 功能 | 目的 |
|---|---|---|
| P0 | Agent Runtime Loop | 保证任务能稳定执行 |
| P0 | Session Manager | 保证会话一致性和可恢复 |
| P0 | Tool Runtime | 保证工具调用可控 |
| P0 | Trace Store | 为调试和演化提供数据 |
| P0 | Resource Registry | 把 prompt、skill、memory policy 版本化 |
| P1 | Reflection Optimizer | 从失败轨迹生成改进提案 |
| P1 | Evaluator | 防止改进候选引入退化 |
| P1 | Commit/Rollback | 支撑安全发布和回滚 |
| P2 | Web 控制台 | 展示会话、资源版本、演化记录 |
| P2 | MCP 接入 | 扩展工具生态 |
| P3 | 多 IM Gateway | 扩展使用入口 |

### 7.1 必做能力

- CLI 入口。
- 本地 API。
- 单 agent runtime loop。
- 基础 Tool Runtime：文件读取、搜索、shell、patch、memory、skill。
- Resource Registry。
- Prompt/Skill/Memory Policy 版本管理。
- Trace Store。
- Reflection Optimizer。
- 固定评估集。
- Commit/Rollback。
- 审计日志。

### 7.2 暂不做

- 多 IM 渠道。
- Web 控制台完整 CRUD。
- 自动改核心代码。
- 自动部署。
- 复杂多 agent bus。
- 强化学习优化器。
- 企业 SSO。

## 8. 里程碑

### Phase 0：设计与验证

- 完成产品规划、架构图、数据模型、MVP 任务拆分。
- 建立 20-50 条评估任务样例。
- 明确资源可变更边界和审批矩阵。

### Phase 1：MVP Runtime

- 实现 CLI、本地 API、Agent Runtime、Tool Runtime。
- 实现 SQLite session 和 trace。
- 实现 prompt/skill registry。

### Phase 2：受控自演化

- 实现 Reflect/Select/Improve/Evaluate/Commit/Rollback。
- 支持 prompt 和 skill 候选变更。
- 支持评估集、回归测试、审计日志。

### Phase 3：产品化

- Web 控制台。
- 演化记录看板。
- 人工审批流。
- 多 provider model router。
- MCP 工具接入。

### Phase 4：扩展

- 多 agent 协作。
- 记忆系统增强。
- 复杂优化器。
- 企业部署和权限体系。

## 9. 成功指标

- 任务成功率提升：同一评估集上，演化后成功率提升。
- 回归率：已通过任务不能明显退化。
- 安全违规率：高风险工具和敏感信息违规为 0。
- 平均恢复时间：失败后能生成可执行改进建议。
- 回滚成功率：任意资源版本可回滚。
- 用户审批负担：低风险变更自动处理，高风险变更才请求审批。

## 10. 风险与控制

| 风险 | 影响 | 控制策略 |
|---|---|---|
| Agent 自我修改失控 | 破坏核心系统 | MVP 禁止核心代码自修改 |
| Prompt 变更引入退化 | 任务成功率下降 | 固定评估集 + 回归测试 |
| 工具权限扩大 | 安全事故 | Tool Policy + Approval Matrix |
| Trace 泄露敏感信息 | 合规风险 | Secret Redaction + Audit |
| 长期记忆污染 | 输出质量下降 | Memory feedback + 版本化 memory policy |
| 评估集过窄 | 虚假提升 | 按场景维护测试集和负样本 |
| 单体化 | 后期难维护 | Gateway / Runtime / RSPL / SEPL 分层 |

## 11. 资深全栈工程师审阅记录

审阅角色：资深全栈工程师，关注生产可落地性、模块边界、安全、数据一致性和 MVP 收敛。

### 11.1 发现的问题

1. 初始规划容易把“自演化”描述成单一算法能力，缺少资源变更边界。
2. 需要明确哪些资源能自动变更，哪些只能观察，哪些禁止变更。
3. Gateway 和 Session Manager 必须在早期设计，否则后续接 IM、Web、Cron 会重写核心。
4. 评估器不能只看成功率，还必须覆盖回归、安全、成本和用户体验。
5. Tool 权限需要分级，否则 shell、deploy、send message 这类工具会成为高风险入口。
6. 需要独立审计日志，不能只依赖普通运行日志。
7. MVP 应该收敛到 CLI + 本地 API，避免过早做多渠道和完整控制台。

### 11.2 已补充修改

- 增加了 Tool L0-L4 权限分级。
- 增加了 RSPL 资源基础字段。
- 增加了 SEPL 可演化范围：允许、只读观察、禁止。
- 增加了 Evaluator 提交规则。
- 增加了数据表草案。
- 增加了 P0-P3 功能优先级。
- 增加了 Phase 0，用于先做评估集和审批矩阵。
- 增加了风险控制表。
- 将 Canva 主图改为本地精确绘制后转换到 Canva 的版本，避免 AI 生成图文字不准确。

### 11.3 仍需后续细化

- 每类资源的 diff 格式。
- Prompt/Skill 评估集样例。
- Approval Matrix 的具体策略表达。
- Sandbox 后端选择：local、Docker、SSH、云沙箱。
- Web 控制台的信息架构。

### 11.4 架构图审阅结论

审阅发现：

- 第一版 Canva AI 横向图保留了大体层级，但出现“DPL 核心架构”等非规划术语。
- 严格提示后的 Canva AI 图出现中文乱码，不适合作为正式架构图。
- 最终版本改用确定性绘制，确保层级、标签、箭头和 MVP 边界准确。

最终采用：

- 本地精确图：[autogenesis_agent_architecture.png](/Users/zappa/Documents/Autogenesis_Agent/docs/product/autogenesis_agent_architecture.png)
- Canva 可编辑图：[Autogenesis Agent 精确产品功能架构图](https://www.canva.com/d/UlzjPCxsZDXQ0cS)

## 12. 建议的下一步

1. 先冻结 MVP 范围：CLI + 本地 API + Prompt/Skill/Memory Policy 演化。
2. 写实现计划：模块、目录结构、数据表、测试策略。
3. 建立第一批评估任务。
4. 开始实现 Resource Registry、Trace Store、Agent Runtime。
5. 第二轮再加入 SEPL 演化闭环。
