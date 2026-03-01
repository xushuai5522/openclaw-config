---
name: agent-browser
description: 浏览器自动化 - 无头浏览器控制，AI Agent专用
metadata: {
  "openclaw": {
    "emoji": "🌐",
    "os": ["darwin", "linux"],
    "requires": {
      "bins": ["chromium", "playwright"],
      "env": []
    }
  }
}
---

# Agent Browser - 浏览器自动化

## 技能说明

快速的无头浏览器自动化CLI，支持AI Agent通过结构化命令导航、点击、输入和截图。

## 使用场景

1. **网页操作**：需要操作网页（登录、填表、点击）
2. **内容抓取**：需要获取动态网页内容
3. **自动化测试**：需要自动化测试网页功能
4. **截图**：需要捕获网页状态

## 执行步骤

### 第一步：检查环境

确保有可用的浏览器：
- 本地 Chrome/Safari
- Playwright 浏览器
- CDP 连接

### 第二步：分析目标页面

1. 理解页面结构
2. 识别关键元素（按钮、输入框、链接）
3. 制定操作序列

### 第三步：执行操作

常用操作：
| 操作 | 命令 |
|------|------|
| 打开页面 | navigate to URL |
| 点击元素 | click selector |
| 输入文字 | type selector text |
| 截图 | screenshot |
| 获取内容 | snapshot |

### 第四步：处理结果

1. 验证操作成功
2. 获取返回内容
3. 处理异常情况

## 常用命令参考

```
# 导航
navigate https://example.com

# 点击
click .button-class
click #submit-btn
click text=登录

# 输入
type input[name="email"] test@example.com
type #password secret

# 等待
wait for .loading to disappear
wait 2s

# 截图
screenshot
screenshot fullPage=true

# 获取内容
snapshot
```

## 注意事项

- 处理反爬网站要谨慎
- 注意登录状态保持
- 处理弹窗和iframe
- 设置合适的超时

## 成功标准

- 能正常操作常见网页
- 异常处理完善
- 截图清晰
- 大哥满意
