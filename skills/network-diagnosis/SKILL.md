# 网络诊断技能

## 问题分析流程

### 1. 检查代理

```bash
# 检查系统代理设置
scutil --proxy

# 检查环境变量
env | grep -i proxy

# 检查监听端口
lsof -i :1080 -i :7890 -i :51363
```

### 2. 识别代理软件

| 端口 | 常见软件 |
|------|----------|
| 1080 | V2Ray, Shadowsocks |
| 7890 | Clash |
| 51363 | Clash |
| 8080 | 代理转发 |

### 3. 解决方案

- **临时关闭**：在软件中关闭"系统代理"
- **永久关闭**：退出软件
- **环境变量**：unset http_proxy https_proxy

### 4. 验证

```bash
# 测试网络连通性
curl -I https://www.google.com

# 检查当前出口IP
curl ipinfo.io
```
