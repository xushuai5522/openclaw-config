# 本地图片处理工作流

## 完整流程

```
1. 官网下载原图 → 获取高清无处理图片
2. rembg抠图 → 去除背景
3. 纯白底叠加 → 居中放置白底
4. AI审核 → 质量检查
```

## 最佳方案（已验证）

### 步骤1：官网下载
```python
# Apple官网示例
url = "https://www.apple.com/shop/buy-mac/mac-studio"

# 提取高分辨率图片URL
js_code = '''
() => {
  const images = [];
  document.querySelectorAll('img').forEach(img => {
    if (img.src && img.src.includes('storeimages.cdn-apple.com')) {
      images.push(img.src.replace(/wid=\d+/, 'wid=2048'));
    }
  });
  return [...new Set(images)];
}
'''
```

### 步骤2：rembg抠图（关键代码）
```python
from rembg import remove
from PIL import Image

img = Image.open('input.jpg')
output = remove(img)  # 抠图

# 关键：正确叠加白底
white = Image.new('RGBA', (output.width, output.height), (255, 255, 255, 255))
# 使用alpha通道正确叠加
if output.mode == 'RGBA':
    output.paste(white, (0, 0), output)  # 用alpha作为mask
else:
    output = output.convert('RGBA')
    output.paste(white, (0, 0), output)

# 调整到800x800
output = output.resize((800, 800), Image.Resampling.LANCZOS)
output.convert('RGB').save('output.jpg', 'JPEG', quality=95)
```

### 步骤3：纯白底
```python
# 创建800x800纯白底
final = Image.new('RGB', (800, 800), (255, 255, 255))
final.paste(img, ((800-img.width)//2, (800-img.height)//2))
```

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

| 图片 | 背景 | 商品完整 | 结果 |
|------|------|----------|------|
| Mac Studio 1 | 纯白 | 是 | ✅ |
| Mac Studio 2 | 纯白 | 是 | ✅ |
| Mac Studio 3 | 纯白 | 是 | ✅ |

## 常见问题

1. **rembg处理后背景变黑** → 用alpha通道正确叠加白底
2. **图片失真** → 官网原图质量最高，不要过度处理
3. **淘宝图片多为营销图** → 优先使用官网图片
4. **复杂渐变背景处理效果差** → 使用GrabCut算法

## 背景复杂度与处理效果

| 背景类型 | 示例 | rembg效果 | GrabCut效果 |
|----------|------|------------|--------------|
| 纯灰/白色 | Mac Studio | ✅ 好 | ✅ 好 |
| 彩色渐变 | iPhone 17 | ❌ 差 | ✅ 好 |

## GrabCut处理代码

```python
import cv2
import numpy as np

img = cv2.imread('input.jpg')
h, w = img.shape[:2]

mask = np.zeros((h, w), np.uint8)
bgdModel = np.zeros((1, 65), np.float64)
fgdModel = np.zeros((1, 65), np.float64)

# 初始矩形
rect = (w//3, h//4, w*2//3, h*2//3)

# 运行GrabCut
cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 10, cv2.GC_INIT_WITH_RECT)

# 提取前景
mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

# 叠加白底
result = img * mask2[:, :, np.newaxis]
white_bg = np.ones((h, w, 3)) * 255
result = np.where(mask2[:, :, np.newaxis] == 1, result, white_bg)

cv2.imwrite('output.jpg', result)
```

## 背景复杂度与处理效果

| 背景类型 | 示例 | rembg效果 |
|----------|------|------------|
| 纯灰/白色 | Mac Studio | ✅ 好 |
| 彩色渐变 | iPhone 17 | ❌ 差 |

## 解决方案

1. 优先选择灰色/白色背景的产品图
2. 复杂背景需要使用 GrabCut 等更高级的分割算法
