# 人人租商品发布混合方案架构设计

## 1. 方案概述

混合方案结合浏览器自动化和API调用的优势：
- **浏览器操作**：处理需要DOM交互的部分（登录、表单填写、下拉选择）
- **API调用**：处理数据传输密集的部分（图片上传、方案配置）

## 2. 技术栈选择

### 浏览器自动化
- **Playwright** (Python)
  - 支持CDP连接现有浏览器
  - 稳定的iframe处理
  - 完善的等待机制

### API调用
- **requests** + **httpx**
  - 复用浏览器的cookies和headers
  - 支持异步上传
  - 灵活的会话管理

## 3. 操作分类

### 适合浏览器的操作
| 操作 | 原因 | 实现方式 |
|------|------|----------|
| 登录 | 需要处理验证码、跳转 | Playwright自动化 |
| 填写基础信息 | 表单字段多、有联动 | 定位input/textarea填充 |
| 选择分类/品牌 | 下拉框、级联选择 | 点击+等待+选择 |
| 提交审核 | 需要触发前端校验 | 点击提交按钮 |

### 适合API的操作
| 操作 | 原因 | 实现方式 |
|------|------|----------|
| 图片上传 | 大文件传输 | POST multipart/form-data |
| 方案配置 | 批量数据提交 | POST JSON |
| 获取商品列表 | 数据查询 | GET with params |
| 修改商品状态 | 简单数据更新 | PUT/PATCH |

## 4. 核心流程设计

```
┌─────────────────────────────────────────────────────────────┐
│                     混合方案核心流程                          │
└─────────────────────────────────────────────────────────────┘

1. 初始化阶段
   ├─ 连接浏览器 (CDP)
   ├─ 检查登录状态
   └─ 提取认证信息 (cookies, token)

2. 基础信息填写 (浏览器)
   ├─ 导航到发布页面
   ├─ 填写商品名称、描述
   ├─ 选择分类、品牌
   └─ 填写基础参数

3. 图片上传 (API)
   ├─ 从浏览器获取上传接口
   ├─ 批量上传图片
   └─ 获取图片URL列表

4. 方案配置 (混合)
   ├─ 浏览器：点击"添加方案"
   ├─ API：提交方案数据
   └─ 浏览器：确认方案显示

5. 提交审核 (浏览器)
   ├─ 触发前端校验
   ├─ 点击提交按钮
   └─ 等待提交结果
```

## 5. 关键技术点

### 5.1 会话共享
```python
# 从浏览器提取认证信息
cookies = await page.context.cookies()
headers = await page.evaluate('''() => {
    return {
        'Authorization': localStorage.getItem('token'),
        'X-User-Id': localStorage.getItem('userId')
    }
}''')

# 创建API会话
session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])
session.headers.update(headers)
```

### 5.2 API接口发现
```python
# 监听网络请求，提取API端点
await page.route('**/*', lambda route: capture_api(route))

def capture_api(route):
    if '/api/' in route.request.url:
        api_endpoints[route.request.method].append({
            'url': route.request.url,
            'headers': route.request.headers,
            'body': route.request.post_data
        })
    route.continue_()
```

### 5.3 图片上传优化
```python
# 并发上传多张图片
async def upload_images(images, session):
    tasks = []
    for img in images:
        task = upload_single_image(img, session)
        tasks.append(task)
    return await asyncio.gather(*tasks)
```

## 6. 错误处理策略

### 浏览器操作失败
- 重试机制：最多3次
- 截图保存：失败时保存现场
- 降级方案：切换到纯浏览器模式

### API调用失败
- 状态码检查：401重新登录，5xx重试
- 超时处理：图片上传超时30s
- 回退机制：API失败时用浏览器上传

## 7. 性能优化

| 优化点 | 方法 | 预期提升 |
|--------|------|----------|
| 图片上传 | API并发上传 | 5张图从50s降到15s |
| 方案配置 | API批量提交 | 3个方案从30s降到5s |
| 页面等待 | 智能等待策略 | 减少30%等待时间 |

## 8. 依赖关系

```
混合方案
├─ 依赖：方案1的API逆向结果
│  ├─ 图片上传接口
│  ├─ 方案配置接口
│  └─ 认证机制
├─ 依赖：现有浏览器脚本
│  └─ CDP连接、iframe处理
└─ 新增：会话管理模块
```

## 9. 可行性评估

### 技术可行性：⭐⭐⭐⭐☆ (4/5)
- ✅ Playwright CDP连接已验证
- ✅ 会话共享技术成熟
- ⚠️ API接口需要逆向分析
- ⚠️ 反爬虫机制未知

### 实施难度：⭐⭐⭐☆☆ (3/5)
- 中等难度
- 需要前后端协同调试
- 错误处理较复杂

### 维护成本：⭐⭐⭐☆☆ (3/5)
- API接口可能变化
- 需要定期更新
- 但比纯浏览器方案稳定

## 10. 风险与限制

### 主要风险
1. **API接口未公开**：需要逆向分析，可能被封禁
2. **认证机制复杂**：token刷新、签名算法
3. **接口变更**：后台升级导致接口失效

### 限制条件
1. **必须先完成方案1**：API逆向是前置条件
2. **需要保持浏览器打开**：CDP连接依赖
3. **单账号限制**：多账号需要多浏览器实例

## 11. 下一步行动

### 如果API逆向成功
1. 实现会话共享模块
2. 封装图片上传API
3. 封装方案配置API
4. 集成到混合脚本

### 如果API逆向失败
1. 记录失败原因
2. 评估纯浏览器方案
3. 考虑OCR+RPA方案
4. 向大哥汇报决策建议

## 12. 成功标准

- [ ] 完整发布一个商品（3个方案+5张图）
- [ ] 总耗时 < 2分钟
- [ ] 成功率 > 95%
- [ ] 错误可自动恢复
