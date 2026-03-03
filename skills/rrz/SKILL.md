---
name: rrz
description: 人人租商家后台运营工具箱。商品管理、审核修复、状态监控。当用户提到人人租、商品上架、审核修改、套餐管理时激活此技能。
---

# 人人租运营工具箱


## 快速参考
- **触发词**: 人人租、商品管理、审核修复
- **核心功能**: 运营工具箱、状态监控
- **后台**: https://admin.rrzu.com

---

## 基础信息

| 项目 | 值 |
|------|-----|
| 后台地址 | https://admin.rrzu.com |
| 商品列表 | https://admin.rrzu.com/spu-view/list |
| 账号 | 15162152584 |
| 密码 | 152584 |
| 店铺 | 书电马数码店 |
| iframe名称 | rrzuji |
| iframe域名 | admin-vue.rrzu.com |

## 页面结构

人人租后台使用 **主页面 + iframe** 架构：
- 主页面：`admin.rrzu.com`（导航栏、侧边栏）
- 商品操作区：`iframe[name=rrzuji]`（来自 `admin-vue.rrzu.com`）
- **跨域限制**：无法用JS从主frame访问iframe内容
- **操作方式**：用 browser snapshot（会自动穿透iframe）+ act 来操作

## 常见弹窗处理

每次进入后台都可能弹出以下弹窗，必须先关闭：

1. **经营地址信息补充** — 点击"跳过"或"确认"
2. **方案应用邀请** — 点击关闭按钮
3. **工单提醒** — 点击"×"关闭

处理方式：
```
browser evaluate: document.querySelectorAll('button').forEach(b => { if(b.textContent.includes('跳') || b.textContent.includes('确认')) b.click() })
```

## 审核规则（平台要求）

### 标题规则
- 格式：`90新 + 品牌 + 型号 + 商品特点`
- 示例：`90新 红蜘蛛 校色仪Pro X2 色彩校准`
- 必须包含具体产品型号

### 禁止词
| 禁止词 | 替换为 |
|--------|--------|
| 租赁 | 租用 |
| 出租 | 提供使用 |
| 免押 | （删除） |
| 免息 | （删除） |
| 分期 | （删除） |
| 最/最便宜/最低价 | （删除） |

### 套餐规则
- 套餐名称必须是租用方式：租完归还、可归还、到期可归还/续租、随租随还
- 不能用"租赁"相关字眼
- 规格表头应为"型号"或"参数"或"配置"，不能是"套餐"

### 图片规则
- 纯白底色 #FFFFFF
- 600x600px 以上（推荐800x800）
- 主图禁止文字（品牌Logo/型号刻字除外）
- 3-5张主图

## 工作流

### 1. 列出审核不通过的商品

```
步骤：
1. 导航到商品列表页
2. 关闭弹窗
3. 用 snapshot 获取 iframe 内容
4. 找到状态为"审核不通过"的商品
5. 记录：商品ID、名称、不通过原因
```

### 2. 修复审核不通过的商品

```
步骤：
1. 在商品列表找到目标商品
2. 点击"修改商品"按钮（在iframe内，用snapshot找ref）
3. 等待新标签页打开（URL格式：/spu-view/create?id=xxx）
4. 在编辑页面中：
   a. 修改标题（添加型号、去除禁止词）
   b. 修改套餐名称（租赁→租用）
   c. 修改描述（去除禁止词）
   d. 修改规格表头（套餐→型号/配置）
5. 点击"提交审核"
6. 确认提交
7. 关闭编辑标签页，回到列表页
```

### 3. 发布新商品

```
步骤：
1. 准备好图片（白底800x800）
2. 导航到发布商品页面
3. 选择类目
4. 填写标题（按规则）
5. 上传图片
6. 设置套餐（租期/价格/押金）
7. 填写描述
8. 提交审核
```

## 辅助脚本

### scripts/rrz_helper.py

用于Playwright直接操作iframe内的元素（browser工具有时不稳定时的备选方案）。

使用方式：
```bash
python3 scripts/rrz_helper.py list          # 列出审核不通过商品
python3 scripts/rrz_helper.py click-edit 17513  # 点击修改按钮
python3 scripts/rrz_helper.py replace-text      # 替换当前编辑页的禁止词
python3 scripts/rrz_helper.py submit            # 提交审核
```

## 常见审核不通过原因及修复方案

### 原因1：标题必须包含具体产品型号
修复：在标题中添加完整型号
示例：`校色仪校色技术支持-仅使用` → `90新 红蜘蛛 校色仪Pro 校色技术支持`

### 原因2：套餐内需要写明具体租用方式
修复：套餐名改为标准租用方式
示例：`套餐1` → `租完归还` / `到期可归还`

### 原因3：删除套餐中的租赁字眼
修复：全文搜索替换 租赁→租用

### 原因4：销售规格表头标题填写有误
修复：将"套餐"改为"型号"或"配置"

### 原因5：商品标题型号与描述型号不一致
修复：统一标题和描述中的型号文字

### 原因6：请增加一个套餐规格
修复：添加新的套餐（如不同租期选项）

## 浏览器操作注意事项

1. 商品列表在 iframe(name=rrzuji) 中，用 snapshot 会自动穿透
2. 点击"修改商品"会打开新标签页（URL: /spu-view/create?id=xxx）
3. 编辑页面也有 iframe，同样用 snapshot 穿透
4. 每次操作前先 screenshot 确认当前状态
5. 提交前必须截图确认修改内容
6. 提交后等待2秒再截图确认状态
7. 操作完关闭多余标签页，保持标签页 <= 3个

## 辅助脚本

脚本位置：`skills/rrz/scripts/`

### rrz_helper.py
Playwright直连CDP操作iframe，用于browser工具不稳定时的备选方案。

```bash
python3 skills/rrz/scripts/rrz_helper.py list           # 列出审核不通过商品
python3 skills/rrz/scripts/rrz_helper.py click-edit ID   # 点击修改按钮
python3 skills/rrz/scripts/rrz_helper.py replace-text    # 替换禁止词
python3 skills/rrz/scripts/rrz_helper.py submit          # 提交审核
```
