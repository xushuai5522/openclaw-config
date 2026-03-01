# 技能：电商商品主图生成

## 功能
从商品图片生成符合电商平台（淘宝/京东/人人租）要求的商品主图

## 适用场景
- 需要生成商品主图上架电商平台
- 现有图片不符合平台要求（背景、文字、水印等）
- 需要统一风格的商品主图

## 提示词模板

### 图生图提示词
```
【电商商品主图生成】
产品：{product_name}

【处理步骤】
1. 背景移除：删除原图背景、所有文字，水印、logo
2. 商品优化：边缘锐利、材质清晰，光影自然、颜色准确
3. 背景设置：纯白色 #FFFFFF，居中布局
4. 输出规格：800×800px，PNG/JPG

【生成视角】
- 正面：商品正面完整展示
- 侧面45度：展示立体感和细节
- 背面：背面全貌和特征

【质量标准】
- 商品占比：70-80%
- 边缘：平滑无瑕疵
- 清晰度：高清锐利
- 光影：自然柔和
- 平台适配：淘宝/京东标准

【风格】：干净专业、电商主图风格
```

## 火山引擎API

### 配置
- API地址：https://ark.cn-beijing.volces.com/api/v3/images/generations
- API Key：675362ca-6313-43e5-a705-3046f668e2b1
- 模型：doubao-seedream-4-0-250828

### 调用示例
```python
import requests
import base64

API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
KEY = "675362ca-6313-43e5-a705-3046f668e2b1"

# 读取图片转base64
with open("product.jpg", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode()

prompt = """【电商商品主图生成】
产品：vivo X200 Pro mini

【处理步骤】
1. 背景移除：删除原图背景、所有文字，水印、logo
2. 商品优化：边缘锐利、材质清晰，光影自然、颜色准确
3. 背景设置：纯白色 #FFFFFF，居中布局
4. 输出规格：800×800px，PNG/JPG

【生成视角】
- 正面：商品正面完整展示

【质量标准】
- 商品占比：70-80%
- 边缘：平滑无瑕疵
- 清晰度：高清锐利

【风格】：干净专业、电商主图风格"""

resp = requests.post(
    API_URL,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"},
    json={
        "model": "doubao-seedream-4-0-250828",
        "prompt": prompt,
        "image": f"data:image/jpeg;base64,{img_base64}",
        "response_format": "url",
        "size": "2K",
        "stream": False,
        "watermark": False
    },
    timeout=120
)

result = resp.json()
if "data" in result:
    gen_url = result["data"][0]["url"]
    # 下载生成的图片
    img_data = requests.get(gen_url, timeout=30)
    with open("output.jpg", "wb") as f:
        f.write(img_data.content)
```

## 工作流

### 1. 爬取图片
- 官网 → 必应 → 百度 → 淘宝
- 数量：官网3张 + 必应10张 + 百度10张

### 2. 本地处理
- 使用rembg去除背景
- 叠加纯白底 800x800px

### 3. AI审核
- 底色：纯白底
- 尺寸：≥600x600px
- 无额外文字
- 无缺陷

### 4. 图生图
- 目标：3张主图
- 限制：最多3张/产品
- 视角：正面、侧面45度、背面

## 平台规则

### 人人租
| 规则 | 要求 |
|------|------|
| 底色 | 纯白底色 |
| 尺寸 | 600x600px 以上 |
| 数量 | 主图≥3张 |
| 内容 | 仅商品展示，禁止文字 |

### 淘宝/京东
| 规则 | 要求 |
|------|------|
| 尺寸 | 800x800px 或 700x700px |
| 底色 | 纯白底 |
| 格式 | JPG |
| 质量 | 85%以上 |

## 注意事项
1. 图生图最多生成3张，避免浪费token
2. 如果AI审核通过≥3张，则不需要图生图
3. 生成多张时确保视角不同
4. 使用base64方式传入本地图片
