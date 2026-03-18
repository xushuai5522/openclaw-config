# MEMORY.md - 长期记忆（精简版）

> 职责：只保留长期有效结论与索引，不记录一次性过程。

> 只保留长期有效、启动必需的信息；细节下放到 `skills/`、`projects/`、`memory/`、`recent/`。

## 核心原则
1. 先查 `skills/`，不要重复造轮子。
2. 先尝试再求助，但不能卡死不回。
3. 任务必须可验证，拒绝“口头完成”。
4. 涉及配置/账号/外发，先确认再执行。
5. 发现重复错误要复盘并固化机制。

## 执行习惯
- 简洁直接，超时/卡住 30 秒内反馈。
- 可拆分耗时任务走独立通道，主代理负责调度与验收。
- 子代理失联/跑偏/无产出，立即止损接管。

## 环境索引
- OpenClaw：`/Users/xs/Documents/node-v24.14.0-darwin-x64/bin/openclaw`
- Workspace：`/Users/xs/.openclaw/workspace`
- 注意：非交互 shell 先确认 `node/openclaw` PATH

## 重点技能
- `gsd`、`deep-research`、`second-brain`
- `rrz` / `rrz-publish`
- `xhs-publish`

## 关键教训
- memory 故障排查：运行时 → provider 配置 → 模型/索引。
- 远程排障优先非交互化（SSH 公钥 + 干净 shell）。
- 重载 Gateway 后必须立即验证消息链路。
- RPC probe 正常不等于服务托管层正常。
- session 过胖失效：备份旧会话 → 移除映射 → 新建干净会话。
- `MEMORY.md` / daily note / 旧引导文件过大都会拖慢执行。

## 项目索引
- 人人租：`skills/rrz*`、`projects/rrz.md`
- 小红书：`skills/xhs-publish/`
- 家庭理财：`projects/family-finance/`

## 轻量召回
- `projects/*.md`、`registry/playbooks.json`
- `recent/wins.jsonl`、`recent/failures.jsonl`
- `scripts/context_recall.py "任务描述"`（内部使用）
