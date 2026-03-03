---
name: n8n-workflow-automation
description: n8n工作流自动化 -设计和输出n8n工作流JSON文件
metadata: {
  "openclaw": {
    "emoji": "🔄",
    "os": ["darwin", "linux"],

## 快速参考
- **触发词**: n8n、工作流自动化
- **核心功能**: 设计和输出n8n工作流JSON
- **适用场景**: 自动化业务流程

---

    "requires": {
      "bins": [],
      "env": []
    }
  }
}
---

# n8n Workflow Automation - n8n工作流自动化

## 技能说明

这个技能可以帮助设计和生成 n8n 工作流 JSON 文件，适合简单的自动化工作流场景。

## 使用场景

1. **大哥需要自动化**：大哥说"帮我做个工作流"
2. **简单重复任务**：需要定时执行的任务
3. **API 集成**：需要连接多个服务的场景

## 执行步骤

### 第一步：理解需求

1. 明确工作流目标
2. 了解输入输出
3. 确定触发条件（定时/webhook/手动）

### 第二步：设计工作流

1. 确定需要的 n8n 节点
2. 设计数据流向
3. 考虑错误处理

### 第三步：生成 JSON

生成符合 n8n 格式的 JSON 文件：
```json
{
  "name": "工作流名称",
  "nodes": [...],
  "connections": {...},
  "settings": {...},
  "staticData": null,
  "tags": [],
  "triggerCount": 1,
  "updatedAt": "...",
  "createdAt": "...",
  "id": "..."
}
```

### 第四步：输出结果

1. 保存 JSON 文件到 workspace
2. 告诉大哥文件位置
3. 提醒大哥导入 n8n 的方法

## n8n 常用节点参考

| 节点 | 功能 |
|------|------|
| Schedule Trigger | 定时触发 |
| Webhook | HTTP 触发 |
| HTTP Request | HTTP 请求 |
| Slack | Slack 消息 |
| Gmail | 邮件 |
| Google Sheets | 表格 |
| IF / Switch | 条件分支 |
| Set | 设置变量 |
| Function | 自定义代码 |

## 注意事项

- 复杂工作流可能生成不准确
- 需要大哥手动调整
- 导出后让大哥在 n8n 中测试
- 某些节点需要配置凭据

## 成功标准

- 生成有效的 n8n JSON
- 简单工作流可直接使用
- 大哥可以导入 n8n
