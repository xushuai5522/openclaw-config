---
name: rrz-e2e
description: 人人租商品上架一体化流程（设备价值定价 + 主图/描述图双上传 + 草稿保存 + 提交审核 + 列表回查）。当用户说"继续上架""一键上架""跑完整流程""别分步骤"时使用。
---

# rrz-e2e

## 原子流程（固定顺序，不可跳步）

1. **获取商品锁** → `scripts/e2e_runtime.py lock <商品ID>`
2. 读取项目状态：`projects/rrz.md`、`projects/rrz-workflow-v1.md`、`projects/rrz-blockers.md`、`projects/rrz-platform-rules.md`
3. **加载/初始化幂等状态** → `scripts/e2e_runtime.py init <商品ID> [resume]`
4. 登录与页面状态确认：关闭异常弹窗，截图确认当前是新建/编辑态
5. 设备价值定价：
   - 运行：`python3 skills/rrz-publish/scripts/rrz_pricing.py <设备价值>`
   - 使用结果回填押金、购买价、各租期价格
   - **完成后** → `scripts/e2e_runtime.py done <商品ID> pricing`
6. 图片上传（两路都必须）
   - 主图：`.add-btn-wrap`
   - 描述图：`.desc-add-btn-wrap`
   - **完成后** → `scripts/e2e_runtime.py done <商品ID> images`
7. 商品描述与关键信息补齐（标题、型号一致、禁词检查）
   - **完成后** → `scripts/e2e_runtime.py done <商品ID> info`
8. **规则校验 gate（新增，未通过禁止提审）**
   - **完成后** → `scripts/e2e_runtime.py done <商品ID> gate`
9. 保存草稿 + 回读验证（截图/字段状态）
   - **完成后** → `scripts/e2e_runtime.py done <商品ID> draft`
10. 提交审核
   - **提交前**检查 step 状态，若 `submit` 已完成则跳过
   - **完成后** → `scripts/e2e_runtime.py done <商品ID> submit`
11. 列表回查（最终成功判定，见下方 L3）
   - **完成后** → `scripts/e2e_runtime.py done <商品ID> verify`
12. **释放商品锁** → `scripts/e2e_runtime.py unlock <商品ID>`

---

## 提审前规则校验 gate（强制）

> 这一步是**文档约束**：凡是要 submit，必须先显式完成规则校验 gate。
> gate 失败时，允许“保存草稿”，**不允许提审**。

### Gate 必查项

#### A. 平台硬规则
- [ ] 标题符合：`成色 + 品牌 + 型号 + 使用场景`
- [ ] 标题含具体型号
- [ ] 标题型号 = 描述型号 = 商品实际型号
- [ ] 套餐名为平台认可的租用方式模板
- [ ] 规格表头不是“套餐”
- [ ] 标题/套餐/描述无已知禁表述（如 `租赁` 等）
- [ ] 已有主图
- [ ] 已有描述图
- [ ] 商品描述满足“包含图片”要求

#### B. 执行读回验证
- [ ] 价格/押金/购买价已读回
- [ ] 主图字段读回非空
- [ ] 描述图字段读回非空
- [ ] 标题最终值读回正确

### Gate 失败处理
1. 记录失败项清单
2. 截图 + 保存当前字段快照
3. 允许停在草稿态修复
4. **禁止继续 submit**

---

## 六条加固规则

### 1. 商品级锁（防并发）
- 每个商品 ID 同一时刻只允许一个写者
- 锁文件：`/tmp/rrz_lock_<商品ID>.lock`
- 锁超时 30 分钟自动释放

### 2. 重试上限 + 熔断（防死循环）
- 单步最大重试 3 次，指数退避（1s → 2s → 4s）
- 连续 3 步失败触发熔断

### 3. 动态超时（防误报）
- 图片上传：基础 30s + 每张额外 10s
- 页面加载：15s（首次）/ 8s（后续）
- 表单保存：20s

### 4. 幂等 step_id（防重复动作）
- step_id：`pricing / images / info / gate / draft / submit / verify`
- 状态文件路径：`/tmp/rrz_state_<商品ID>.json`
- 已完成步骤直接跳过

### 5. 播报策略（里程碑 + 异常即时）
- 里程碑：定价完成、图片完成、gate 通过、草稿成功、提交成功、列表回查通过
- 异常：任何失败、熔断、锁冲突

### 6. 成功判定分层
- **L1**：页面值回读正确
- **L2**：草稿/提交提示成功
- **L3**：列表页回查状态变化
- 最终业务成功以 **L3** 为准

---

## 强约束（保留）
- 只上传主图不算完成，必须有描述图
- 提交后未回查到状态变化，禁止重复新建
- DOM 改值不等于保存成功；必要时写 Vue 数据层并再验证
- 禁止把历史经验规则写成平台硬规则
- 提审前必须先过 `projects/rrz-platform-rules.md` 对应的硬规则检查

---

## 图片上传方案（已验证）

### 原理
人人租使用自研 OSS SDK（`rrzuOssSdkUmd.js`），上传流程：
1. `GET /file/oss/token?project=shop-admin&file_type=2`
2. SDK 解密 OSS 凭证
3. `POST {host}` 上传到阿里云 OSS
4. 返回 CDN 地址

### 使用方法
在 iframe[name=rrzuji] 内执行 `scripts/rrz_upload.js`：

```javascript
const {done, url} = await window.rrzUploadOne(base64String, 'jpg');
```

### 关键约束
- 必须在 iframe 内执行
- 依赖页面已加载的 `createUploader` SDK
- 主图和描述图都必须上传，缺一不可

---

## 运行时脚本
- `scripts/e2e_runtime.py` — 锁管理、幂等状态、熔断控制、告警去重、gate 状态落盘 / submit 放行检查
- `scripts/rrz_upload.js` — 图片上传（注入 iframe 使用）
- `scripts/rrz_vue_locate.js` — 动态定位商品信息 model / `sellTableData`
- `scripts/rrz_gate.js` — 提审前规则 gate，输出 pass / warning / block 报告
- `scripts/rrz_submit_atomic.js` — 原子写值 + gate 校验 + 草稿/提审动作
- `scripts/rrz_capture_state.js` — 失败证据抓取（含最近一次 gate 报告）
