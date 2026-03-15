# 技能：浏览器复制功能

当需要在网页上复制某个内容（如API Token、验证码等）时使用。

## 场景
- 复制API Key
- 复制验证码

## 快速参考
- **触发词**: 网页复制、内容提取
- **核心功能**: 提取网页内容
- **适用场景**: 内容采集、数据抓取

---

- 复制任何网页上隐藏的内容

## 方法

### 方法1：查找复制按钮
找到页面中所有按钮，点击有复制图标（SVG）的按钮：
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:18800')
    
    for page in browser.contexts[0].pages:
        # 查找所有按钮
        buttons = page.query_selector_all('button')
        
        for btn in buttons:
            # 检查是否有SVG图标（通常是复制按钮）
            if btn.query_selector('svg'):
                btn.click()
                break
    
    browser.close()
```

### 方法2：点击指定位置的按钮
通过索引点击按钮（如第3个按钮）：
```python
buttons = page.query_selector_all('button')
if len(buttons) > 3:
    buttons[3].click()
```

### 方法3：获取剪贴板内容
点击复制后，获取剪贴板内容：
```python
import subprocess
result = subprocess.run(['pbpaste'], capture_output=True, text=True)
token = result.stdout.strip()
```

## 完整示例：复制Replicate API Token

```python
from playwright.sync_api import sync_playwright
import subprocess

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:18800')
    
    for page in browser.contexts[0].pages:
        if 'api-tokens' in page.url:
            # 找到复制按钮并点击
            buttons = page.query_selector_all('button')
            for btn in buttons:
                if btn.query_selector('svg'):
                    btn.click()
                    break
    
    browser.close()

# 获取剪贴板
result = subprocess.run(['pbpaste'], capture_output=True, text=True)
api_token = result.stdout.strip()
print(f"API Token: {api_token}")
```

## 注意事项
1. 点击复制按钮后，需要等待一小段时间让剪贴板更新
2. 使用 `pbpaste` 获取macOS剪贴板内容
3. 某些网站可能有多个复制按钮，需要选择正确的那个
