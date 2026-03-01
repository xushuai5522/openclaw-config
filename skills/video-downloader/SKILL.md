# 技能：视频爬取

从网页中爬取视频，用于学习培训视频等场景。

## 适用场景
- 需要保存网页中的视频进行离线学习
- 批量下载培训课程视频

## 爬取方法

### 步骤1：定位视频页面
使用Playwright连接浏览器，打开目标视频页面。

### 步骤2：提取视频URL
从页面HTML中提取视频URL：
```python
import re
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:18800')
    page = browser.contexts[0].pages[0]
    
    html = page.content()
    
    # 查找视频URL
    patterns = ['video', 'mp4', 'm3u8', 'media']
    for pattern in patterns:
        matches = re.findall(rf'https?://[^\s"<>]+{pattern}[^\s"<>]*', html, re.I)
        if matches:
            print(f'Found: {matches[0]}')
    
    browser.close()
```

### 步骤3：下载视频
```bash
curl -L -o video.mp4 "视频URL"
```

## 常见视频URL模式
- `media.rrzuji.cn` - 人人租视频
- 关键词：`video`, `mp4`, `m3u8`, `media`, `blob`

## 注意事项
1. 视频URL可能需要登录态，从已登录的浏览器中提取
2. 部分视频使用特殊播放器，URL不在DOM中暴露
3. 提取URL后直接用curl下载即可
