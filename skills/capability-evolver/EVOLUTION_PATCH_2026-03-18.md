# Capability Evolver 进化补丁（2026-03-18）

## 本次运行摘要
- 执行命令：`EVOLVE_LOAD_MAX=10 node index.js run`
- 运行结果：成功完成
- 扫描范围：近 7 天 memory 文件，共 7 个
- 命中文件：5 个
- 生成建议：2 条
- 高优问题：1 个

## 从运行日志识别出的核心模式

### 1. 超时/中断是当前最突出的稳定性问题
近期日志聚合结果：
- `2026-03-16.md`：timeout 12 次
- `2026-03-17.md`：timeout 2 次
- 近 7 天累计 timeout / 中断 15 次

结合 daily note，根因已较清楚：
- 长任务使用 `exec(background=true)` 时，仍会被 `timeout` 杀掉；
- 过去容易把 `SIGTERM` 误判为 heartbeat / cron 抢断；
- 说明当前 evolver 只会“统计超时”，但还不会把“超时误判 → 根因模式 → 固化策略”提炼成结构化经验。

### 2. 工具失败计数偏粗，容易把“已知旧问题”反复报新警
近期日志聚合结果：
- 近 7 天工具失败累计 9 次
- 主要集中于旧历史文件，而不是当天新增爆发

当前问题：
- evolver 只做简单关键词计数；
- 没有区分“新出现问题”与“历史遗留重复记录”；
- 没有把同一根因（如 timeout / ref 失效 / 权限）做归并；
- 导致日志会重复输出大而泛的建议，信噪比一般。

### 3. 输出停留在“建议”，缺少“补丁动作层”
当前引擎能输出：
- 发现
- 建议

但还缺：
- 对应改哪个文件
- 建议加入哪条 durable memory
- 哪些属于立即执行，哪些仅观察
- 同一天重复运行时的去重与增量比较

也就是说，它更像“异常扫描器”，还不像真正的“进化补丁生成器”。

---

## 建议补丁（不自动应用，供后续实施）

### Patch A — 新增“根因归并”层（高优）
**目标**：把 `timeout / SIGTERM / killed / timed out` 归到统一的“执行通道超时”根因，而不是只做表面计数。

**建议实现**：
1. 在 `analyzeErrors()` 之后增加 `classifyRootCauses()`；
2. 新增根因类别：
   - `executionTimeout`
   - `permissionGap`
   - `locatorFragility`
   - `networkInstability`
   - `manualMisjudgment`
3. 对 `SIGTERM + background + timeout` 这种组合，优先归因为 `executionTimeout`；
4. 建议输出从“超时出现15次”升级为：
   - `执行通道超时：15 次（主要集中在长任务后台 exec）`

**预期收益**：
- 建议更可执行；
- 避免把同一问题拆成多个表面标签重复报警。

### Patch B — 增加“增量检测”，避免重复报警（高优）
**目标**：区分“新增问题”与“历史重复问题”。

**建议实现**：
1. 读取 `memory/evolver-log.md` 最近一次记录；
2. 保存上次聚合计数快照；
3. 本次输出时增加：
   - `新增 timeout: +2`
   - `新增 toolFailure: +0`
4. 若某类问题无新增，仅标为“持续存在”，降低优先级。

**预期收益**：
- 每次进化更像趋势分析，而不是重复念旧账；
- 减少噪音，便于判断是否恶化。

### Patch C — 输出结构升级为“发现 → 根因 → 动作”三段式（高优）
**目标**：让 evolver 直接产出可执行补丁，而不是只有泛建议。

**建议实现**：
对每条建议增加字段：
- `rootCause`
- `actionType`
- `targetFile`
- `patchHint`
- `confidence`

**示例输出**：
```md
- [high/repair] 根因：executionTimeout
  - 现象：近7天 timeout/中断 15 次
  - 动作：更新 AGENTS.md / TOOLS.md 的长任务执行约束
  - 补丁提示：后台长任务默认 timeout >= 600s，优先分批执行并落盘
  - 置信度：high
```

**预期收益**：
- 直接生成“该改哪里”的结果；
- 更符合“进化补丁”定位。

### Patch D — 把 daily note 中的 durable lesson 自动提炼候选（中优）
**目标**：从记忆中提炼已确认根因，而不是只扫错误词。

**建议实现**：
1. 对以下标记做额外加权：
   - `教训：`
   - `经验：`
   - `根因：`
   - `已明确执行策略：`
   - `durable`
2. 若某条经验在 2 天内重复出现，则生成：
   - `建议写入 TOOLS.md / MEMORY.md`
3. 对本次场景，自动提炼：
   - `background=true 并不会绕过 timeout`
   - `遇到 SIGTERM 先查 exec timeout，再查 heartbeat/cron`

**预期收益**：
- 从“扫异常”升级到“固化经验”；
- 更接近真正的自我进化。

### Patch E — 同日重复运行去重（中优）
**目标**：避免同一天多次执行把 log 写得又长又重复。

**建议实现**：
1. 日志 key 改为 `date + strategy + fingerprint`；
2. 若同日、同策略、同 fingerprint，则：
   - 不重复写完整记录；
   - 只追加一条 `重复运行，无新增发现`；
3. 若发现数值变化，再生成新块。

**预期收益**：
- `memory/evolver-log.md` 更干净；
- 便于长期查看趋势。

---

## 建议固化到长期机制的两条经验

### 经验 1
`exec(background=true)` 不是免死金牌，仍受 `timeout` 约束；长任务要么给足 timeout，要么拆批并落盘。

**建议落点**：
- `TOOLS.md`（执行通道经验）
- 或 `MEMORY.md`（若提升为长期原则）

### 经验 2
看到 `SIGTERM / timeout` 时，先检查执行通道与 timeout 配置，不要先按时间线怀疑 heartbeat / cron。

**建议落点**：
- `TOOLS.md`
- `projects/openclaw-timeout-observability-plan.md` 已可作为专项文档承接

---

## 本次结论
本轮 evolver 成功运行，但暴露出一个明显短板：
**当前引擎已经能扫出异常，却还不够擅长把异常转成“去重后的根因 + 精确补丁动作”。**

一句话总结：
**能发现问题，但补丁生成能力还偏弱；下一步应该补“根因归并、增量检测、动作化输出”。**
