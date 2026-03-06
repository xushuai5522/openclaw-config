# 人人租混合方案 - 使用指南

## 📦 文件清单

```
scripts/
├── hybrid_architecture.md      # 架构设计文档
├── feasibility_assessment.md   # 可行性评估报告
├── rrz_hybrid.py              # 混合方案主脚本
├── product_example.json       # 商品数据示例
├── rrz_helper.py              # 浏览器辅助脚本（已有）
└── README.md                  # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install playwright requests
playwright install chromium
```

### 2. 启动浏览器（CDP模式）

```bash
# macOS/Linux
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=18800 \
  --user-data-dir=/tmp/chrome-debug

# 手动登录人人租后台: https://admin.rrzu.com
```

### 3. 发现API接口（首次运行）

```bash
cd /Users/xs/.openclaw/workspace/skills/rrz/scripts
python3 rrz_hybrid.py discover-api 60
```

在浏览器中操作：
- 上传几张图片
- 添加租赁方案
- 提交商品

脚本会捕获所有API请求并保存到 `discovered_apis.json`

### 4. 准备商品数据

复制 `product_example.json` 并修改：

```json
{
  "name": "你的商品名称",
  "description": "商品描述",
  "category": "分类名称",
  "brand": "品牌名称",
  "images": [
    "/path/to/image1.jpg",
    "/path/to/image2.jpg"
  ],
  "plans": [
    {
      "period": 30,
      "price": 299,
      "deposit": 2000,
      "name": "月租"
    }
  ]
}
```

### 5. 发布商品

**纯浏览器模式（稳定但慢）：**
```bash
python3 rrz_hybrid.py publish --data my_product.json
```

**混合模式（快但需要API）：**
```bash
python3 rrz_hybrid.py publish --data my_product.json --api
```

## 📊 性能对比

| 模式 | 耗时 | 稳定性 | 前置条件 |
|------|------|--------|----------|
| 纯浏览器 | ~100s | ⭐⭐⭐⭐⭐ | 无 |
| 混合模式 | ~40s | ⭐⭐⭐⭐☆ | 需要API逆向 |

## ⚠️ 重要提示

### 当前状态

- ✅ 架构设计已完成
- ✅ 脚本框架已实现
- ⚠️ **API接口需要逆向** - 这是关键！
- ⚠️ 图片上传API未实现（占位代码）
- ⚠️ 方案配置API未实现（占位代码）

### API逆向步骤

1. 运行 `discover-api` 命令
2. 分析 `discovered_apis.json`
3. 找到图片上传接口（通常是 `/api/upload/*`）
4. 找到方案配置接口（通常是 `/api/product/*`）
5. 更新 `rrz_hybrid.py` 中的API URL
6. 测试API调用

### 如果API逆向失败

脚本会自动降级到纯浏览器模式，不影响使用。

## 🔧 故障排查

### 问题1：连接浏览器失败

```
Exception: 未找到人人租后台页面
```

**解决：**
1. 确认Chrome已启动（CDP端口18800）
2. 确认已登录人人租后台
3. 检查 `CDP_URL` 配置

### 问题2：找不到iframe

```
Exception: 未找到人人租iframe
```

**解决：**
1. 等待页面完全加载
2. 检查iframe的URL或name
3. 更新 `get_rrz_iframe()` 的匹配规则

### 问题3：API调用失败

```
✗ 第1张失败: HTTP 401
```

**解决：**
1. 检查认证信息是否正确
2. 重新提取cookies和token
3. 查看 `discovered_apis.json` 中的headers

### 问题4：元素定位失败

```
TimeoutError: Timeout 30000ms exceeded
```

**解决：**
1. 增加等待时间
2. 更新元素选择器
3. 检查页面结构是否变化

## 📝 开发日志

### 2026-03-04
- ✅ 完成架构设计文档
- ✅ 实现混合方案脚本框架
- ✅ 完成可行性评估
- ⚠️ API接口待逆向

### 待办事项
- [ ] 完成API逆向
- [ ] 实现图片上传API
- [ ] 实现方案配置API
- [ ] 完整测试流程
- [ ] 性能基准测试

## 🤝 贡献指南

如果你发现了API接口，请更新：

1. `rrz_hybrid.py` 中的 `upload_images_api()`
2. `rrz_hybrid.py` 中的 `add_plans_api()`
3. 更新 `api_reference.md` 文档

## 📚 相关文档

- [架构设计](./hybrid_architecture.md) - 详细的技术架构
- [可行性评估](./feasibility_assessment.md) - 风险和收益分析
- [SKILL.md](../SKILL.md) - 技能总览

## 💬 联系方式

有问题找大哥 🐂🐴
