# 人人租API手动抓包操作指南

## 目标
通过浏览器开发者工具手动抓取人人租后台的API请求，获取真实的接口信息。

## 准备工作

1. 打开人人租后台：https://admin.rrzu.com
2. 确保已登录
3. 按 F12 打开开发者工具
4. 切换到 Network（网络）标签
5. 勾选 "Preserve log"（保留日志）
6. 清空现有记录（点击禁止图标）

## 抓包步骤

### 第一步：获取商品列表API

1. 点击左侧菜单的"商品管理"或"商品列表"
2. 等待页面加载完成
3. 在Network标签中查找包含以下关键词的请求：
   - `product`
   - `goods`
   - `list`
4. 找到后，右键该请求 → Copy → Copy as cURL (bash)
5. 保存到文本文件：`api_product_list.txt`

**需要记录的信息：**
- 完整URL（包含域名和路径）
- 请求方法（GET/POST）
- 请求头中的 Authorization 或 Cookie
- 查询参数（page, size等）

### 第二步：获取商品详情API

1. 在商品列表中，点击任意商品的"查看"或"编辑"按钮
2. 等待详情页加载
3. 在Network标签中查找商品详情请求
4. 右键 → Copy as cURL
5. 保存到：`api_product_detail.txt`

**需要记录的信息：**
- URL格式（是否包含商品ID）
- 响应数据结构

### 第三步：图片上传API

1. 在商品编辑页面，找到图片上传组件
2. 点击上传按钮，选择一张测试图片
3. 在Network标签中查找上传请求（通常是POST，包含 `upload` 或 `image`）
4. 右键 → Copy as cURL
5. 保存到：`api_upload_image.txt`

**需要记录的信息：**
- 上传接口URL
- Content-Type（通常是 multipart/form-data）
- 表单字段名称
- 响应中的图片URL格式

### 第四步：商品创建/更新API

1. 在商品编辑页面，修改任意字段（如商品名称）
2. 点击"保存"按钮
3. 在Network标签中查找保存请求（通常是POST或PUT）
4. 右键 → Copy as cURL
5. 保存到：`api_save_product.txt`

**需要记录的信息：**
- 请求方法（POST创建 / PUT更新）
- 请求体的JSON结构
- 必填字段和可选字段

### 第五步：提交审核API

1. 在商品详情页，找到"提交审核"按钮
2. 点击提交
3. 在Network标签中查找提交请求
4. 右键 → Copy as cURL
5. 保存到：`api_submit_review.txt`

## 数据整理

将所有抓取的cURL命令保存到一个文件中：

```bash
# 创建汇总文件
cat api_*.txt > api_all_captured.txt
```

## 关键信息提取

从抓取的请求中提取以下信息：

### 1. API Base URL
```
示例：https://admin-vue.rrzu.com
或：https://api.rrzu.com
```

### 2. 鉴权方式
```
方式A：Bearer Token
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

方式B：Cookie
Cookie: session_id=abc123; token=xyz789
```

### 3. 接口列表
```
GET  /api/products              - 商品列表
GET  /api/products/{id}         - 商品详情
POST /api/products              - 创建商品
PUT  /api/products/{id}         - 更新商品
POST /api/upload/image          - 上传图片
POST /api/products/{id}/submit  - 提交审核
```

### 4. 请求参数格式
```json
// 创建商品示例
{
  "name": "商品名称",
  "categoryId": 123,
  "images": ["https://..."],
  "description": "描述",
  "specs": {...},
  "plans": [...]
}
```

## 验证步骤

1. 将提取的信息更新到 `rrz_api.py`
2. 运行测试脚本：
   ```bash
   python3 test_api.py "your_token_here"
   ```
3. 查看测试报告：`test_report.md`

## 常见问题

### Q1: 找不到API请求？
A: 尝试以下方法：
- 清空Network日志后重新操作
- 使用Filter过滤：输入 `api` 或 `admin`
- 查看XHR和Fetch类型的请求

### Q2: 请求太多，不知道哪个是API？
A: 关注以下特征：
- URL包含 `/api/`
- 响应类型是 `application/json`
- 请求方法是 POST/PUT/DELETE
- 响应数据包含 `code`, `data`, `message` 等字段

### Q3: 如何获取Token？
A: 三种方法：
1. 从Network请求头中复制 Authorization
2. 从Application → Cookies 中查找
3. 从Application → Local Storage 中查找

### Q4: cURL命令太长怎么办？
A: 可以只复制关键部分：
- URL
- Authorization头
- 请求体（-d 参数后的内容）

## 输出文件

完成后应该有以下文件：
- `api_product_list.txt` - 商品列表请求
- `api_product_detail.txt` - 商品详情请求
- `api_upload_image.txt` - 图片上传请求
- `api_save_product.txt` - 保存商品请求
- `api_submit_review.txt` - 提交审核请求
- `api_all_captured.txt` - 所有请求汇总

## 下一步

将抓取的信息整理后，更新以下文件：
1. `api_documentation.md` - 补充实际的接口信息
2. `rrz_api.py` - 修改base_url和接口路径
3. 运行 `test_api.py` 验证可行性

---

**预计时间**: 10-15分钟  
**难度**: ⭐⭐（需要基本的浏览器开发者工具使用经验）
