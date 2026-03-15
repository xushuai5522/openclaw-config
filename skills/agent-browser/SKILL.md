---
name: agent-browser
description: 浏览器自动化与网页内容提取 - 无头浏览器控制、网页操作、页面复制/抓取，AI Agent专用。用于网页点击、输入、登录、截图、复制页面内容、提取 token/验证码/文本等场景。 
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

## 快速参考

- **触发词**: 浏览器自动化、网页操作、爬虫
- **核心功能**: 导航、点击、输入、截图、内容提取
- **依赖**: Playwright、Chrome/Chromium

---

## 使用示例

### 示例1: 登录网站
```bash
# 打开登录页
browser open --url "https://example.com/login"

# 输入用户名密码
browser type --selector "input[name='username']" --text "user@example.com"
browser type --selector "input[name='password']" --text "password123"

# 点击登录按钮
browser click --selector "button[type='submit']"

# 等待跳转
browser wait --selector ".dashboard"

# 截图确认
browser screenshot
```

### 示例2: 表单填写
```bash
# 填写多个字段
browser type --selector "#name" --text "张三"
browser type --selector "#phone" --text "13800138000"
browser type --selector "#email" --text "test@example.com"

# 选择下拉框
browser select --selector "#city" --value "苏州"

# 勾选复选框
browser check --selector "#agree"

# 提交表单
browser click --selector "#submit"
```

### 示例3: 内容抓取
```bash
# 获取页面结构
browser snapshot

# 提取特定内容
browser evaluate --script "document.querySelector('.price').textContent"

# 批量提取
browser evaluate --script "Array.from(document.querySelectorAll('.item')).map(el => el.textContent)"
```

---

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

## 页面复制/内容提取（已整合 web-copy）

适用场景：
- 复制 API Token / 验证码 / 页面隐藏文本
- 提取页面上的文案、价格、状态、按钮文本
- 点击复制按钮后读取剪贴板内容

推荐顺序：
1. 先 `snapshot` / `evaluate` 直接取 DOM 文本
2. 页面必须点“复制”按钮时，再定位按钮点击
3. 点击复制后，如需本机剪贴板内容，再配合系统剪贴板读取

原则：
- 能直接读页面文本，就不要多走复制按钮链路
- 复制链路主要用于 token、验证码、只暴露在剪贴板流程里的内容

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
