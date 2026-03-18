# TOOLS.md - 环境速查

> 职责：只放环境入口与速查索引；详细步骤放 skill/project；敏感信息不入常驻上下文。

> 仅放低风险索引与入口；详细步骤放 skill/project；敏感信息放本地私密清单（不进常驻上下文）。

## 鼠标控制
- 原生：`/Users/xs/bin/mouse_click`（`mouse_click x y`）
- 备选：`/usr/local/Homebrew/bin/cliclick`

## 电商主图
- Skill：`/Users/xs/.openclaw/workspace/skills/image-generator/SKILL.md`
- 模板/参数/API：见 skill 文档

## NAS（飞牛）
- 管理地址：`http://192.168.1.80:5666/`
- SMB 入口：`smb://192.168.1.80`
- 待确认：共享名（Finder 首挂或 SSH 查配置）

## OpenClaw 路径
- OpenClaw：`/Users/xs/Documents/node-v24.14.0-darwin-x64/bin/openclaw`
- Node：`/Users/xs/Documents/node-v24.14.0-darwin-x64/bin/node`
- 非交互 shell 预检：`which node && which openclaw`

## 上下文瘦身原则
- 停用过时 `BOOTSTRAP.md`
- `MEMORY.md` 仅存长期索引
- `AGENTS.md` 仅存高价值规则
