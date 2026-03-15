---
name: openclaw-doctor
description: Diagnose, repair, and validate OpenClaw runtime and host problems. Use when OpenClaw is "只说话不干活", tool calls fail, gateway/session behavior is abnormal, PATH/node/openclaw command resolution is broken, startup context is too heavy, skills are missing, heartbeat misbehaves, browser/CDP/network/process problems need diagnosis, or the user asks to check/fix/optimize an OpenClaw deployment or machine.
---

# OpenClaw Doctor

目标：先定位真故障，再做最小修复，最后做真实动作验收。

## 核心原则
- 先证据，后结论；不要凭感觉猜。
- 优先修**执行链**，不是只看“能回复”。
- 优先做**最小可回滚修复**。
- 修完必须做**真实动作测试**，不能只看 `openclaw status`。
- 发现旧上下文/历史残留拖慢系统时，优先瘦身而不是继续硬扛。

## 标准排障顺序

### 1. 先确认连接与命令链
按顺序检查：
1. SSH / 本机访问是否正常
2. `which node`
3. `which openclaw`
4. `node -v`
5. `openclaw status`

如果 `openclaw` 存在但执行时报：
- `env: node: No such file or directory`
- `command not found`

优先判断为：**PATH / 非交互 shell 环境问题**。

### 2. 查真实路径，不要假定 PATH 正常
若 PATH 可疑：
- 查 `command -v openclaw`
- 查 `which -a openclaw`
- 查 `ls -l` 真实软链接
- 必要时直接用绝对路径执行 `openclaw`

若是 Node 独立安装目录（例如 `/Users/.../node-*/bin`），优先：
- 把该目录加入 shell 配置
- 补 `~/.local/bin/node`
- 补 `~/.local/bin/openclaw`

### 2.5 目标机定位
若远端机器可能换 IP：
- 不要死盯旧 IP
- 优先通过 **ARP / 邻居表 + MAC** 定位当前 IP
- 重新定位后再做 SSH / 端口 / OpenClaw 检查

### 3. 看状态，但别停在状态页
必查：
- `openclaw status`
- 必要时 `openclaw status --deep`
- 最近日志：`~/.openclaw/logs/`

重点搜这些关键词：
- `TimeoutExpired`
- `timed out after`
- `command not found`
- `Approval required`
- `safeBins`
- `bootstrap`
- `heartbeat`
- `tool`
- `exec`

若 shell 环境脏、引号复杂、非交互输出异常：
- **不要继续单行 SSH 硬拼**
- 改走：**本地短脚本 -> 上传远端执行 -> 回收结果**

## 资源文件
- 需要快速复核排障顺序时，读 `references/checklist.md`
- 需要做远程最小动作验收时，运行 `scripts/remote_agent_smoke.sh <host> <key_path>`

## 已整合能力
- 已吸收原 `system-diagnosis` 的常见系统诊断职责：浏览器/CDP 端口、代理、网络、进程、日志、资源占用排查。
- 遇到浏览器连不上、CDP 异常、代理错配、系统服务异常时，默认直接按本技能处理，不再分流到旧 skill。

## 高概率故障模式

### A. 只说话不干活
常见根因：
1. `node/openclaw` 在非交互 shell 不可见
2. `BOOTSTRAP.md` 还在，污染每次启动上下文
3. `MEMORY.md` / `AGENTS.md` / 其他启动文件过大，导致会话启动和动作链变慢
4. 历史日志中已有超时证据，但一直没做上下文瘦身

#### 处理顺序
1. 修 PATH / 绝对路径
2. 停用旧 `BOOTSTRAP.md`
3. 精简 `MEMORY.md`
4. 必要时精简 `AGENTS.md`
5. 重新做真实动作测试

### B. 会话/心跳假死
优先检查：
- HEARTBEAT 是否过长、是否塞了重任务
- 是否存在会阻塞的命令放在前面
- 是否缺少“失败立即汇报”规则

修复原则：
- 心跳只保留轻任务
- 长任务转 cron / 子代理
- 预算尽量控制在约 30 秒内
- 明确：命令失败一次就汇报，不反复重试
- 遇到 `Approval required` / 权限拦截 / 命令不存在 / 超时：立即汇报阻塞

### C. 技能缺失 / 本地能力没同步
若目标机缺技能：
1. 查 `~/.openclaw/workspace/skills/`
2. 只同步缺的 skill
3. 同步后再次用真实任务触发验证

## 上下文瘦身规则

### 必须停用或处理
- 过时 `BOOTSTRAP.md`
- 已失效、超长、重复的长期记忆
- 把 SOP/账号细节/长流水硬塞进 `MEMORY.md`

### 推荐体积控制
- `MEMORY.md`：保留长期索引，尽量小
- `AGENTS.md`：只留高价值规则
- `HEARTBEAT.md`：短、小、只保留轻检查

### 瘦身后必须做
- 备份原文件
- 写明为什么改
- 重新做动作链测试

## 修复后验收模板
至少做 2 轮：

### 验收 1：单动作
- 让 OpenClaw 执行 `exec`
- 期望：返回真实命令结果

### 验收 2：动作链
按顺序要求它：
1. `write` 写文件
2. `exec` 读取文件
3. 最终只回复读取内容

通过标准：
- 文件真实存在
- 读取内容正确
- Agent 最终回复与文件一致

如果只回复“已完成”但没有落盘/没有结果，视为**未修好**。

## 收尾规则
修完后：
1. 把修复过程写进 `memory/YYYY-MM-DD.md`
2. 把环境坑写进 `TOOLS.md`
3. 清理测试文件
4. 若涉及配置清理 / 安全收口，分两步验收：
   - 先验安全基线（插件白名单、workspaceOnly、鉴权、安全项）
   - 再验业务能力（群聊、配对、文档、远程连接、工具调用）
5. 汇报：
   - 根因
   - 改了什么
   - 如何验证
   - 还剩什么风险

## 数据处理注意
- 临时配置快照、日志、备份 JSON 默认按敏感信息处理
- 对外汇报必须脱敏：token / key / secret / open_id / 内网地址

## 默认汇报格式
- **根因**：一句话说本质
- **已修复**：列动作
- **已验证**：列真实测试
- **剩余风险**：只说还没解决的
