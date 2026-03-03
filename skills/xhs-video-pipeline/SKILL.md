---
name: xhs-video-pipeline
description: 小红书视频制作流水线。协调视频分析、脚本撰写、剪辑、音频处理四个角色协同工作。当用户提到制作视频、剪辑视频、视频发布时激活。
---

# 小红书视频制作流水线


## 快速参考
- **触发词**: 小红书视频制作、视频流水线
- **核心功能**: 协调视频分析、脚本、剪辑、音频
- **适用场景**: 小红书视频内容生产

---

## 触发条件
用户提到：做视频、剪视频、视频笔记、拍了视频

---

## 四大角色协同

```
素材输入
   ↓
🔍 视频分析大师 → 分析素材内容、筛选精彩片段、标记关键时间点
   ↓
📝 脚本大师 → 根据分析结果撰写文案脚本、规划镜头顺序
   ↓
🎬 剪辑大师 → 裁剪拼接、调速、加转场、加字幕、调色
   ↓
🎵 音频处理大师 → 配背景音乐、调音量、生成配音
   ↓
成品输出 → 保存草稿/发布
```

---

## 🔍 角色1：视频分析大师

### 职责
- 分析视频素材内容（人物、场景、动作、表情）
- 标记精彩片段时间点
- 评估画质、光线、构图
- 筛选最佳素材

### 使用技能
- `video-watcher` — 按间隔提取帧，分析视频内容
- `video-frames` — 提取关键帧/短片段

### 工作流程
```bash
# 1. 提取帧分析内容
bash skills/video-watcher/scripts/extract_frames.sh input.mp4 output_dir 5

# 2. 用image工具逐帧分析
# 识别：宝宝表情、动作、场景、光线质量

# 3. 输出分析报告
# - 精彩片段时间点列表
# - 每段内容描述
# - 推荐使用片段排序
```

### 输出格式
```
## 素材分析报告
| 时间段 | 内容 | 评分 | 推荐用途 |
|--------|------|------|----------|
| 0:03-0:08 | 宝宝笑着看镜头 | ⭐⭐⭐⭐⭐ | 封面/开头 |
| 0:15-0:22 | 宝宝爬行 | ⭐⭐⭐⭐ | 中间过渡 |
| 0:30-0:35 | 宝宝吃东西表情 | ⭐⭐⭐⭐⭐ | 搞笑片段 |
```

---

## 📝 角色2：脚本大师

### 职责
- 根据素材分析结果规划视频结构
- 撰写文案（标题+正文+字幕文本）
- 规划镜头顺序和节奏
- 设计字幕出现时机

### 文案规则（继承xhs-publish）
- **拟人、俏皮、口语化，严禁AI味！**
- 短句为主，带小幽默
- 字幕简短有力，每条不超过15字

### 脚本模板
```
## 视频脚本

标题：{标题}
时长：{预计时长}秒
BGM：{推荐BGM风格}

| 序号 | 时间 | 画面 | 字幕 | 备注 |
|------|------|------|------|------|
| 1 | 0-3s | 宝宝笑脸特写 | "今天又被她拿捏了" | 开头hook |
| 2 | 3-8s | 宝宝爬行 | "12个月 已经到处跑了" | 日常展示 |
| 3 | 8-12s | 搞笑表情 | "这表情绝了😂" | 高潮 |
| 4 | 12-15s | 温馨画面 | "当爸爸真的太幸福了" | 结尾 |
```

### 小红书视频规格
| 参数 | 推荐值 |
|------|--------|
| 比例 | 3:4（竖屏）或 1:1（方形） |
| 分辨率 | 1080×1440 或 1080×1080 |
| 时长 | 15-60秒（最佳30秒左右） |
| 封面 | 从视频中截取最佳帧 |

---

## 🎬 角色3：剪辑大师

### 职责
- 按脚本裁剪拼接视频片段
- 调整播放速度（慢动作/加速）
- 添加转场效果
- 烧录字幕
- 调整画面比例
- 生成封面图

### 使用技能
- `ffmpeg-video-editor` — 自然语言→ffmpeg命令
- `ffmpeg-cli` — 完整ffmpeg操作（脚本化）
- `video-edit` — AI增强（调色、防抖、画质提升）
- `video-subtitles` — 自动字幕生成+烧录

### 常用操作

#### 裁剪片段
```bash
ffmpeg -y -hide_banner -i input.mp4 -ss 00:00:03 -to 00:00:08 -c copy clip1.mp4
```

#### 拼接片段
```bash
# 创建文件列表
echo "file 'clip1.mp4'" > files.txt
echo "file 'clip2.mp4'" >> files.txt
echo "file 'clip3.mp4'" >> files.txt
# 拼接
ffmpeg -y -hide_banner -f concat -safe 0 -i files.txt -c copy merged.mp4
```

#### 竖屏适配（3:4）
```bash
ffmpeg -y -hide_banner -i input.mp4 \
  -vf "scale=1080:1440:force_original_aspect_ratio=decrease,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:black" \
  -c:a copy output_vertical.mp4
```

#### 加字幕
```bash
ffmpeg -y -hide_banner -i input.mp4 \
  -vf "subtitles='subs.srt':force_style='FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2'" \
  output_subtitled.mp4
```

#### 慢动作
```bash
ffmpeg -y -hide_banner -i input.mp4 \
  -filter_complex "[0:v]setpts=2.0*PTS[v];[0:a]atempo=0.5[a]" \
  -map "[v]" -map "[a]" output_slow.mp4
```

#### 截取封面
```bash
ffmpeg -y -hide_banner -i input.mp4 -ss 00:00:05 -frames:v 1 cover.jpg
```

---

## 🎵 角色4：音频处理大师

### 职责
- 添加背景音乐（控制音量平衡）
- 生成AI配音（edge-tts）
- 提取/替换音频轨道
- 音量标准化

### 常用操作

#### 添加BGM（降低BGM音量）
```bash
ffmpeg -y -hide_banner -i video.mp4 -i bgm.mp3 \
  -filter_complex "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy output.mp4
```

#### 生成AI配音
```bash
edge-tts --voice zh-CN-XiaoyiNeural --rate=+10% --text "字幕文本" --write-media voiceover.mp3
```

#### 替换音频
```bash
ffmpeg -y -hide_banner -i video.mp4 -i new_audio.mp3 \
  -map 0:v -map 1:a -c:v copy -shortest output.mp4
```

#### 提取音频
```bash
ffmpeg -y -hide_banner -i video.mp4 -vn -acodec libmp3lame audio.mp3
```

#### 音量标准化
```bash
ffmpeg -y -hide_banner -i input.mp4 -af loudnorm output.mp4
```

---

## 完整制作流程示例

```bash
# 1. 分析素材
bash skills/video-watcher/scripts/extract_frames.sh raw_video.mp4 ./frames 3

# 2. 根据分析结果裁剪精彩片段
ffmpeg -y -hide_banner -i raw_video.mp4 -ss 00:00:03 -to 00:00:08 -c copy clip1.mp4
ffmpeg -y -hide_banner -i raw_video.mp4 -ss 00:00:15 -to 00:00:22 -c copy clip2.mp4
ffmpeg -y -hide_banner -i raw_video.mp4 -ss 00:00:30 -to 00:00:35 -c copy clip3.mp4

# 3. 拼接
printf "file 'clip1.mp4'\nfile 'clip2.mp4'\nfile 'clip3.mp4'" > files.txt
ffmpeg -y -hide_banner -f concat -safe 0 -i files.txt -c copy merged.mp4

# 4. 竖屏适配
ffmpeg -y -hide_banner -i merged.mp4 \
  -vf "scale=1080:1440:force_original_aspect_ratio=decrease,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:white" \
  -c:a copy vertical.mp4

# 5. 加字幕
ffmpeg -y -hide_banner -i vertical.mp4 \
  -vf "subtitles='subs.srt':force_style='FontSize=22,PrimaryColour=&HFFFFFF,Outline=2'" \
  subtitled.mp4

# 6. 加BGM
ffmpeg -y -hide_banner -i subtitled.mp4 -i bgm.mp3 \
  -filter_complex "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy final.mp4

# 7. 截取封面
ffmpeg -y -hide_banner -i final.mp4 -ss 00:00:02 -frames:v 1 cover.jpg
```

---

## 已安装的视频技能清单

| 技能 | 用途 | 对应角色 |
|------|------|----------|
| video-watcher | 视频内容分析（提取帧） | 🔍 分析大师 |
| video-frames | 提取关键帧/短片段 | 🔍 分析大师 |
| ffmpeg-video-editor | 自然语言→ffmpeg命令 | 🎬 剪辑大师 |
| ffmpeg-cli | ffmpeg全功能脚本 | 🎬 剪辑大师 |
| video-edit | AI增强（调色/防抖/画质） | 🎬 剪辑大师 |
| video-subtitles | 自动字幕生成+烧录 | 🎬 剪辑大师 |
| vea | 视频编辑Agent（集锦生成） | 🎬 剪辑大师 |

---

## 注意事项
- 视频素材存储：`/Users/xs/.openclaw/workspace/xiaohongshu/视频素材/`
- 成品存储：`/Users/xs/.openclaw/workspace/xiaohongshu/成品视频/`
- 小红书视频最大支持5分钟，推荐15-60秒
- 竖屏（3:4或9:16）比横屏流量好
- 前3秒必须抓眼球
