---
name: weather
description: Get current weather and forecasts (no API key required).
homepage: https://wttr.in/:help
metadata: {"clawdbot":{"emoji":"🌤️","requires":{"bins":["curl"]}}}
---

# Weather

## 快速参考

- **触发词**: 天气、weather、天气预报
- **数据源**: wttr.in (主要) / Open-Meteo (备用)
- **优势**: 无需API Key，免费使用

---

## 使用示例

### 示例1: 快速查询当前天气

```bash
# 苏州天气
curl -s "wttr.in/Suzhou?format=3"
# 输出: Suzhou: ⛅️ +15°C

# 北京天气
curl -s "wttr.in/Beijing?format=3"
# 输出: Beijing: ☀️ +8°C

# 上海天气
curl -s "wttr.in/Shanghai?format=3"
# 输出: Shanghai: 🌧 +12°C
```

---

### 示例2: 详细天气信息

```bash
# 完整格式（位置+天气+温度+湿度+风速）
curl -s "wttr.in/Suzhou?format=%l:+%c+%t+%h+%w"
# 输出: Suzhou: ⛅️ +15°C 65% ↙5km/h

# 解释：
# %l = 位置 (Suzhou)
# %c = 天气状况 (⛅️)
# %t = 温度 (+15°C)
# %h = 湿度 (65%)
# %w = 风速风向 (↙5km/h)
```

---

### 示例3: 未来天气预报

```bash
# 3天预报
curl -s "wttr.in/Suzhou"

# 输出示例:
# Weather report: Suzhou
# 
#      \  /       Partly cloudy
#    _ /"".-.     15 °C          
#      \_(   ).   ↙ 5 km/h       
#      /(___(__)  10 km          
#                 0.0 mm         
# 
# ┌──────────────────────────────┬───────────────────────┐
# │            Monday 03         │     Tuesday 04        │
# ├──────────────────────────────┼───────────────────────┤
# │     \   /     Sunny          │    \  /       Partly  │
# │      .-.      18 °C          │  _ /"".-.     16 °C   │
# │   ― (   ) ―   ↙ 8 km/h       │    \_(   ).   ↙ 6 km/h│
# │      `-'      10 km          │    /(___(__)  10 km   │
# │     /   \     0.0 mm         │              0.0 mm   │
# └──────────────────────────────┴───────────────────────┘

# 只看今天
curl -s "wttr.in/Suzhou?1"

# 只看当前
curl -s "wttr.in/Suzhou?0"
```

---

### 示例4: 不同单位和语言

```bash
# 公制单位（摄氏度、公里）
curl -s "wttr.in/Suzhou?m&format=3"

# 美制单位（华氏度、英里）
curl -s "wttr.in/Suzhou?u&format=3"

# 中文输出
curl -s "wttr.in/Suzhou?lang=zh&format=3"
# 输出: 苏州: ⛅️ +15°C
```

---

### 示例5: 特殊位置查询

```bash
# 机场代码
curl -s "wttr.in/PVG?format=3"  # 上海浦东机场
curl -s "wttr.in/PEK?format=3"  # 北京首都机场

# 带空格的城市名（URL编码）
curl -s "wttr.in/New+York?format=3"
curl -s "wttr.in/Los+Angeles?format=3"

# 经纬度
curl -s "wttr.in/31.2304,121.4737?format=3"  # 上海坐标
```

---

### 示例6: 生成天气图片

```bash
# 生成PNG图片
curl -s "wttr.in/Suzhou.png" -o /tmp/weather.png

# 透明背景PNG
curl -s "wttr.in/Suzhou_transparency=150.png" -o /tmp/weather.png

# 在飞书/微信中发送天气图片
# 1. 下载图片
curl -s "wttr.in/Suzhou.png" -o ~/.openclaw/workspace/weather.png
# 2. 发送图片（使用message工具）
```

---

### 示例7: 程序化使用（JSON格式）

```bash
# 使用Open-Meteo API（返回JSON）
curl -s "https://api.open-meteo.com/v1/forecast?latitude=31.2304&longitude=121.4737&current_weather=true"

# 输出示例:
# {
#   "latitude": 31.23,
#   "longitude": 121.47,
#   "current_weather": {
#     "temperature": 15.2,
#     "windspeed": 5.4,
#     "winddirection": 225,
#     "weathercode": 2,
#     "time": "2026-03-02T15:00"
#   }
# }

# 解析JSON
curl -s "https://api.open-meteo.com/v1/forecast?latitude=31.2304&longitude=121.4737&current_weather=true" | jq '.current_weather.temperature'
# 输出: 15.2
```

---

## Two free services, no API keys needed.

## wttr.in (primary)

Quick one-liner:
```bash
curl -s "wttr.in/London?format=3"
# Output: London: ⛅️ +8°C
```

Compact format:
```bash
curl -s "wttr.in/London?format=%l:+%c+%t+%h+%w"
# Output: London: ⛅️ +8°C 71% ↙5km/h
```

Full forecast:
```bash
curl -s "wttr.in/London?T"
```

Format codes: `%c` condition · `%t` temp · `%h` humidity · `%w` wind · `%l` location · `%m` moon

Tips:
- URL-encode spaces: `wttr.in/New+York`
- Airport codes: `wttr.in/JFK`
- Units: `?m` (metric) `?u` (USCS)
- Today only: `?1` · Current only: `?0`
- PNG: `curl -s "wttr.in/Berlin.png" -o /tmp/weather.png`

## Open-Meteo (fallback, JSON)

Free, no key, good for programmatic use:
```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true"
```

Find coordinates for a city, then query. Returns JSON with temp, windspeed, weathercode.

Docs: https://open-meteo.com/en/docs

---

## 格式代码参考

| 代码 | 含义 | 示例 |
|------|------|------|
| %c | 天气状况 | ⛅️ |
| %t | 温度 | +15°C |
| %h | 湿度 | 65% |
| %w | 风速风向 | ↙5km/h |
| %l | 位置 | Suzhou |
| %m | 月相 | 🌕 |
| %p | 降水量 | 0.0mm |
| %P | 气压 | 1013hPa |

---

## 常见场景

### 每日早报
```bash
# 添加到HEARTBEAT.md，每天早上8点检查
curl -s "wttr.in/Suzhou?format=%l:+%c+%t+%h+%w"
# 如果有雨，提醒大哥带伞
```

### 出行提醒
```bash
# 检查未来3天天气
curl -s "wttr.in/Suzhou?1"
# 根据天气建议穿衣
```

### 多地对比
```bash
# 对比多个城市天气
for city in Suzhou Beijing Shanghai; do
  echo "$city: $(curl -s "wttr.in/$city?format=3")"
done
```

---

## 常见问题

### 中文城市名不识别
```bash
# 使用拼音
curl -s "wttr.in/Suzhou?format=3"  # ✅
curl -s "wttr.in/苏州?format=3"    # ❌ 可能不识别
```

### 服务不可用
```bash
# wttr.in超时，使用Open-Meteo备用
curl -s "https://api.open-meteo.com/v1/forecast?latitude=31.2304&longitude=121.4737&current_weather=true"
```

### 获取城市坐标
```bash
# 使用geocoding API
curl -s "https://geocoding-api.open-meteo.com/v1/search?name=Suzhou&count=1" | jq '.results[0] | {latitude, longitude}'
```
