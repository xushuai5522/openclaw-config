# video-toolkit - 视频处理工具箱

## 快速参考
- **触发词**: 视频处理、视频编辑、字幕生成
- **核心功能**: 下载→编辑→分析→字幕→增强
- **依赖**: ffmpeg, yt-dlp, whisper

---


视频下载、编辑、分析、字幕、增强的综合工具。

## 功能模块

### 1. 视频下载 (video-downloader)
- 支持YouTube、抖音、B站等
- 自动选择最佳画质
- 批量下载
- 断点续传

### 2. 视频分析 (video-watcher)
- 提取关键帧
- 场景识别
- 内容理解
- 生成摘要

### 3. 帧提取 (video-frames)
- 按时间间隔提取帧
- 按场景变化提取
- 批量导出图片
- 支持多种格式

### 4. 视频编辑 (video-edit)
- 剪辑、裁剪、合并
- 转场效果
- 滤镜调色
- 画面调整

### 5. 视频增强 (vea)
- AI背景移除
- 色彩分级
- 视频放大
- 画面稳定

### 6. 字幕生成 (video-subtitles)
- 语音转文字（Whisper）
- 多语言翻译
- 字幕烧录
- SRT格式导出

### 7. FFmpeg工具 (ffmpeg-cli / ffmpeg-video-editor)
- 自然语言生成FFmpeg命令
- 格式转换
- 压缩优化
- 批量处理

## 使用场景

### 下载视频
```bash
# 下载抖音视频
python video_toolkit.py download --url "https://v.douyin.com/xxx"

# 下载YouTube视频
python video_toolkit.py download --url "https://youtube.com/watch?v=xxx"
```

### 分析视频
```bash
# 提取关键帧分析内容
python video_toolkit.py analyze --input video.mp4

# 生成视频摘要
python video_toolkit.py summarize --input video.mp4
```

### 提取帧
```bash
# 每秒提取1帧
python video_toolkit.py extract-frames --input video.mp4 --fps 1

# 提取场景变化帧
python video_toolkit.py extract-frames --input video.mp4 --scene-detect
```

### 编辑视频
```bash
# 剪辑片段
python video_toolkit.py cut --input video.mp4 --start 00:10 --end 00:30

# 添加字幕
python video_toolkit.py add-subtitle --input video.mp4 --srt subtitle.srt

# 调整尺寸
python video_toolkit.py resize --input video.mp4 --width 1920 --height 1080
```

### 生成字幕
```bash
# 语音转文字
python video_toolkit.py transcribe --input video.mp4 --lang zh

# 翻译字幕
python video_toolkit.py translate --input subtitle.srt --from zh --to en

# 烧录字幕
python video_toolkit.py burn-subtitle --input video.mp4 --srt subtitle.srt
```

### FFmpeg命令生成
```bash
# 自然语言生成命令
python video_toolkit.py ffmpeg --prompt "把视频转成16:9，压缩到10MB以内"

# 执行生成的命令
python video_toolkit.py ffmpeg --prompt "提取音频" --execute
```

## 完整流程示例

### 小红书视频制作
```bash
# 1. 下载素材
python video_toolkit.py download --url "抖音链接"

# 2. 分析内容
python video_toolkit.py analyze --input raw.mp4

# 3. 剪辑片段
python video_toolkit.py cut --input raw.mp4 --start 00:10 --end 01:30

# 4. 生成字幕
python video_toolkit.py transcribe --input cut.mp4 --lang zh

# 5. 烧录字幕
python video_toolkit.py burn-subtitle --input cut.mp4 --srt subtitle.srt

# 6. 调整尺寸（小红书9:16）
python video_toolkit.py resize --input final.mp4 --aspect 9:16

# 7. 压缩优化
python video_toolkit.py compress --input final.mp4 --max-size 100MB
```

## 整合说明

本技能整合了以下原有技能：
- video-downloader - 视频下载
- video-watcher - 视频分析
- video-frames - 帧提取
- video-edit - 视频编辑
- vea - 视频增强
- video-subtitles - 字幕生成
- ffmpeg-cli - FFmpeg命令行
- ffmpeg-video-editor - FFmpeg编辑器

所有视频处理功能统一在此技能中管理。

## 依赖工具

- ffmpeg（核心工具）
- yt-dlp（视频下载）
- whisper（语音识别）
- opencv（视频分析）
- PIL/Pillow（帧处理）

## 配置文件

```json
{
  "download": {
    "quality": "best",
    "format": "mp4",
    "output_dir": "./downloads/"
  },
  "transcribe": {
    "model": "base",
    "language": "zh",
    "output_format": "srt"
  },
  "compress": {
    "codec": "h264",
    "crf": 23,
    "preset": "medium"
  }
}
```

## 常见问题

### 下载失败
- 检查网络连接
- 检查代理配置
- 更新yt-dlp版本

### 字幕识别不准
- 使用更大的Whisper模型
- 检查音频质量
- 手动校对修正

### 视频处理慢
- 使用GPU加速
- 降低输出质量
- 减少处理步骤
