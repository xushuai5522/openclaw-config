# 人人租自动化发布 - Selenium版

> 状态说明（2026-03-15）：这个目录保留为**当前主线代码骨架**，但 README 中部分“已支持/已完成”表述带有历史乐观成分。继续开发时以 `projects/rrz.md`、`projects/rrz-codebase.md` 和真实代码/真实页面验证为准，不直接把本 README 当现状。

专为NEC服务器设计，使用真实Chrome + Selenium处理弹窗问题。

## 核心优势

✅ **真实Chrome浏览器** - 不是无头浏览器，完全模拟真人操作  
✅ **原生弹窗处理** - Selenium可以直接处理JavaScript alert/confirm  
✅ **自动ChromeDriver管理** - webdriver-manager自动下载匹配版本  
✅ **稳定可靠** - 比Playwright在NEC服务器上更稳定  

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置账号

```bash
cp config.example.env .env
# 编辑.env文件，填入真实账号密码
```

### 3. 运行测试

```bash
python rrz_selenium.py
```

## 使用方法

### 基础用法

```python
from rrz_selenium import RRZSeleniumPublisher

# 创建发布器
publisher = RRZSeleniumPublisher(headless=False)

# 初始化浏览器
publisher.setup_driver()

# 登录
publisher.login('13800138000', 'password')

# 发布商品
product_data = {
    'title': '商品名称',
    'category': '数码产品',
    'description': '商品描述',
    'pricing': {
        'daily_price': 10,
        'deposit': 100,
        'stock': 5
    }
}

image_paths = ['image1.jpg', 'image2.jpg']
publisher.publish_product(product_data, image_paths)

# 关闭浏览器
publisher.close()
```

### 处理弹窗

```python
# Selenium的核心优势：原生弹窗处理
publisher.handle_alert(timeout=3)
```

## 与Playwright对比

| 特性 | Selenium | Playwright |
|------|----------|------------|
| 弹窗处理 | ✅ 原生支持 | ❌ 需要复杂配置 |
| NEC服务器兼容性 | ✅ 完美 | ⚠️ 有问题 |
| ChromeDriver管理 | ✅ 自动 | ⚠️ 手动 |
| 学习曲线 | 平缓 | 陡峭 |

## 项目结构

```
rrz-selenium-fighter/
├── rrz_selenium.py      # 核心发布器
├── requirements.txt     # Python依赖
├── config.example.env   # 配置模板
└── README.md           # 本文件
```

## 常见问题

### Q: ChromeDriver版本不匹配？
A: webdriver-manager会自动下载匹配的ChromeDriver，无需手动管理。

### Q: 弹窗处理失败？
A: 检查弹窗类型，Selenium支持alert/confirm/prompt三种原生弹窗。

### Q: 无头模式运行？
A: 设置 `headless=True`，但建议先用有头模式调试。

## 开发计划

- [x] 基础登录功能
- [x] 商品信息填写
- [x] 图片上传
- [x] 价格设置
- [x] 弹窗处理
- [ ] 批量发布
- [ ] 错误重试
- [ ] 日志记录
- [ ] 截图保存

## License

MIT
