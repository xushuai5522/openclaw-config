---
name: apple-notes
description: Manage Apple Notes via the `memo` CLI on macOS (create, view, edit, delete, search, move, and export notes).
---

# Apple Notes

## 快速参考
- **触发词**: 备忘录、笔记、Apple Notes
- **核心命令**: `memo create`, `memo list`, `memo search`
- **依赖**: memo CLI (macOS)

## 使用示例

### 创建笔记
```bash
memo create "会议记录" "今天讨论了项目进度，下周一交付第一版"
```

### 搜索笔记
```bash
memo search "项目"
```

### 列出所有笔记
```bash
memo list
memo list --folder "工作"
```

### 导出笔记
```bash
memo export "会议记录" --format markdown
```

## 使用场景
- 快速记录想法
- 会议记录
- 待办事项
- 知识收集
