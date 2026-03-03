---
name: summarize
description: Summarize URLs or files with the summarize CLI (web, PDFs, images, audio, YouTube).
homepage: https://summarize.sh
metadata: {"clawdbot":{"emoji":"🧾","requires":{"bins":["summarize"]},"install":[{"id":"brew","kind":"brew","formula":"steipete/tap/summarize","bins":["summarize"],"label":"Install summarize (brew)"}]}}
---

# Summarize

## 快速参考

- **触发词**: 总结、摘要、summarize
- **支持格式**: 网页、PDF、图片、音频、视频、YouTube
- **核心命令**: `summarize <url/file> --model <model>`

---

## 使用示例

### 示例1: 总结网页文章

```bash
# 总结技术博客
summarize "https://blog.example.com/ai-trends-2026" \
  --model google/gemini-3-flash-preview \
  --length medium

# 输出示例:
# 文章总结了2026年AI发展的三大趋势：
# 1. 多模态模型成为主流
# 2. AI Agent广泛应用于企业
# 3. 开源模型性能接近闭源
```

---

### 示例2: 总结PDF文档

```bash
# 总结技术文档
summarize "/path/to/whitepaper.pdf" \
  --model openai/gpt-4o \
  --length long

# 总结学术论文
summarize "research-paper.pdf" \
  --model anthropic/claude-opus-4 \
  --length xl
```

---

### 示例3: 总结YouTube视频

```bash
# 总结技术教程视频
summarize "https://youtu.be/dQw4w9WgXcQ" \
  --youtube auto \
  --model google/gemini-3-flash-preview

# 输出示例:
# 视频内容：介绍了如何使用OpenClaw进行自动化
# 主要步骤：
# 1. 安装配置
# 2. 编写技能
# 3. 测试部署
# 时长：15分钟
```

---

### 示例4: 总结音频文件

```bash
# 总结播客
summarize "podcast-episode.mp3" \
  --model openai/gpt-4o \
  --length medium

# 总结会议录音
summarize "meeting-recording.wav" \
  --model anthropic/claude-sonnet-4 \
  --length short
```

---

### 示例5: 总结图片内容

```bash
# 总结图表
summarize "chart.png" \
  --model google/gemini-3-flash-preview

# 总结截图
summarize "screenshot.jpg" \
  --model openai/gpt-4o
```

---

### 示例6: 批量总结

```bash
# 总结多个文件
for file in *.pdf; do
  echo "总结: $file"
  summarize "$file" --model google/gemini-3-flash-preview --length short
  echo "---"
done

# 总结多个URL
cat urls.txt | while read url; do
  summarize "$url" --model google/gemini-3-flash-preview --json >> summaries.json
done
```

---

## Quick start

```bash
summarize "https://example.com" --model google/gemini-3-flash-preview
summarize "/path/to/file.pdf" --model google/gemini-3-flash-preview
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto
```

## Model + keys

Set the API key for your chosen provider:
- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- xAI: `XAI_API_KEY`
- Google: `GEMINI_API_KEY` (aliases: `GOOGLE_GENERATIVE_AI_API_KEY`, `GOOGLE_API_KEY`)

Default model is `google/gemini-3-flash-preview` if none is set.

## Useful flags

### 长度控制
- `--length short` - 简短摘要（~100字）
- `--length medium` - 中等长度（~300字）
- `--length long` - 详细总结（~500字）
- `--length xl` - 超长总结（~1000字）
- `--length xxl` - 完整总结（~2000字）
- `--length 500` - 自定义字符数

### 输出控制
- `--max-output-tokens <count>` - 限制输出token数
- `--json` - JSON格式输出（便于程序处理）
- `--extract-only` - 只提取内容，不总结（仅URL）

### 特殊功能
- `--firecrawl auto|off|always` - 使用Firecrawl处理被屏蔽的网站
- `--youtube auto` - YouTube视频自动回退到Apify（需要`APIFY_API_TOKEN`）

## Config

Optional config file: `~/.summarize/config.json`

```json
{
  "model": "openai/gpt-4o",
  "length": "medium",
  "max_output_tokens": 1000
}
```

Optional services:
- `FIRECRAWL_API_KEY` - 处理被屏蔽的网站
- `APIFY_API_TOKEN` - YouTube视频回退方案

---

## 支持的格式

### 网页
- HTML页面
- 博客文章
- 新闻网站
- 技术文档

### 文档
- PDF
- Word (.docx)
- Markdown (.md)
- 纯文本 (.txt)

### 多媒体
- 图片 (PNG, JPG, WebP)
- 音频 (MP3, WAV, M4A)
- 视频 (MP4, MOV)
- YouTube视频

---

## 常见场景

### 技术学习
```bash
# 总结技术博客
summarize "https://blog.example.com/new-tech" --length medium

# 总结技术视频
summarize "https://youtu.be/xxx" --youtube auto --length long
```

### 会议记录
```bash
# 总结会议录音
summarize "meeting.mp3" --model openai/gpt-4o --length medium
```

### 文档阅读
```bash
# 快速了解PDF内容
summarize "report.pdf" --length short

# 详细总结学术论文
summarize "paper.pdf" --length xl
```

---

## 安装

```bash
# macOS (Homebrew)
brew install steipete/tap/summarize

# 验证安装
summarize --version
```

---

## 常见问题

### API Key未设置
```bash
# 设置环境变量
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."

# 或写入配置文件
echo '{"model": "google/gemini-3-flash-preview"}' > ~/.summarize/config.json
```

### 网站被屏蔽
```bash
# 使用Firecrawl
export FIRECRAWL_API_KEY="..."
summarize "https://blocked-site.com" --firecrawl always
```

### YouTube视频无法访问
```bash
# 使用Apify回退
export APIFY_API_TOKEN="..."
summarize "https://youtu.be/xxx" --youtube auto
```
