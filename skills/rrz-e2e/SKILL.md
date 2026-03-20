---
name: rrz-e2e
description: 人人租商品上架一体化流程（设备价值定价 + 主图/描述图双上传 + 草稿保存 + 提交审核 + 列表回查）。当用户说"继续上架""一键上架""跑完整流程""别分步骤"时使用。
---

# rrz-e2e

## 原子流程（固定顺序，不可跳步）

1. **获取商品锁** → `scripts/e2e_runtime.py lock <商品ID>`
2. 读取项目状态：`projects/rrz.md` 与 `registry/playbooks.json`
3. **加载/初始化幂等状态** → `scripts/e2e_runtime.py init <商品ID> [resume]`
4. 登录与页面状态确认：关闭异常弹窗，截图确认当前是新建/编辑态
5. 设备价值定价：
   - 运行：`python3 skills/rrz-publish/scripts/rrz_pricing.py <设备价值>`
   - 使用结果回填押金、购买价、各租期价格
   - **完成后** → `scripts/e2e_runtime.py done <商品ID> pricing`
6. 图片上传（两路都必须）
   - 主图：`.add-btn-wrap`
   - 描述图：`.desc-add-btn-wrap`
   - 若上传异常：移除 `webkitdirectory/directory` 再上传
   - **完成后** → `scripts/e2e_runtime.py done <商品ID> images`
7. 商品描述与关键信息补齐（标题、型号一致、禁止词检查）
   - **完成后** → `scripts/e2e_runtime.py done <商品ID> info`
8. 保存草稿 + 回读验证（截图/字段状态）
   - **完成后** → `scripts/e2e_runtime.py done <商品ID> draft`
9. 提交审核
   - **提交前**检查 step 状态，若 `submit` 已完成则跳过
   - **完成后** → `scripts/e2e_runtime.py done <商品ID> submit`
10. 列表回查（最终成功判定，见下方 L3）
    - **完成后** → `scripts/e2e_runtime.py done <商品ID> verify`
11. **释放商品锁** → `scripts/e2e_runtime.py unlock <商品ID>`

## 六条加固规则

### 1. 商品级锁（防并发）
- 每个商品 ID 同一时刻只允许一个写者
- 锁文件：`/tmp/rrz_lock_<商品ID>.lock`（flock 排他锁）
- 锁超时 30 分钟自动释放（防死锁）
- 主会话与子会话操作同一商品时，后者获取锁失败应等待或报告

### 2. 重试上限 + 熔断（防死循环）
- 单步最大重试 3 次，指数退避（1s → 2s → 4s）
- 连续 3 步失败触发熔断：暂停流程，保存当前状态，报告大哥
- 熔断后需人工确认才能继续（`scripts/e2e_runtime.py reset-breaker <商品ID>`）

### 3. 动态超时（防误报）
- 图片上传：基础 30s + 每张额外 10s
- 页面加载：15s（首次）/ 8s（后续）
- 表单保存：20s
- 超时不立即判定失败，先截图 + 再等一轮（共 2 轮），仍超时才标记失败

### 4. 幂等 step_id（防重复动作）
- 每步有唯一 step_id：`pricing / images / info / draft / submit / verify`
- 状态文件记录每步完成时间戳
- 断线重跑时先读状态，已完成的步骤直接跳过
- 状态文件路径：`/tmp/rrz_state_<商品ID>.json`

### 5. 播报策略（里程碑 + 异常即时）
- **里程碑播报**：定价完成、图片上传完成、草稿保存成功、审核提交成功、列表回查通过
- **异常即时播报**：任何步骤失败、熔断触发、锁冲突
- **去重**：同类错误 5 分钟内只报一次（聚合计数）

### 6. 成功判定分层
- **L1**：页面值回读（字段值与预期一致）
- **L2**：草稿/提交成功提示（toast + 页面状态变化）
- **L3**：列表页回查状态（最终业务成功以此为准）
- 仅 toast 不可靠，必须至少达到 L1；最终以 L3 为准

## 状态持久化
- 原子写：先写 tmp 文件，再 rename（防写坏）
- 每次写入带版本号 + 内容哈希
- 异常恢复时校验哈希，不匹配则从最近有效快照恢复

## 强约束（保留）
- 只上传主图不算完成，必须有描述图
- 提交后未回查到状态变化，禁止重复新建
- DOM 改值不等于保存成功；必要时写 Vue 数据层并再验证

## 失败切换（保留）
- browser 普通点击失败 1-2 次，切截图定位 + 鼠标模拟
- 仍失败则回退到"保存草稿 + 回查"，避免脏提交

## 图片上传方案（已验证 2026-03-20）

### 原理
人人租使用自研 OSS SDK（`rrzuOssSdkUmd.js`），上传流程：
1. `GET /file/oss/token?project=shop-admin&file_type=2` → 获取 AES 加密的 OSS 凭证
2. SDK 用 cookie 中的密钥解密 → 得到 `{host, policy, access_id, signature, dir, token, url}`
3. `POST {host}` FormData 上传到阿里云 OSS
4. CDN 地址：`https://img1.rrzuji.cn/{path}`

### 使用方法
在 iframe[name=rrzuji] 内执行 `scripts/rrz_upload.js` 注入上传函数，然后：

```javascript
// 单张上传
const {done, url} = await window.rrzUploadOne(base64String, 'jpg');

// 批量上传
const {done, urls} = await window.rrzUpload([b64_1, b64_2], 'image', 'jpg');
```

### 上传后写入 Vue 数据层
主图上传后需要写入 formData：
```javascript
// 找到 Vue 实例
const vm = findFormVue(document.body, 0);
// 主图
vm.$data.formData.picList = [{url: 'https://img1.rrzuji.cn/...'}];
// 描述图
vm.$data.formData.descPicList = [{url: 'https://img1.rrzuji.cn/...'}];
```

### 关键约束
- 必须在 iframe 内执行（跨域限制）
- 依赖页面已加载的 `createUploader` SDK
- 需要有效的 `Go-Token` cookie（已登录状态）
- 主图和描述图都必须上传，缺一不可

## 运行时脚本
- `scripts/e2e_runtime.py` — 锁管理、幂等状态、熔断控制、告警去重
- `scripts/rrz_upload.js` — 图片上传（注入 iframe 使用）
- 用法见脚本 `--help` 或脚本内注释
