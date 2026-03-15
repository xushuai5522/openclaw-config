# OpenClaw Doctor Checklist

## 快速检查
1. `which node`
2. `which openclaw`
3. `node -v`
4. `openclaw status`
5. `openclaw status --deep`（必要时）
6. `ls ~/.openclaw/logs`
7. grep 日志关键词：
   - `TimeoutExpired`
   - `timed out after`
   - `command not found`
   - `Approval required`
   - `safeBins`
   - `bootstrap`
   - `heartbeat`
   - `tool`
   - `exec`

## 高优先级根因
- 非交互 shell PATH 缺失
- 旧 `BOOTSTRAP.md` 残留
- `MEMORY.md` / `AGENTS.md` 过肥
- 缺 skill
- 心跳里塞了重任务
- 固定 IP 失效，实际目标机已换 IP
- 配置清理后只验了安全，没单独验业务能力是否还活着

## 远端连接补充
- 不要默认相信旧 IP
- 已知目标机若存在 DHCP 变化，优先：**ARP + MAC / 邻居表定位当前 IP**
- 若固定 IP 连不上，但 ARP 命中设备，先重新确认当前 IP，再 SSH

## 取证方式补充
- 遇到多层引号、脏 shell、非交互回显异常：
  - **不要继续单行 SSH 硬拼**
  - 改走：**本地短脚本 -> 上传远端执行 -> 回收结果**
- 适合抓：日志、索引文件、配置片段、脚本内容、批量命令输出

## 配置与安全补充
- 临时配置快照（如 `tmp/openclaw*.json`）默认按敏感文件处理
- 对外汇报时必须脱敏：token / key / secret / open_id / 内网地址
- 做安全收口后，分两步验收：
  1. **安全基线**：插件白名单、workspaceOnly、鉴权、安全项
  2. **业务能力**：群聊/配对/文档/远程连接/工具调用是否还正常

## 心跳修复补充
- 心跳总预算控制在约 30 秒内
- 命令失败一次就汇报，不要反复重试
- 遇到 `Approval required` / 权限 / 超时 / 命令不存在：立即汇报阻塞
- 长任务转 cron / 子代理

## 修后必验
- 单动作：exec
- 连续动作：write -> exec -> 回复结果
- 文件真实存在
- 输出与文件内容一致
