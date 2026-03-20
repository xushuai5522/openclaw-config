# 人人租API逆向工程进展报告

## 项目目标
用纯requests实现人人租商品发布，完全脱离浏览器自动化。

## 当前进展

### ✅ 已完成

1. **项目结构搭建**
   - 创建项目目录：`/Users/xs/.openclaw/workspace/projects/rrz-api-hunter/`
   - 准备抓包工具和测试脚本

2. **Token获取**
   - 从保存的cookie中提取到关键token：
     - `Data-Token: 7c6335b111cc755e`
     - `RRZUJI_SE: kk0n0pk88qiga51iplsdgjm1q9`

3. **API端点探索**
   - 测试了多个可能的API基础URL
   - 确认 `https://go-micro.rrzu.com` 是真实的API服务器
   - 但具体的端点路径需要通过抓包确认

### 🔄 进行中

**需要实际抓包获取真实API调用**

由于盲测API端点全部返回404，必须通过实际操作页面来捕获真实的API请求。

### 📋 抓包方案

已准备3种抓包方案：

#### 方案1：浏览器控制台注入（推荐）
**文件**: `api_interceptor.js`

**使用步骤**：
1. 打开浏览器，访问 https://admin.rrzu.com
2. 登录账号：15162152584 / 152584
3. 按F12打开开发者工具，切换到Console标签
4. 复制 `api_interceptor.js` 的全部内容，粘贴到控制台并回车
5. 在页面中执行以下操作：
   - 点击"商品管理" -> "商品列表"（获取列表API）
   - 点击"发布商品"（获取创建API）
   - 上传一张图片（获取上传API）
   - 填写表单并提交（获取提交API）
6. 操作完成后，在控制台运行：`exportApiLog()`
7. 会自动下载JSON文件，包含所有API调用记录

**优点**：
- 最简单，不需要额外工具
- 实时显示API调用
- 自动记录请求和响应

#### 方案2：Playwright CDP抓包
**文件**: `api_hunter.py`

**使用步骤**：
1. 确保浏览器CDP已启动（端口18800）
2. 在浏览器中打开 https://admin.rrzu.com 并登录
3. 运行：`python3 api_hunter.py`
4. 在浏览器中操作页面
5. 按Ctrl+C停止，自动生成分析报告

**优点**：
- 自动生成分析报告
- 可以捕获所有网络请求
- 适合长时间监控

#### 方案3：浏览器DevTools手动导出
**最传统的方法**：
1. F12 -> Network标签
2. 操作页面
3. 右键请求 -> Copy -> Copy as cURL
4. 或者直接查看请求详情

### 🎯 下一步行动

**需要大哥协助**：
1. 选择一种抓包方案（推荐方案1）
2. 在浏览器中执行操作并导出API日志
3. 将日志文件发给我

**我会立即**：
1. 分析API端点和参数格式
2. 编写纯requests实现
3. 测试完整的发布流程
4. 交付可用的API脚本

### 📁 项目文件清单

```
/Users/xs/.openclaw/workspace/projects/rrz-api-hunter/
├── README.md                    # 本文档
├── api_interceptor.js           # 浏览器控制台注入脚本（推荐）
├── api_hunter.py                # Playwright抓包工具
├── test_api.py                  # API端点测试脚本
├── test_real_api.py             # 真实API测试脚本
└── captured/                    # 抓包结果目录（待生成）
```

### 🔍 已知信息

**后台信息**：
- 主站：https://admin.rrzu.com
- iframe域名：admin-vue.rrzu.com
- API服务器：https://go-micro.rrzu.com
- 账号：15162152584 / 152584

**关键API（待确认具体路径）**：
- 登录接口
- 商品列表：`/product/Spu/list` (?)
- 创建商品：`/product/Spu/create` (?)
- 更新商品：`/product/Spu/update` (?)
- 图片上传：`/upload/image` (?)

**鉴权方式**：
- Cookie: `Data-Token=xxx; RRZUJI_SE=xxx`
- 可能还需要其他请求头

### ⏱️ 预计完成时间

- 获取API日志：10分钟（需要大哥操作）
- 分析并编写代码：30分钟
- 测试验证：20分钟
- **总计：约1小时**

---

## 快速开始（推荐）

```bash
# 1. 打开浏览器控制台脚本
cat /Users/xs/.openclaw/workspace/projects/rrz-api-hunter/api_interceptor.js

# 2. 复制输出的内容，粘贴到浏览器控制台

# 3. 操作页面后运行
exportApiLog()

# 4. 将下载的JSON文件放到项目目录
# 5. 通知我继续分析
```

---

**状态**：等待API日志数据
**阻塞点**：需要实际操作页面来捕获API调用
**建议**：使用方案1（浏览器控制台注入），最快最简单
