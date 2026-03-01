# SKILL.md - 商品图片爬取工作流

## 完整流程

```
1. 官网搜索 → 用户提供产品型号
2. AI分析官网，寻找指定商品详情页
3. 获取官网商品主图
4. AI初筛型号 → 识别并锁定商品主体
5. 淘宝搜索 → 获取商品ID列表
6. AI筛选列表中合适的商品
7. 按筛选的列表结果，逐个进入详情页提取 → 提取商品主体图（imgextra URL）
8. 综合提取 → 10+张主体图片
```

## 步骤详解

### 步骤1-3：官网获取原图
```python
# Apple官网示例
url = "https://www.apple.com/shop/buy-mac/mac-studio"

# 提取图片JS
js_code = '''
() => {
  const images = [];
  document.querySelectorAll('img').forEach(img => {
    if (img.src && img.src.includes('storeimages.cdn-apple.com')) {
      images.push(img.src.replace(/wid=\d+/, 'wid=2048'));
    }
  });
  return [...new Set(images)].slice(0, 15);
}
'''
```

### 步骤4：AI初筛型号
```python
prompt = '''分析这个淘宝搜索结果截图。请识别每个商品的型号。
识别规则：
1. Mac Studio Ultra (M2 Ultra)
2. Mac Studio (M2 Max/Pro)
输出格式：商品标题|型号'''
```

### 步骤5-6：淘宝搜索筛选
```python
# 搜索词
keyword = "Mac Studio M2 Ultra"

# 获取商品ID
js_code = '''
() => {
  const ids = [];
  document.querySelectorAll('a[href*="/item.htm?id="]').forEach(a => {
    const match = a.href.match(/id=(\d+)/);
    if (match) ids.push(match[1]);
  });
  return [...new Set(ids)].slice(0, 10);
}
'''
```

### 步骤7：详情页提取
```python
js_code = '''
() => {
  const images = [];
  document.querySelectorAll('img').forEach(img => {
    if (img.src && img.src.includes('alicdn') && img.src.includes('imgextra')) {
      images.push(img.src);
    }
  });
  return [...new Set(images)].slice(0, 15);
}
'''
```

## 本地图片处理工作流

```
1. 去文字 → opencv inpaint
2. 抠图 → rembg（纯色背景）或 GrabCut（渐变背景）
3. 白底叠加 → PIL居中放置
4. AI审核 → 质量检查
```

## 工具选择

| 背景类型 | 推荐工具 | 效果 |
|----------|----------|------|
| 纯灰/白色 | rembg | ✅ 好 |
| 彩色渐变 | GrabCut | ✅ 好 |

## 抠图代码

### rembg（纯色背景）
```python
from rembg import remove
from PIL import Image

img = Image.open('input.jpg')
output = remove(img)

# 正确叠加白底
if output.mode == 'RGBA':
    output.paste(white, (0, 0), output)
```

### GrabCut（渐变背景）
```python
import cv2
import numpy as np

img = cv2.imread('input.jpg')
h, w = img.shape[:2]

mask = np.zeros((h, w), np.uint8)
bgdModel = np.zeros((1, 65), np.float64)
fgdModel = np.zeros((1, 65), np.float64)
rect = (w//3, h//4, w*2//3, h*2//3)

cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 10, cv2.GC_INIT_WITH_RECT)

mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
result = img * mask2[:, :, np.newaxis]
```

## 数据来源

| 平台 | 状态 | 备注 |
|------|------|------|
| Apple官网 | ✅ 可用 | 图片干净 |
| PICO官网 | ⚠️ 部分可用 | 需访问 |
| 淘宝 | ✅ 可用 | 需要登录 |
| 闲鱼 | ⚠️ 需登录 | |
| 京东 | ⚠️ 需登录 | |

## AI审核标准

```
prompt: "审核这张电商商品图片：
1. 背景是否为纯白底？
2. 是否有残留文字/水印？
3. 商品主体是否完整清晰？
4. 是否可用于主图？"

回答格式：可用/不可用 + 原因
```

## 验证结果

| 商品 | 处理效果 |
|------|----------|
| Mac Studio | ✅ 3张白底图 |
| PICO 4 | ✅ 2张白底图 |
| iPhone 17 | ⚠️ GrabCut处理中 |

## 常见问题

1. **rembg处理后背景变黑** → 用alpha通道正确叠加白底
2. **图片失真** → 官网原图质量最高，不要过度处理
3. **淘宝图片多为营销图** → 优先使用官网图片
4. **复杂渐变背景处理效果差** → 使用GrabCut算法
