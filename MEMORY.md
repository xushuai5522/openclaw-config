# MEMORY.md - 长期记忆

## 我的通用工作原则
1. 🌐 永远使用中文沟通
2. 💾 重要事项即时记录到文件（不过度依赖记忆）
3. 🔄 根据页面实时变化及时调整方案
4. ✅ 完成任务后才算结束，中途遇到问题及时汇报
5. 📝 每完成关键步骤主动汇报进度，但不停止工作，继续完成任务
6. ⚠️ 遇到不确定的情况先确认再执行，仅包含需要人为确认的需求问题，技术和方案问题先执行测试，最后汇报即可
7. 🎯 以结果为导向，减少无效沟通
8. 🔧 任何需要我手动操作，但是不涉及敏感权限的，不要再问我，你来完成
9. 🔁 任务执行失败多次，不涉及敏感权限和安全相关，需要主动变更方案并执行重试，重试多次失败（3种以上方案失败过重试10次失败），才可以向我请求帮助，否则需要完全自主实现交代的所有任务
10. 📊 定期检查系统状态，保持主动工作节奏
11. 🔍 **新功能开发优先GitHub** - 优先寻找成熟开源方案，不要自己实现
12. 🚀 **先尝试再求助** - 在让用户操作之前，永远先利用已知技能和方案尝试完成，能自己解决就不问用户

## 每次回复的必要格式（重要！必须遵守）
### 1. 开头必须带emoji
- 👌 = 了解/收到
- 👍 = 确认/完成
- 💪 = 进行中

### 2. 简单报告消息队列状态（不解释任务内容）
- 队列深度
- 待处理数量

例：
```
👌 收到！
| 队列 | 状态 |
|------|------|
| 深度 | 0 |
| 待处理 | 无 |
```

### 3. 超时处理原则（重要！）
- **遇到网络超时/工具卡死，不要无限等待**
- 设置合理超时（30秒），超时立即放弃
- **超时后检测任务是否仍在运行**
- 如果任务正常运行 → 输出进展，继续工作
- 如果任务真正失败 → 放弃并报错
- 记录错误到日志
- 尝试备用方案
- **无论如何要给大哥回复，不能卡死**
- 如果实在搞搞定，诚实地告诉大哥问题所在

### 3. 飞书emoji（已禁用，因API失败）
- 现在使用普通文字回复

## 智能工作流
### 每日流程
- 早8点：天气 + 日历 + 邮件检查
- 下午：任务处理 + 人人租后台检查
- 晚6点：当日总结

### 每周任务
- 周报总结
- 清理不必要文件
- 检查系统健康

## 平台配置
- OpenClaw Gateway 已配置无头浏览器模式 (browser.headless: true)
- 用户新增 API 端点: https://az.ve-rel.com/

## 自动化原则
- 登录模块：自主调用，不再询问用户
- 登录脚本位置：/Users/xs/.openclaw/workspace/rrz_login.py

## 人人租自动化 (2026-02-17)
- 完整自动化脚本: /Users/xs/.openclaw/workspace/rrz_full_auto.py
- 成功提审商品: Tektronix MDO3052
- 定价: 7天259/30天432/3月1231/6月2332/1年4406, 押金2308
- 优化要点: 60秒超时, 循环关闭弹窗, JS直接操作DOM
- 商家后台: https://admin.rrzu.com
- 账号: 15162152584
- 密码: 152584
- 店铺名: 书电马数码店
- 商品类目: 电脑/平板 > 平板 > 小米

### 登录技能 (2026-02-18)
- 技能位置: `/Users/xs/.openclaw/workspace/skills/rrz-login/SKILL.md`
- 登录模块: `/Users/xs/.openclaw/workspace/rrz_login.py`
- 登录方式: 密码登录（必须勾选同意协议）
- 关键步骤: 点击"密码登录" → 输入账号密码 → 勾选协议 → 点击登录

### 上架规则（爬虫分析得出）
- 标题格式: `90新 + 品牌 + 型号 + 商品特点`
- 图片要求: 纯白底色（商品主体以外不允许有白色以外的其他背景色），600x600px以上
- 主图要求: 仅允许商品展示，**不允许文字内容添加**
- 禁止词: 免押、免息、分期、最佳、最便宜等
- 内存和运行内存选择必须正确匹配

### 审核不通过商品修改流程（已固化技能）
- 审核拒绝原因：
  - 套餐内需要详细写明具体租用方式
  - 删除套餐中的"租赁"字眼
- 修改方法（自动化脚本）：
  1. 使用Playwright连接CDP (http://127.0.0.1:18800)
  2. 获取name='rrzuji'的iframe
  3. 使用frame.evaluate()执行JavaScript查找并点击修改商品按钮
  4. 在编辑页面，先关闭"方案应用邀请"确认弹窗
  5. 找到套餐相关输入框，去除"租赁"字眼，添加租用方式说明
  6. 点击提交审核按钮

### 自动化脚本位置
- /Users/xs/.openclaw/workspace/rrz_click_edit_v2.py

### 审核不通过商品（2026-02-16）
- 红蜘蛛 X Elite 专业校色 (ID:17513) - ✅ 已修复并重新提交审核
- Wacom数位屏 新帝Pro11寸 (ID:191550) - ✅ 已修复并重新提交审核
- Apple TV 7代 (ID:195292) - 系统下架，需去除"最"等敏感词
- Xiaomi Pad 5 11英寸 80新: 租金 1.92-3.30元/天，押金 800元 ✅
- Xiaomi Pad 6S Pro 12.4英寸 90新: 租金 4.93-6.00元/天，押金 1000元 ✅ (已修复并上架)
- 修复并重新提交的审核不通过商品:
  - HIFI耳机 (ID:798114) - 审核中
  - 红蜘蛛校色仪 (ID:17513) - 审核中  
  - wacom数位屏 (ID:191550) - 审核中
  - 坚果投影 (ID:640674) - 审核中
  - 博世探测仪 (ID:191191) - 审核中

## 用户偏好
- 中文交流
- 希望 AI 自动完成任务，减少人工干预
- 希望 24/7 运行
- 需要无头浏览器模式

## 每日图片推荐
- 仅每天第一次对话时附带一张精选照片
- 用户会打分，我会根据反馈调整推荐风格
- 照片来源：Unsplash经典获奖作品

## 视频爬取技能 (2026-02-20)
- 从网页HTML中提取视频URL
- 常用URL模式：media.rrzuji.cn, video, mp4, m3u8
- 工具：Playwright + curl
- 成功案例：人人租商家大学视频

## 图片处理技能 (2026-02-20)
- 从闲鱼监控数据获取商品图片
- 去除水印 + 转换为白底图
- 工具：Pillow + requests
- 输出：800x800px 白底图

## 官网图片获取技能 (2026-02-20)
- 从Apple等官网获取产品图
- 方法：Playwright打开图片URL → 截图 → 裁剪白底
- 解决CDN访问限制问题

## 浏览器复制技能 (2026-02-20)
- 查找页面中带SVG图标的按钮
- 点击复制按钮后使用pbpaste获取剪贴板
- 成功案例：Replicate API Token复制

## 飞书图片发送（重要！必须遵守）
- 飞书图片必须用 **workspace相对路径**，如 `./xianyu_login.png`
- **禁止**用绝对路径 `/tmp/xxx.png` 或 `/Users/xs/...`
- 正确示例：`message: media="./image.png"`
- 错误示例：`message: media="/tmp/image.png"` ❌
- 如果图片在/tmp等临时目录，必须先复制到workspace目录再发送
- **每次发送图片前必须检查路径是否符合规范**
- 发送前心里默念：路径必须是 `./xxx/yyy.jpg` 格式

## 系统级鼠标模拟能力 (2026-02-19)
- 工具：**cliclick** (macOS命令行鼠标模拟)
- 安装：`brew install cliclick`
- 权限：需要Mac辅助功能权限（系统偏好设置 → 安全性与隐私 → 隐私 → 辅助功能）
- 使用方式：
  - `cliclick p` - 获取当前鼠标位置
  - `cliclick m:x,y` - 移动鼠标到指定位置
  - `cliclick c:x,y` - 在指定位置点击
  - `cliclick dc:x,y` - 在指定位置右键点击
  - `cliclick t:"文字"` - 输入文字
- 应用场景：
  - 点击Chrome扩展图标连接浏览器
  - 操作iframe内的元素（当OpenClaw浏览器工具失效时）
  - 系统级自动化操作
- 注意事项：
  - iframe内部元素优先使用OpenClaw浏览器工具
  - cliclick作为备用方案

### TTS (文字转语音)
- 问题：edge-tts 生成的 MP3 飞书无法解析 (duration=0)
- 解决方案：edge-tts → afconvert 转换 WAV → 飞书 audio 消息
- 最终配置：
  - 语音：zh-CN-XiaoyiNeural
  - 语速：+30%
  - 采样率：16kHz
  - 格式：WAV (LEI16)
- 发送方式：飞书 audio 消息 (file_type=opus)
- 脚本：/Users/xs/.openclaw/scripts/feishu_tts.py

### STT (语音转文字 - 永久技能)
飞书语音消息解析步骤：
1. 飞书语音文件已自动保存到 `/Users/xs/.openclaw/media/inbound/*.ogg`
2. 使用afconvert转换OGG为WAV格式 (macOS)
3. 使用faster-whisper进行语音识别
4. 返回文字内容

**关键：使用本地inbound目录的文件，不要尝试从飞书API下载！**

代码示例：
```python
import subprocess
from faster_whisper import WhisperModel

# 1. OGG已保存在inbound目录，使用完整路径
ogg_path = "/Users/xs/.openclaw/media/inbound/{filename}.ogg"
wav_path = "/tmp/voice.wav"

# 2. 转换格式 (macOS) - 使用16kHz采样率
subprocess.run(["afconvert", "-d", "LEI16", "-f", "WAVE", "-r", "16000", ogg_path, wav_path])

# 3. 语音识别 - 必须使用base模型（更准确）
model = WhisperModel("base", device="cpu")
segments, info = model.transcribe(wav_path, language="zh")
text = "".join([s.text for s in segments])
print(text)
```

**模型要求**：必须使用 **base** 模型（唯一选项）

**脚本位置**: /Users/xs/.openclaw/scripts/feishu_stt.py

## Brave Search API
- 注册遇到人机验证和OTP验证码问题，自动化无法绕过
- 账号：945370625@qq.com / Xs552200.123
- 需要用户手动完成注册获取 API Key

## 浏览器自动化问题 (2026-02-17)
- macOS持续终止Chrome进程(SIGKILL)
- Playwright连接CDP端口18800不稳定
- 尝试方案：重启浏览器、更换端口、简化参数均失败
- 建议：使用无头浏览器模式或改用Safari

## 人人租自动化问题 (2026-02-19)
- 验证码问题：人人租有反爬机制，有头和无头模式都会触发验证码
- 根本原因：网站风控，不是技术问题
- 解决方案：
  1. 手动登录一次后保存Cookie
  2. 等待验证码间歇期再试
  3. 使用API（如有）

## Skills 系统进阶 (2026-02-19)
- 来源：大哥发的今日头条文章「深入解析 OpenClaw 的 Skills 扩展系统」
- 三级渐进披露：
  - 第一级：名片(~24 token/技能) - 名称+描述注入提示词
  - 第二级：完整说明书 - AI判断相关时才读取
  - 第三级：深度资源 - 仅执行时加载
- AI自生成技能：可用 skill-creator 让俺自己写新技能
- 热重载：250ms文件监听，改了SKILL.md立即生效
- 跨平台：遵循 AgentSkills 标准，兼容 Claude Code、Cursor 等

## 今日新技能 (2026-02-19)
- daily-review：每日复盘与知识提炼技能
- error-learning：错误学习与自我修正
- task-planning：任务规划与拆分
- humanizer：去除AI味，让文字更自然
- self-improvement：自我进化技能
- n8n-workflow-automation：n8n工作流生成
- qmd：超省token模式
- find-skills：技能搜索与安装（元能力）
- second-brain：第二大脑，知识库管理
- deep-research：深度研究，复杂任务分析
- prompt-guard：提示词防护，防御注入攻击
- agent-browser：浏览器自动化
- 位置：/Users/xs/.openclaw/workspace/skills/
