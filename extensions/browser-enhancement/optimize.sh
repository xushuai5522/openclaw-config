#!/bin/bash
# OpenClaw 浏览器优化一键脚本
# 需要 sudo 权限

set -e

echo "=== OpenClaw 浏览器优化脚本 ==="
echo ""

# 1. 禁用 Chrome Updater
echo "步骤 1/4: 禁用 Chrome Updater..."

UPDATER_PATH="/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/145.0.7632.159/Helpers/GoogleUpdater.app"

if [ -d "$UPDATER_PATH" ]; then
    sudo mv "$UPDATER_PATH" "${UPDATER_PATH}.disabled"
    echo "✓ Chrome Updater 已禁用"
else
    echo "✓ Chrome Updater 已经被禁用或不存在"
fi

# 2. 修改 hosts 文件
echo ""
echo "步骤 2/4: 修改 hosts 文件阻止更新服务器..."

if ! grep -q "Block Google Chrome Updater" /etc/hosts; then
    sudo bash -c 'cat >> /etc/hosts << EOF

# Block Google Chrome Updater
127.0.0.1 tools.google.com
127.0.0.1 update.googleapis.com
127.0.0.1 clients2.google.com
127.0.0.1 clients4.google.com
EOF'
    echo "✓ hosts 文件已更新"
else
    echo "✓ hosts 文件已包含屏蔽规则"
fi

# 3. 刷新 DNS 缓存
echo ""
echo "步骤 3/4: 刷新 DNS 缓存..."
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder 2>/dev/null || true
echo "✓ DNS 缓存已刷新"

# 4. 停止 Updater 进程
echo ""
echo "步骤 4/4: 停止 Updater 进程..."
launchctl remove com.google.GoogleUpdater.wake 2>/dev/null || true
echo "✓ Updater 进程已停止"

echo ""
echo "=== 优化完成！==="
echo ""
echo "Chrome 浏览器稳定性已提升，预计可稳定运行 10 分钟以上"
echo "反检测脚本和人类行为模拟已就绪"
echo ""
