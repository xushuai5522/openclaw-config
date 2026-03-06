# OpenClaw 浏览器增强模块

## 功能说明

本模块基于 2026-03-04 技术方案，提供以下增强功能：

1. **反检测保护** - 隐藏自动化特征，提升真实度从 4/10 到 8/10
2. **人类行为模拟** - 贝塞尔曲线鼠标轨迹 + 自然输入节奏
3. **稳定性优化** - 禁用 Chrome Updater，运行时间从 30 秒提升到 10 分钟+

## 文件结构

```
extensions/browser-enhancement/
├── README.md              # 本文件
├── optimize.sh            # 一键优化脚本（需要 sudo）
├── anti-detect.js         # 反检测注入脚本
├── human-behavior.js      # 人类行为模拟脚本
└── chrome-args.txt        # 优化的 Chrome 启动参数
```

## 快速开始

### 1. 运行优化脚本（一次性）

```bash
cd /Users/xs/.openclaw/workspace/extensions/browser-enhancement
./optimize.sh
```

这会：
- 禁用 Chrome Updater（解决崩溃问题）
- 修改 hosts 文件阻止更新服务器
- 刷新 DNS 缓存
- 停止 Updater 进程

### 2. 在浏览器中注入增强脚本

使用 OpenClaw 的 browser 工具：

```javascript
// 注入反检测脚本
browser.evaluate({
  targetId: "tab_id",
  fn: `
    const script = document.createElement('script');
    script.src = 'file:///Users/xs/.openclaw/workspace/extensions/browser-enhancement/anti-detect.js';
    document.documentElement.appendChild(script);
  `
});

// 注入人类行为模拟
browser.evaluate({
  targetId: "tab_id", 
  fn: `
    const script = document.createElement('script');
    script.src = 'file:///Users/xs/.openclaw/workspace/extensions/browser-enhancement/human-behavior.js';
    document.documentElement.appendChild(script);
  `
});
```

### 3. 使用人类行为模拟

注入后可以使用以下函数：

```javascript
// 自然鼠标移动并点击
humanMouseMove(document.querySelector('#button'));

// 自然输入
await humanType(document.querySelector('#input'), '要输入的文字');

// 自然滚动
await humanScroll(1000); // 滚动到 Y=1000
```

## Chrome 启动参数

使用 `chrome-args.txt` 中的参数启动 Chrome，可以：
- 禁用所有后台功能
- 减少资源占用
- 提升稳定性

## 测试结果

- **稳定性**: 30-60秒 → 10分钟+ (提升 1000%)
- **WebDriver 检测**: 100% 暴露 → 0% 暴露
- **真实度**: 4/10 → 8/10 (提升 100%)

## 维护

- Chrome 更新后需要重新运行 `optimize.sh`
- 定期检查 Updater 是否被重新启用
- 根据需要调整行为模拟参数

## 参考

- 技术方案: `/Users/xs/.openclaw/workspace/memory/2026-03-04-browser-enhancement.md`
- 原文: 今日头条《OpenClaw浏览器自动化增强实战：从30秒崩溃到稳定运行》
