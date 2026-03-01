# 人人租商品上架技能

## 描述
人人租平台商品上架全流程自动化，包括：图片处理、定价计算、商品创建、审核提交、审核不通过修改。

## 触发条件
用户提到：上架商品、人人租上架、发布商品、提交审核

## 前置条件
- 浏览器已登录人人租后台 https://admin.rrzu.com
- CDP端口 http://127.0.0.1:18800 可连接
- 商品图片已准备好（或提供商品关键词用于爬图）

## 平台信息
| 项目 | 值 |
|------|-----|
| 后台地址 | https://admin.rrzu.com |
| 店铺 | 书电马数码店 |
| API基础URL | https://go-micro.rrzu.com |
| iframe名称 | rrzuji |
| Token获取 | `document.cookie.match(/Go-Token=([^;]+)/)?.[1]` |

---

## 完整上架流程

### 第1步：图片准备

#### 图片要求
- 尺寸：600x600px及以上，正方形
- 背景：纯白色 RGB(255,255,255)
- 禁止：商家logo、水印、电话、微信等联系方式
- 第一张图必须为浅白色底图
- 商品内容居中，四边适当留白

#### 白底处理代码
```python
from PIL import Image
import numpy as np

img = Image.open('input.jpg')
arr = np.array(img)

# 接近白色的像素强制纯白（阈值>240）
mask = np.all(arr[:,:,:3] > 240, axis=2)
arr[mask] = [255, 255, 255]

# 浅灰色区域也处理（>220且色差<15）
gray_mask = np.all(arr[:,:,:3] > 220, axis=2) & (np.max(arr[:,:,:3], axis=2) - np.min(arr[:,:,:3], axis=2) < 15)
arr[gray_mask] = [255, 255, 255]

out = Image.fromarray(arr)
out.save('output.jpg', 'JPEG', quality=98)
```

### 第2步：定价计算

#### 通用定价规则
```
设备成本 = 闲鱼中位数（去除最低10%）
基础月租 = 设备价值 × 15%
押金 = 设备价值 × 80%
```

#### 租期阶梯
| 租期 | 计算方式 |
|------|----------|
| 1天 | 月租/30 × 1.8（短租溢价） |
| 3天 | 月租/30 × 1.5 × 3 |
| 7天 | 月租 × 60% |
| 30天 | 月租 |
| 90天 | 月租×3 × 95折 |
| 180天 | 月租×6 × 9折 |
| 365天 | 月租×12 × 85折 |
| 730天 | 月租×24 × 80折 |
| 1095天 | 月租×36 × 75折 |

#### 双方案
- 方案一（到期须归还）：基础价格
- 方案二（到期可归还/续租）：基础价格 × 1.15

#### 运费规则
| 租期总租金 | 寄送 | 归还 |
|-----------|------|------|
| ≤¥300 | ❌ | ❌ |
| ¥301-500 | ✅ | ❌ |
| ¥501-800 | ✅ | ❌ |
| >¥800 | ✅ | ✅ |

### 第3步：创建商品（API方式）

#### 3.1 获取Token
```javascript
// 在iframe rrzuji中执行
const token = document.cookie.match(/Go-Token=([^;]+)/)?.[1]
```

#### 3.2 创建SPU
```
POST https://go-micro.rrzu.com/product/Spu/create
Headers: Authorization: {token}, Content-Type: application/json
```

#### 3.3 关键字段
```json
{
  "name": "90新 {品牌} {型号} {功效描述}",
  "category_id": "类目ID",
  "sku": [
    {
      "rental": [
        {"days": 1, "total_rental": "xx", "rental": "xx"},
        ...
      ],
      "deposit": "押金"
    }
  ]
}
```

#### 标题规范
- 格式：`90新 + 品牌 + 型号 + 功效描述`
- 必须包含功效描述词（如"高性能"、"轻薄便携"）
- 禁止词：免押、免息、分期、最、最便宜、测试

### 第4步：上传图片到素材中心

⚠️ 页面有两个图片上传区域，必须分别上传！

#### 4.1 商品主图（spu_picture）
- 上传按钮：`.add-btn-wrap`
- 对应字段：`spu_picture`
- 用途：商品列表展示的主图

#### 4.2 描述图片（detail_picture）— 关键！
- 上传按钮：**`.desc-add-btn-wrap`**
- 对应字段：`detail_picture`（前端formData中叫`descPicList`）
- 用途：商品详情描述中的图片
- ⚠️ **不上传这个会导致"商品描述需要包含图片"错误！**

#### 上传流程（两个区域相同）
1. 进入编辑页面 → 切到"商品信息"tab
2. 点击 `.add-btn-wrap`（+ 上传图片）
3. 弹出素材中心选择器
4. 点击"上传文件"按钮
5. **关键**：去掉file input的`webkitdirectory`属性
   ```javascript
   const input = document.querySelector('input[type="file"]');
   input.removeAttribute('webkitdirectory');
   input.removeAttribute('directory');
   ```
6. 用Playwright `set_input_files()` 上传图片
7. 等待上传完成 → 点击"确定"
8. 进入 `test_upload_images` 文件夹找到新图片
9. 选中图片 → 点击"确定"

### 第5步：填写商品描述

⚠️ 商品描述必须包含图片，纯文字会被拒绝！
⚠️ 后端检查的是 `detail_picture` 字段，不是 description 里的 `<img>` 标签！

#### 设置描述图片（关键！）

前端Vue formData中：
- `descPicList` → 提交时映射为 `detail_picture`
- `description` → 描述HTML文本

```javascript
function findFormVue(el, depth) {
    if (depth > 10) return null;
    if (el.__vue__) {
        const data = el.__vue__.$data || {};
        if (data.formData && 'description' in data.formData) return el.__vue__;
    }
    for (const child of el.children) { const r = findFormVue(child, depth + 1); if (r) return r; }
    return null;
}

const vm = findFormVue(document.body, 0);
const fd = vm.$data.formData;

// ✅ 必须设置descPicList（映射为detail_picture）
fd.descPicList = [
    {url: 'https://img1.rrzuji.cn/...'},
    {url: 'https://img1.rrzuji.cn/...'}
];

// 同时设置description文本
fd.description = '<img src="url1"/><img src="url2"/>';
```

#### 设置富文本编辑器（关键！）

⚠️ **直接操作DOM的innerHTML不会同步到表单数据！必须通过Vue实例设置。**

```javascript
// ❌ 错误方式 - innerHTML不会同步到formData
const editor = document.querySelector('.w-e-text');
editor.innerHTML = html;  // 提交时description为空！

// ✅ 正确方式 - 通过Vue实例设置formData.description
function findFormVue(el, depth) {
    if (depth > 10) return null;
    if (el.__vue__) {
        const data = el.__vue__.$data || {};
        if (data.formData && 'description' in data.formData) return el.__vue__;
    }
    for (const child of el.children) {
        const r = findFormVue(child, depth + 1);
        if (r) return r;
    }
    return null;
}

const vm = findFormVue(document.body, 0);
vm.$data.formData.description = descHtml;

// 同时设置editorContent和DOM（保持UI同步）
function findEditorVue(el, depth) {
    if (depth > 10) return null;
    if (el.__vue__) {
        const data = el.__vue__.$data || {};
        if ('editorContent' in data) return el.__vue__;
    }
    for (const child of el.children) {
        const r = findEditorVue(child, depth + 1);
        if (r) return r;
    }
    return null;
}
const editorVm = findEditorVue(document.body, 0);
if (editorVm) editorVm.$data.editorContent = descHtml;

const editor = document.querySelector('.w-e-text');
if (editor) editor.innerHTML = descHtml;
```

### 第6步：提交审核

点击"提交审核"按钮，或通过API：
```
POST https://go-micro.rrzu.com/product/Spu/update
Body: { ...spu_data, status: 1 }
```

### 第7步：审核不通过修改

#### 审核打回历史记录

**第1次打回（2026-02-25）：**
- 标题：需要描述商品主要功效，"迷你主机"仅描述产品类型
- 图片：背景存在浅灰色区域，不符合纯白色要求

**第2次打回（2026-02-25）：**
- 标题：加了"高性能"仍不通过，审核认为这是泛泛描述
- 图片：背景仍有浅灰色（旧图片未被替换）

**第4次提交失败（2026-02-25）：**
- 页面显示"提交成功"但API status仍为0（草稿）
- 原因：直接跳到"商品信息"tab修改，没有按步骤走完
- 教训：必须从第一步开始，每步点"下一步"

**第5次提交失败（2026-02-25）：**
- 页面显示"提交成功"但API status仍为0（草稿）
- 原因：description为空！前端wangEditor的innerHTML修改不会同步到Vue formData
- 教训：必须通过Vue实例 `vm.$data.formData.description` 设置描述

**第6次提交失败（2026-02-25）：**
- description有内容但后端报"商品描述需要包含图片"
- 原因：后端检查的不是description里的`<img>`标签，而是`detail_picture`字段
- `detail_picture`为null → 失败

**第7次提交失败（2026-02-25）：**
- 直接设置formData.detail_picture无效，提交时仍为null
- 原因：前端formData用的字段名是`descPicList`，提交时映射为`detail_picture`

**第9次提交成功（2026-02-25）：**
- 发现页面有两个图片上传区域：`.add-btn-wrap`（商品主图）和 `.desc-add-btn-wrap`（描述图片）
- 之前一直只上传了商品主图，没上传描述图片 → `detail_picture`为空 → "商品描述需要包含图片"
- 通过`.desc-add-btn-wrap`上传描述图片后，`detail_picture`有值，提交成功
- 待审核列表确认有Mac mini ✅

#### 常见拒绝原因及修复
| 原因 | 修复方式 |
|------|----------|
| 标题缺少功效描述 | ❌ "高性能"不够 → ✅ 用具体场景如"办公设计开发" |
| 图片背景非纯白 | 阈值>220不够 → 用PNG格式避免JPEG压缩灰化，或阈值降到>200 |
| 商品描述无图片 | 描述中插入`<img>`标签 |
| 包含敏感词"测试" | 替换为"调试"或删除 |
| 包含"租赁"字眼 | 改为"租用" |

#### 标题规范（经验总结）
- ❌ `90新 苹果 Mac mini M4 迷你主机` — 缺功效
- ❌ `90新 苹果 Mac mini M4 高性能迷你主机` — "高性能"太泛
- ✅ `90新 苹果 Mac mini M4 办公设计开发迷你主机` — 具体场景
- ✅ `90新 苹果 Mac mini M4 视频剪辑编程办公迷你主机` — 多场景

**原则：标题功效词必须是具体使用场景，不能是形容词**

#### 提交流程（经验总结）
- ⚠️ **必须按步骤顺序走完**：基础信息→销售规格→支付信息→物流信息→商品信息→提交审核
- ❌ 直接跳到"商品信息"tab修改后提交 → 数据不会保存到后端
- ✅ 从第一步开始，每步点"下一步"走到最后再提交 → 数据正确保存
- 提交后必须通过API验证 `status: 1`（审核中）才算真正提交成功

#### 图片规范（经验总结）
- JPEG压缩会导致纯白(255)变成浅灰(242-254)
- **建议用PNG格式上传**，避免压缩灰化
- 如果必须JPEG，quality设为100
- 白底处理阈值从>220降到>200，覆盖更多灰色像素
- 上传后必须下载验证服务器上的实际图片

#### 修改流程
1. 商品列表 → 找到未通过商品 → 点击"修改商品"
2. 修改对应问题
3. 重新提交审核

---

## 关键注意事项

1. **弹窗处理**：页面经常弹出"方案应用邀请"弹窗，需要关闭
   ```javascript
   document.querySelectorAll('[class*="modal"]').forEach(m => m.style.display = 'none');
   document.querySelectorAll('[class*="mask"]').forEach(m => m.style.display = 'none');
   ```

2. **iframe操作**：所有表单操作都在 `name='rrzuji'` 的iframe中

3. **API vs 前端**：
   - 价格/标题/基础信息 → API直接修改
   - 图片上传 → 必须通过前端素材中心
   - 商品描述 → 前端wangEditor
   - 提交审核 → 前端按钮或API

4. **状态限制**：已提交审核的商品不能直接API更新，需要先在前端"修改商品"

5. **代理分成**：默认20%

## 定价计算脚本

参考 `scripts/rrz_pricing.py`（如需创建）：
```python
def calculate_pricing(device_value):
    monthly = round(device_value * 0.15)
    deposit = round(device_value * 0.80)
    
    rental = [
        (1,    round(monthly/30 * 1.8)),
        (3,    round(monthly/30 * 1.5 * 3)),
        (7,    round(monthly * 0.60)),
        (30,   monthly),
        (90,   round(monthly * 3 * 0.95)),
        (180,  round(monthly * 6 * 0.90)),
        (365,  round(monthly * 12 * 0.85)),
        (730,  round(monthly * 24 * 0.80)),
        (1095, round(monthly * 36 * 0.75)),
    ]
    
    return {
        'deposit': deposit,
        'monthly': monthly,
        'rental_plan_1': [{'days': d, 'total': t, 'daily': round(t/d, 2)} for d, t in rental],
        'rental_plan_2': [{'days': d, 'total': round(t*1.15), 'daily': round(t*1.15/d, 2)} for d, t in rental],
    }
```
