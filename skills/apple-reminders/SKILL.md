---
name: apple-reminders
description: Manage Apple Reminders via the `remindctl` CLI on macOS.
---

# Apple Reminders

## 快速参考
- **触发词**: 提醒事项、待办、Reminders
- **核心命令**: `remindctl add`, `remindctl list`, `remindctl complete`
- **依赖**: remindctl CLI (macOS)

## 使用示例

### 添加提醒
```bash
# 简单提醒
remindctl add "买菜"

# 指定列表
remindctl add "买菜" --list "购物清单"

# 带截止日期
remindctl add "提交报告" --due "2026-03-05"

# 带优先级
remindctl add "重要会议" --priority high
```

### 列出提醒
```bash
# 今天的提醒
remindctl list --today

# 所有未完成
remindctl list --incomplete

# 特定列表
remindctl list --list "工作"
```

### 完成提醒
```bash
remindctl complete "买菜"
```

## 使用场景
- 日常待办管理
- 购物清单
- 工作任务跟踪
- 定期提醒
