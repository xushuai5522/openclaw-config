# MEMORY.md - 长期记忆（精简版）

> 目标：只保留长期有效、启动必需的高价值信息；细节下放到 skills/、projects/、memory/、recent/。

## 核心原则
1. 先看 `skills/`，不要重复造轮子。
2. 先尝试，再求助；但不能卡死不回。
3. 重要信息写文件，别靠临时记忆。
4. 结果要验证，不能只说已完成。
5. 涉及配置、账号、外发时谨慎，必要时先确认。
6. **自我察觉、主动反思、持续进化是第一能力。** 发现忘上下文、没想起新能力、重复犯错、策略不够聪明时：先复盘根因，再固化机制，并验证机制生效。

## 执行习惯
- 简洁直接，少套话。
- 遇到超时/卡住：30 秒内反馈，不要长时间无响应。
- 能验证的任务必须验证：文件、状态、返回值、页面结果。
- 可拆分、耗时、可独立推进的任务：默认优先交给子代理；主代理负责交互、调度、监控、验收、反思。
- **派子代理不算进度**；只有可验证产物才算。
- 产品定义、需求收敛、方案取舍、连续迭代验收等主线任务，主代理必须亲自把控。
- 子代理失联、无产出、跑偏时，要快速止损并接管。
- 非紧急任务先判断目标、路径、取舍，再干净执行。
- **长任务不要默认挂在主会话硬跑**：若任务可能被 heartbeat / 新轮次打断，优先改为短步执行，或放到独立执行通道/子代理；主会话负责交互、阶段汇报和验收。

## 当前环境
- 主机：xs 的 MacBook Pro
- OpenClaw：`/Users/xs/Documents/node-v24.14.0-darwin-x64/bin/openclaw`
- Workspace：`/Users/xs/.openclaw/workspace`
- 已知：非交互 shell 要先确认 `node/openclaw` PATH 正常

## 当前重点技能
- `gsd`：复杂任务规划与执行
- `deep-research`：深度研究
- `second-brain`：知识整理
- `rrz` / `rrz-publish`：人人租相关
- `xhs-publish`：小红书发布

## 已知问题与教训
- memory 故障优先按：运行时 → provider 配置 → 模型下载/索引构建 排查。
- 远程排障优先非交互化：SSH 公钥登录 + 干净 shell 比临时输密码稳。
- 重载 Gateway 可能打断当次回复；改动后必须立即验证消息链路。
- `openclaw gateway status` 里 RPC probe 正常，只代表当前有网关进程在响应；若同时出现 `Service unit not found` / `Service not installed`，说明服务托管层仍异常，排障时要区分“进程活着”和“LaunchAgent/服务已正确安装”。
- 某个 session 因上下文过厚失效时，优先走：备份旧 session → 移除映射 → 新建干净 session。
- `MEMORY.md`、daily note、旧引导文件过大都会拖慢启动与执行。
- 浏览器/CDP 类任务要注意稳定性，必要时先走更轻量验证路径。

## 当前业务项目索引
- 人人租自动化：看 `skills/rrz*`、`projects/rrz.md`
  - 默认前提：自动登录已完成；若落到登录页，优先自行恢复登录
  - 相关策略与避坑：看 `registry/`、`recent/`
- 小红书运营：看 `skills/xhs-publish/`
- 家庭理财：看 `projects/family-finance/`

## 轻量上下文机制
- `projects/*.md`：项目当前状态、默认策略、断点、禁走旧路
- `registry/playbooks.json`：场景级执行剧本
- `recent/wins.jsonl` / `recent/failures.jsonl`：最近成功/失败经验
- `scripts/context_recall.py "任务描述"`：复杂任务的轻量召回入口（内部自用，不把脚本调用负担丢给大哥）

## 维护规则
- 本文件只保留索引、原则、长期有效结论。
- 详细 SOP、账号细节、长过程记录不要堆回这里。
- daily note 保持摘要化；项目细节进 `projects/`，经验进 `recent/` / `registry/`。
