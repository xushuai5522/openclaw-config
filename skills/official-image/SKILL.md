# 技能：官网产品图片获取

从品牌官网获取产品图片，处理后用于电商上架。

## 适用场景
- 获取Apple/华为/小米等官网产品图
- 获取品牌官方产品图片

## 方法：浏览器截图法

由于官网CDN有访问限制，直接下载会失败。采用浏览器截图方案：

### 步骤1：获取图片URL
用Playwright打开官网页面，提取所有图片URL：
```python
images = page.evaluate('''
    () => {
        const results = [];
        document.querySelectorAll('img').forEach(img => {
            if (img.width > 300 && img.src) {
                results.push({src: img.src, width: img.width});
            }
        });
        return results;
    }
''')
```

### 步骤2：用浏览器打开图片并截图
```python
# 打开图片URL
page.goto("图片URL")
page.screenshot(path="output.png")
```

### 步骤3：处理成白底图
用Pillow裁剪并转为800x800白底图

## 示例：Mac Studio
1. 打开 https://www.apple.com.cn/mac-studio/
2. 提取图片URL，如 `https://www.apple.com.cn/v/mac-studio/k/images/overview/hero/static_front__fmvxo.png`
3. 用浏览器打开该URL
4. 截图保存
5. 裁剪处理

## 依赖
- Playwright
- Pillow
