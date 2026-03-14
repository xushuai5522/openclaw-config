# RRZ Codex 本轮测试总结

更新时间：2026-03-14 08:58 Asia/Shanghai

## 目标
继续推进人人租发布/提交流程打通，复用前一轮 Codex 已有成果，避免重复摸索。

## 结论总览
本轮产物分三阶段：

1. **2026-03-10 表层自动化试错**
   - 目标：定位类目、价格表、素材中心、主图绑定、强提校验。
   - 结论：
     - 品牌/型号表面可选，但**未真正落库**。
     - 销售规格中**押金等值未真正落库**。
     - 主图在页面上看似挂上，但提交时仍报**请添加商品图片**，说明**图片绑定不稳定**。
   - 关键截图：`tmp_rrz_force_submit_result.png`

2. **2026-03-11 ~ 2026-03-12 底层状态注入 / 提交流程探针**
   - 方向正确，进入 Vue 内部状态层。
   - 核心成果：
     - 写了 `rrz_live_state_patch.py`：直接 patch Vue 表单状态。
     - 写了 `rrz_live_submit_probe.py`：直接 probe `checkData/saveData/submitData`。
     - 能定位到真实表单对象：`baseInfoForm / sellInfoForm / sellTableData / sellDetailForm`。
     - 能把阻塞逐步推进到更深校验层。
   - 仍未完全打通最终提交。

3. **2026-03-13 之后**
   - Codex 多次继续尝试，但日志显示反复出现：
     - `You've hit your usage limit. To get more access now, send a request to your admin or try again at Mar 17th, 2026 11:03 PM.`
   - 因此后续推进基本停滞。

## 当前浏览器现场判断
- 浏览器中存在两个人人租 create 页残留现场。
- 现场出现过“**经营地址信息补充**”弹窗。
- 现场还出现过**测试数据串单**现象：
  - 标题/描述是 `泰克 MDO3052 混合域示波器`
  - 品牌/型号却显示 `苹果 / Mac mini（M4）2024款`
- 这更像是**测试用示波器数据 patch 到 Mac mini 类目页**导致的串单，不一定代表真实发布目标错误，但说明现场已经被测试污染。

## 本轮最有价值文件

### 核心脚本
1. `rrz_live_state_patch.py`
   - 作用：连接当前 Chrome CDP，会写真实 Vue 状态，不依赖表层点击。

2. `rrz_live_submit_probe.py`
   - 作用：探测 `checkData / saveData / submitData`，记录请求、模态框、异常。

3. `rrz_force_submit.py`
   - 作用：第一轮强提校验脚本，用于收集最早的真实阻塞信息。

### 配置
4. `tmp_rrz_state_patch_config.json`
   - `rrz_live_state_patch.py` 的测试输入。
   - 当前内容使用的是 **泰克 MDO3052 示波器测试数据**。

5. `tmp_rrz_submit_probe_config.json`
   - `rrz_live_submit_probe.py` 的 live probe 配置。

### 关键截图
6. `tmp_rrz_force_submit_result.png`
   - 最早强提后的真实前端阻塞截图。

7. `tmp_rrz_main_images_attached.png`
   - 表面主图曾挂回页面的证据。

8. `tmp_rrz_after_price_fix.png`
   - 价格/buyout 修正后的状态截图。

9. `tmp_rrz_submit_attempt_after_price.png`
   - 价格修正后再次点击提交的截图。

10. `tmp_rrz_submit_after_all_checks.png`
   - 尝试清完 section 检查后再次提交的截图。

11. `tmp_rrz_modal_blocking_submit.png`
   - 提交流程中阻塞 modal 的截图。

12. `tmp_rrz_submit_probe_live.png`
   - submit probe 的 live 截图。

13. `tmp_rrz_after_dom_submit_click2.png`
   - 2026-03-14 最新 DOM 提交测试残留截图。

## 文件对应关系

### A. 强提验证链
- 脚本：`rrz_force_submit.py`
- 截图：`tmp_rrz_force_submit_result.png`
- 结论：品牌/型号、押金、主图是三大硬阻塞。

### B. 状态注入链
- 脚本：`rrz_live_state_patch.py`
- 配置：`tmp_rrz_state_patch_config.json`
- 截图：
  - `tmp_rrz_state_patch_after.png`
  - `tmp_rrz_live_page2_after_low_level.png`
  - `tmp_rrz_after_price_fix.png`

### C. 提交流程探针链
- 脚本：`rrz_live_submit_probe.py`
- 配置：`tmp_rrz_submit_probe_config.json`
- 截图：
  - `tmp_rrz_submit_probe_live.png`
  - `tmp_rrz_submit_after_all_checks.png`
  - `tmp_rrz_modal_blocking_submit.png`

## 日志结论（来自 ~/.codex/log/codex-tui.log 与 ~/.codex/history.jsonl）
1. 2026-03-10 的明确摘要：
   - 品牌、型号没选上/未落库。
   - 押金必填未落库。
   - 主图回填不稳定。
2. 2026-03-11 ~ 2026-03-12：
   - Codex 开始读 Vue 组件、抓 `detailsContentRef`、抓 `sellDetailForm.images`、抓 `submitData()`、甚至下载前端 bundle 反向分析。
   - 方向正确，产物值得复用。
3. 2026-03-13：
   - 继续点提交、测 `/server-violation/product?spu_id=`。
   - 但已经被 usage limit 反复打断。

## 当前判断
- **不要从头重做。**
- **不要继续依赖旧的挂起 Codex 进程。**
- **应基于已有两个核心脚本继续推进。**
- 当前最可能的剩余关键问题：
  1. 真实发布目标到底是 Mac mini 还是示波器，必须先定；当前测试现场已经串单。
  2. 主图绑定字段与最终提交 payload 的对应关系仍需确认。
  3. `submitData()` / 点击提交后，是否还卡在：
     - `server-violation/product?spu_id=` 预检
     - 顶层 modal
     - 经营地址补充弹窗
     - 或真正后端 submit API

## 下一步要求（给新的 Codex）

### 总原则
1. **先基于已有成果继续，不要从零摸索。**
2. **先澄清真实目标商品。**
   - 当前现场混有：
     - `泰克 MDO3052 示波器` 测试数据
     - `Mac mini（M4）2024款` 类目状态
   - 第一件事：确认这次要推进的是哪一个真实商品发布路径；如果现场已污染，先只做诊断与清理，不要盲提。
3. **优先复用以下文件：**
   - `rrz_live_state_patch.py`
   - `rrz_live_submit_probe.py`
   - `rrz_force_submit.py`
   - `tmp_rrz_state_patch_config.json`
   - `tmp_rrz_submit_probe_config.json`
4. **不要只做表层点击。**
   - 优先走真实 Vue 状态与真实 submit 链路。
5. **任何提交动作前，先截图 + 输出当前表单状态摘要。**
6. **如果要动 live 页面，先判断当前页是不是测试污染页。**

### 具体任务
1. 读取并理解：
   - `rrz-codex-findings.md`
   - `rrz_live_state_patch.py`
   - `rrz_live_submit_probe.py`
   - `rrz_force_submit.py`
2. 检查当前 Chrome CDP 下 RRZ 页面：
   - 哪个 tab 是真实待推进页
   - 是否存在测试串单
   - 是否存在阻塞 modal / 顶层弹窗
3. 输出一份“当前现场诊断”摘要：
   - tab 列表
   - 每个 RRZ tab 的标题、URL、主要商品信息
   - 是否可继续复用
4. 如果现场污染严重：
   - 不要直接提交
   - 先给出“保留现场证据 + 清理方案 + 重新进入页面方案”
5. 如果现场可用：
   - 继续复用 `rrz_live_state_patch.py` 与 `rrz_live_submit_probe.py`
   - 先打通 `saveData()` 与 `submitData()` 的真实阻塞点
   - 再决定是否执行真实提交
6. 明确输出：
   - 现在卡在哪一步
   - 是否为前端状态问题 / modal 问题 / submit API 问题 / 地址补充问题
   - 下一步最小动作是什么

## 期望输出方式
- 先给过程性摘要，不要沉默挂机。
- 每完成一个里程碑就输出：
  - 已检查什么
  - 发现什么
  - 下一步干什么
- 若再次遇到额度/权限/环境阻塞，立刻明确报出。

## 备注
- 老 Codex 进程已长时间挂起且 CPU 为 0，实际不再推进。
- 旧进程保留价值不高，可关闭后重开。
- 新 Codex 需用**全授权自动执行模式**继续推进，但仍应优先保护 live 页面与真实商品数据，避免盲提。