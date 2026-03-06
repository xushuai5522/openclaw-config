# 人人租后台API文档

## 基础信息

- **Base URL**: `https://admin-vue.rrzu.com` (待确认)
- **协议**: HTTPS
- **数据格式**: JSON
- **鉴权方式**: (待分析)

---

## 1. 鉴权机制

### 登录
```
POST /api/auth/login
Content-Type: application/json

Request:
{
  "username": "string",
  "password": "string"
}

Response:
{
  "code": 0,
  "data": {
    "token": "string",
    "userInfo": {...}
  }
}
```

### Token使用方式
- Header: `Authorization: Bearer {token}` (待确认)
- 或 Cookie: `token={value}` (待确认)

---

## 2. 商品管理

### 2.1 获取商品列表
```
GET /api/products?page=1&size=20&status=all

Headers:
- Authorization: Bearer {token}

Response:
{
  "code": 0,
  "data": {
    "list": [...],
    "total": 100,
    "page": 1,
    "size": 20
  }
}
```

### 2.2 获取商品详情
```
GET /api/products/{id}

Response:
{
  "code": 0,
  "data": {
    "id": 123,
    "name": "商品名称",
    "images": [...],
    "description": "...",
    "plans": [...],
    ...
  }
}
```

### 2.3 创建商品
```
POST /api/products
Content-Type: application/json

Request:
{
  "name": "商品名称",
  "categoryId": 1,
  "images": ["url1", "url2"],
  "description": "商品描述",
  "specs": {...},
  "plans": [...]
}

Response:
{
  "code": 0,
  "data": {
    "id": 123,
    "status": "draft"
  }
}
```

### 2.4 更新商品
```
PUT /api/products/{id}
Content-Type: application/json

Request: (同创建商品)

Response:
{
  "code": 0,
  "message": "更新成功"
}
```

---

## 3. 图片上传

### 3.1 上传图片
```
POST /api/upload/image
Content-Type: multipart/form-data

Request:
- file: (binary)
- type: "product" (可选)

Response:
{
  "code": 0,
  "data": {
    "url": "https://cdn.rrzu.com/xxx.jpg",
    "id": "xxx"
  }
}
```

---

## 4. 方案配置

### 4.1 创建租赁方案
```
POST /api/products/{productId}/plans
Content-Type: application/json

Request:
{
  "name": "方案名称",
  "duration": 30,
  "price": 100.00,
  "deposit": 500.00,
  "stock": 10
}

Response:
{
  "code": 0,
  "data": {
    "planId": 456
  }
}
```

---

## 5. 审核流程

### 5.1 提交审核
```
POST /api/products/{id}/submit
Content-Type: application/json

Request:
{
  "note": "提交说明"
}

Response:
{
  "code": 0,
  "message": "提交成功，等待审核"
}
```

### 5.2 获取审核状态
```
GET /api/products/{id}/audit-status

Response:
{
  "code": 0,
  "data": {
    "status": "pending|approved|rejected",
    "reason": "审核不通过原因",
    "updatedAt": "2024-01-01 12:00:00"
  }
}
```

---

## 反爬机制分析

### 已发现的机制
1. **Token鉴权**: (待确认具体方式)
2. **时间戳**: (待确认是否需要)
3. **签名算法**: (待确认是否存在)
4. **User-Agent检测**: (待确认)
5. **频率限制**: (待测试)

### 应对策略
- 使用真实浏览器的User-Agent
- 保持合理的请求间隔
- 复用登录token
- 如有签名，需逆向JS代码

---

## 错误码

| Code | 说明 |
|------|------|
| 0    | 成功 |
| 401  | 未授权/token过期 |
| 403  | 无权限 |
| 404  | 资源不存在 |
| 500  | 服务器错误 |

---

## 待补充

- [ ] 确认实际的API base URL
- [ ] 分析鉴权token的获取和使用方式
- [ ] 测试各接口的必填字段
- [ ] 确认图片上传的具体格式要求
- [ ] 分析是否有请求签名
- [ ] 测试频率限制阈值
