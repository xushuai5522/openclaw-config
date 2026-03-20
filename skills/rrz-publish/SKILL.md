---
name: rrz-publish
description: 人人租商品发布规则与定价。标题生成、禁止词、定价计算、表单填写规则。当用户提到发布商品、上架、新品上架时激活。
---

# 人人租商品发布规则

> 职责：发布规则、定价计算、表单填写规范。
> 后台基础操作 → `rrz`；完整上架流程 → `rrz-e2e`。

## 定价计算

```bash
python3 skills/rrz-publish/scripts/rrz_pricing.py <设备价值>
```

| 项目 | 公式 |
|------|------|
| 基础月租 | 设备价值 × 15% |
| 押金 | 设备价值 × 80% |

### 租期阶梯

| 租期 | 计算 |
|------|------|
| 1天 | 月租/30 × 1.8 |
| 3天 | 月租/30 × 1.5 × 3 |
| 7天 | 月租 × 60% |
| 30天 | 月租 |
| 90天 | 月租×3 × 95折 |
| 180天 | 月租×6 × 9折 |
| 365天 | 月租×12 × 85折 |
| 730天 | 月租×24 × 80折 |
| 1095天 | 月租×36 × 75折 |

### 双方案
- 方案一（到期须归还）：基础价格
- 方案二（到期可归还/续租）：基础价格 × 1.15

### 运费规则

| 租期总租金 | 寄送 | 归还 |
|-----------|------|------|
| ≤¥300 | ❌ | ❌ |
| ¥301-500 | ✅ | ❌ |
| ¥501-800 | ✅ | ❌ |
| >¥800 | ✅ | ✅ |

## 标题生成

格式：`{成色} {品牌} {型号} {具体使用场景}`

场景必须是动词短语，不能是形容词：

| 品类 | ❌ 错误 | ✅ 正确 |
|------|---------|---------|
| 电脑/主机 | 高性能主机 | 办公设计开发主机 |
| 平板 | 大屏平板 | 学习网课办公平板 |
| 校色仪 | 专业校色仪 | 摄影后期色彩校准校色仪 |
| 数位屏 | 高端数位屏 | 绘画设计手绘数位屏 |
| 投影仪 | 智能投影仪 | 家用观影办公投影仪 |

## 表单填写顺序（不可跳步）

```
基础信息 → 销售规格 → 支付信息 → 物流信息 → 商品信息 → 提交审核
```

每步必须点"下一步"走到最后，跳步会导致数据不保存。

## 图片上传

### 两个上传入口
- 主图：`.add-btn-wrap`
- 描述图：`.desc-add-btn-wrap`（缺少会报错"商品描述需要包含图片"）

### 推荐方式（已验证）
在 iframe 内注入 `rrz-e2e/scripts/rrz_upload.js`，用 SDK 直传 OSS：
```javascript
const {done, url} = await window.rrzUploadOne(base64String, 'jpg');
```

### 写入 Vue 数据层
DOM 改值无效，必须通过 Vue 实例：
```javascript
// 找 formData 所在的 Vue 实例
function findFormVue(el, depth) {
    if (depth > 10) return null;
    if (el.__vue__) {
        const d = el.__vue__.$data || {};
        if (d.formData && 'description' in d.formData) return el.__vue__;
    }
    for (const child of el.children) {
        const r = findFormVue(child, depth + 1);
        if (r) return r;
    }
    return null;
}
const vm = findFormVue(document.body, 0);
vm.$data.formData.picList = [{url: 'https://img1.rrzuji.cn/...'}];
vm.$data.formData.descPicList = [{url: 'https://img1.rrzuji.cn/...'}];
vm.$data.formData.description = '<p>描述</p><img src="..."/>';
```

## 商品描述

后端检查的是 `detail_picture` 字段（由 `descPicList` 映射），不是 description 里的 `<img>`。

## 白底处理

```python
from PIL import Image
import numpy as np
img = Image.open('input.jpg')
arr = np.array(img)
mask = np.all(arr[:,:,:3] > 200, axis=2)
arr[mask] = [255, 255, 255]
Image.fromarray(arr).save('output.png')
```

上传后需下载验证，人人租会把 PNG 转 JPG，可能灰化。
