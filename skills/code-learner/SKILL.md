---
name: code-learner
description: |
  代码仓库自主学习技能。系统化学习嵌入式代码仓库的架构、模块关系、关键函数和设计模式。
  触发场景：
  1. 大哥说"继续学习"、"学代码"、"看看xxx仓库"
  2. Heartbeat 空闲时自主触发学习
  3. 新仓库导入后需要学习
  4. Bug 分析前需要快速了解某个模块
  不适用：直接修改代码（需大哥授权）、代码评审（用 git-workflow）。
---

# Code Learner — 代码仓库自主学习

## 学习目标

把代码知识转化为**可持久化的文档**，存入 memory/ 目录，让未来的 session 不用重新读代码。

## 仓库清单

### 学习工作区（/home/op/tools/，可切分支不可 commit）

| 仓库 | 路径 | 芯片 | 用途 | 学习状态 |
|------|------|------|------|---------|
| esp32_platform | `/home/op/tools/esp32_platform` | ESP32-S3 | WiFi 模组 | ✅ 已学（memory/code-architecture.md） |
| AE100_EMS | `/home/op/tools/AE100_EMS` | GD32F30x | AE100/AE103 MCU | ✅ 架构已学（memory/mcu-architecture.md） |
| Storage_PCS_ARM_EMS | `/home/op/tools/Storage_PCS_ARM_EMS` | GD32F470VG | AE103 PCS | ✅ 架构已学（CLAUDE.md 很详细） |
| A17C5_EMS | `/home/op/tools/A17C5_EMS` | GD32F30x | A17C5 PPS | ⚡ 架构概览 |
| a7320_esp32_app | `/home/op/tools/a7320_esp32_app` | ESP32-S3 | A7320 独立 | ⚡ 架构概览 |

### 平台只读区（/data/code-repos/，不可触碰）
代码复用平台自动同步，**绝对不能手动操作**。

## 学习流程（4阶段）

### Phase 1: 架构扫描（~30分钟）
```
1. 目录结构 + 文件统计（find + wc）
2. 主入口（main.c）→ 启动流程
3. 任务列表（xTaskCreate grep）→ 优先级 + 栈大小
4. 编译配置（CMake/Keil）→ 条件编译宏
5. 子模块（.gitmodules）→ 依赖关系
```
输出：更新 `memory/mcu-architecture.md` 或 `memory/code-architecture.md`

### Phase 2: 核心模块深读（~2小时/模块）
按 Bug 分析价值排优先级：
```
通信层（UART/CAN/WiFi）> EMS 算法 > OTA > Flash > 告警 > 外设
```
每个模块记录：
- 关键函数签名 + 行号
- 数据结构定义
- 状态机/流程图
- 已知陷阱

### Phase 3: 交叉关系分析
```
模组 ↔ MCU 通信协议（命令码映射）
MCU ↔ DSP 控制接口
MCU ↔ BMS 电池管理接口
```
输出：更新 `memory/mcu-architecture.md` 的交叉关系章节

### Phase 4: 知识检索优化
```
1. 确认代码复用平台已导入（/opt/code-reuse-platform）
2. 确认向量化完成（keyword + semantic search 可用）
3. 记录常用搜索关键词映射
```

## 学习规则

1. **只读不写** — 学习工作区可以 `git checkout`/`git log`，绝不 commit/push
2. **develop 分支** — 默认看 develop，master 可能落后
3. **先看 CLAUDE.md** — 如果仓库有 CLAUDE.md，先读完再学（已有 AI 文档化的知识）
4. **增量记录** — 不要覆盖已有的架构文档，追加新发现
5. **标注置信度** — 不确定的结论标注 ⚠️
6. **git log -S 追溯** — 关键函数用 `git log -S "function_name"` 看变更历史

## 学习成果存放

| 内容 | 文件 |
|------|------|
| ESP32 模组架构 | `memory/code-architecture.md` |
| MCU 仓库架构 | `memory/mcu-architecture.md` |
| 安全隐患 | `memory/code-risks.md` |
| 缺陷模式 | `memory/bug-patterns/` |
| 关键词映射 | 各架构文档的"搜索关键词"章节 |

## Heartbeat 自学习

空闲 heartbeat 时（无待处理任务），可自主选择一个未完成的学习目标：
1. 检查 `memory/mcu-architecture.md` 中的"学习状态"列
2. 选择 ⚡（概览）级别的仓库深入学习
3. 或对已学仓库的某个模块做 Phase 2 深读
4. 每次学习不超过 30 分钟（控制 token 消耗）
