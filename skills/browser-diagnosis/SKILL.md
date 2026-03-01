# 浏览器诊断技能

## 诊断流程

### 1. 检查浏览器状态
```bash
# 检查OpenClaw浏览器状态
openclaw browser status

# 检查CDP端口
lsof -i :18800
```

### 2. 检查系统资源
```bash
# CPU和内存
top -l 1 | head -10

# Chrome进程数
ps aux | grep -i chrome | grep -v grep | wc -l
```

### 3. 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 超时/无响应 | CDP连接断开 | 重启浏览器 |
| 多个Chrome进程 | 残留进程过多 | 清理进程 |
| 页面加载慢 | 网络/资源问题 | 检查网络 |

### 4. 自动诊断脚本
```bash
#!/bin/bash
echo "=== 浏览器诊断 ==="

# 检查CDP
echo "CDP端口状态:"
lsof -i :18800 | head -3

# Chrome进程
echo "Chrome进程数:"
ps aux | grep -i chrome | grep -v grep | wc -l

# 资源
echo "系统负载:"
uptime
```

### 5. 快速修复
```bash
# 停止并重启浏览器
openclaw browser stop
openclaw browser start
```
