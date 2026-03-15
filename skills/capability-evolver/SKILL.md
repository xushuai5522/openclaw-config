---
name: capability-evolver
description: |
  自我进化技能。从多个信号源识别改进点，持续优化能力和知识库。
  合并了原 self-improvement、error-learning、daily-review 的功能。
  触发场景：
  1. Heartbeat 定期触发（每3天自动执行一次完整进化分析）
  2. 大哥说"进化分析"、"自我检查"、"evolver"
  3. 连续工具调用失败后主动反思
  4. 每日结束时归纳当天记忆（23:30 cron）
  不适用：实时对话中的错误修正（直接改就行）。
---

# Capability Evolver — 自我进化

## 信号源（从哪里发现改进点）

| 信号源 | 检查方式 | 频率 |
|--------|---------|------|
| 日常对话记忆 | `memory/YYYY-MM-DD.md` 近 7 天 | 每次进化 |
| 大哥的纠正 | memory_search "不对/应该/错了/改" | 每次进化 |
| 工具调用失败 | memory_search "error/failed/超时" | 每次进化 |
| 服务运行状态 | `scripts/daily_healthcheck.sh` 日志 | 每次进化 |
| cron 执行状态 | `openclaw cron list` 检查 lastError | 每次进化 |
| Bug 分析教训 | `memory/bug-analysis-docs.md` 新增条目 | 每次进化 |
| 代码学习进展 | `memory/mcu-architecture.md` 学习状态 | 每周 |

## 进化流程

### Phase 1: 采集（Collect）
1. 读取近 7 天 `memory/YYYY-MM-DD.md`
2. 检查 `memory/evolver-log.md` 上次进化时间
3. memory_search 搜索错误/纠正信号
4. 检查 cron 状态和服务健康

### Phase 2: 分析（Analyze）
从采集数据中识别以下模式：

| 模式 | 示例 | 改进方向 |
|------|------|---------|
| 🔧 工具踩坑 | API 参数错误、飞书格式问题 | 更新 TOOLS.md |
| 🎯 判断错误 | 大哥纠正方向/结论 | 更新 MEMORY.md 工作习惯 |
| 🔁 重复劳动 | 相同模板/流程重复 3+ 次 | 创建脚本或 skill |
| 📚 知识盲区 | 被大哥告知新信息 | 更新相关知识文档 |
| ⏱️ 效率瓶颈 | 子代理超时、多次重试 | 优化流程 |
| 🏥 服务故障 | 服务挂过、cron 失败 | 加固或迁移 |

### Phase 3: 执行（Apply）
每次进化最多 5 个改进：

| 发现类型 | 写入目标 | 需要告知大哥 |
|---------|---------|-------------|
| API/工具踩坑 | TOOLS.md | ❌ |
| 工作流改进 | MEMORY.md | ❌ |
| 新知识/教训 | memory/ 相关文件 | ❌ |
| 性格/风格调整 | SOUL.md | ✅ 必须告知 |
| 新 skill 建议 | 只提议不自动创建 | ✅ 需审批 |
| 服务加固建议 | 只记录不自动执行 | ✅ 需审批 |

### Phase 4: 记录（Log）
写入 `memory/evolver-log.md`：

```markdown
## YYYY-MM-DD 进化记录

### 🔍 发现（X 个）
- [类型] 描述

### 🛠 行动（X 个）
- 更新了 XXX.md：具体改了什么

### 📊 统计
- 上次进化: YYYY-MM-DD
- 累计进化次数: N
```

## 每日记忆归纳（Daily Review 功能）

每天 23:30 或大哥说"总结今天"时：
1. 回顾当天对话（memory_search 当天日期）
2. 提取：关键决策、新学到的知识、待办事项
3. 写入 `memory/YYYY-MM-DD.md`
4. 如有重要发现，同步更新 MEMORY.md

## 安全规则

1. 只改 workspace 内文件
2. 修改 SOUL.md 必须告知大哥
3. 每次最多 5 个改进
4. 记录变更前内容，支持回滚
5. 不自动创建新 cron 或 skill（只提议）
