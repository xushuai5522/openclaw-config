# AGENTS.md - Workspace Rules

> 职责：只定义“怎么执行”（启动、规则、安全、验收）。不放人格、不放细节 SOP。

## Session startup
1. Read `SOUL.md`
2. Read `USER.md`
3. In main/private chat, read `MEMORY.md`
4. Read daily note: `memory/YYYY-MM-DD.md` (today; fallback yesterday)
5. Check `skills/` before creating new workflows
6. For ongoing work, check `projects/*.md`
7. For automation/browser/long tasks, recall `registry/` + `recent/`

## Execution rules
- Action first,少废话；能做就直接做
- 不把内部脚本执行转嫁给用户
- 可能卡住/超时时，30 秒内反馈
- 结果必须可验证（文件/状态/返回值/页面）
- 先想清路径，再执行，避免反复试错

## Long-task rules
- 长任务默认走独立执行通道（sub-agent/background/session）
- 主代理负责：目标定义、检查点、跟进、验收、必要时接管
- **派任务不算进度**；只有可验证产物才算
- 决策型/连续收敛型工作由主代理主导
- 子代理无产出或跑偏时，立即止损并接管

## Memory rules
- 重要信息写文件，不靠临时记忆
- 日志进 `memory/`，长期结论进 `MEMORY.md`
- **任务收尾双写（强制）**：每次任务结束先写 `memory/YYYY-MM-DD.md`；有可复用结论再同步到 `MEMORY.md`
- 保持上下文精简，详细 SOP 放 skills/projects

## Safety rules
- 不泄露隐私
- 破坏性或对外动作先确认
- 优先可回滚方案
- 风险配置变更：backup → change → verify

## Heartbeat
- 仅做保活/健康检查，轻量、限时
- 被阻塞就直接报阻塞，不深挖
- 不在 heartbeat 中跑长任务
