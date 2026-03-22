# MEMORY.md - 长期记忆（精简版）

> 职责：只保留长期有效结论与索引，不记录一次性过程。

> 只保留长期有效、启动必需的信息；细节下放到 `skills/`、`projects/`、`memory/`、`recent/`。

## 核心原则
1. 先查 `skills/`，不要重复造轮子。
2. 先尝试再求助，但不能卡死不回。
3. 任务必须可验证，拒绝“口头完成”。
4. 涉及配置/账号/外发，先确认再执行。
5. 发现重复错误要复盘并固化机制。

## 执行习惯
- 简洁直接，超时/卡住 30 秒内反馈。
- 可拆分耗时任务走独立通道，主代理负责调度与验收。
- 子代理失联/跑偏/无产出，立即止损接管。
- 会话重建或读完 memory 后，先识别断点并直接续到第一项待做，不重复向大哥索要已知信息。
- 涉及“官方产品 / 官方接入 / 官方安装”时，先核验来源；若官方性无法证实，停在核实阶段，不把社区壳包当官方方案落地。

## 环境索引
- OpenClaw：`/Users/xs/Documents/node-v24.14.0-darwin-x64/bin/openclaw`
- Workspace：`/Users/xs/.openclaw/workspace`
- 注意：非交互 shell 先确认 `node/openclaw` PATH

## 重点技能
- `gsd`、`deep-research`、`second-brain`
- `rrz` / `rrz-publish`
- `xhs-publish`

## 长期主线
- 人人租自动运营系统（上架 + 商家后台运营）是长期主任务，不是一次性脚本；后续默认按“长期维护目标 / 持续升级工作流”处理。
- 该方向的默认目标不是单次补商品，而是形成稳定、可靠、高效率、低人工介入的长期工作流。  

## 关键教训
- memory 故障排查：运行时 → provider 配置 → 模型/索引。
- 远程排障优先非交互化（SSH 公钥 + 干净 shell）。
- 重载 Gateway 后必须立即验证消息链路。
- RPC probe 正常不等于服务托管层正常。
- session 过胖失效：备份旧会话 → 移除映射 → 新建干净会话。
- `MEMORY.md` / daily note / 旧引导文件过大都会拖慢执行。
- `exec(background=true)` 仍受 timeout 约束，长任务必须显式设高 timeout 或分批执行。
- 人人租图片上传：不操作 file input，直接用页面已加载的 OSS SDK + base64 转 File 对象（见 `skills/rrz-e2e/scripts/rrz_upload.js`）。
- 人人租执行器禁止依赖固定 Vue 组件 uid；必须按特征动态定位商品信息 model 与销售规格 `sellTableData`，并优先收敛为原子提交脚本，避免重复踩“页面树变化后脚本失效”的旧坑。
- 人人租图片写回到 Vue 数据层时，图片对象不能只写 `url/path/name`，必须同步补 `src`（至少 `src=url`）；否则真实 `saveData/submitData` 在 payload 组装阶段会因读取 `B.src.replace(...)` 报错，导致草稿/提审链路失败。
- 人人租真实提审主链已验证：动态 Vue 定位 → OSS SDK 上传主图/描述图 → Vue 数据层写回（含 `src`）→ `saveData/submitData` 主链 → 列表回查；样板单 814346 已成功进入“审核中”。
- 人人租总架构已正式接线：闲鱼监控系统归入 `cost_estimation`（定价前置层 / 成本估算层），图片处理工作流归入 `image_pipeline`（商品包落地层 / 上传前处理层）；后续执行器必须直接消费它们的标准产物，而不是把两者当外围参考工具。

## 项目索引
- 人人租：`skills/rrz*`、`projects/rrz.md`、`projects/rrz-workflow-v1.md`、`projects/rrz-platform-rules.md`、`projects/rrz-blockers.md`、`projects/rrz-module-contracts.md`
- 小红书：`skills/xhs-publish/`
- 家庭理财：`projects/family-finance/`

## 轻量召回
- `projects/*.md`、`registry/playbooks.json`
- `recent/wins.jsonl`、`recent/failures.jsonl`
- `scripts/context_recall.py "任务描述"`（内部使用）
