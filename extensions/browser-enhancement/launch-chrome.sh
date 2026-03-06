#!/bin/bash
# OpenClaw 浏览器增强 - Chrome启动优化参数

# 基础路径
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
USER_DATA_DIR="$HOME/.openclaw/chrome-profile"
EXTENSIONS_DIR="$HOME/.openclaw/workspace/extensions/browser-enhancement"

# 创建用户数据目录
mkdir -p "$USER_DATA_DIR"

# 优化的启动参数
CHROME_FLAGS=(
  # 禁用后台功能
  "--disable-background-networking"
  "--disable-background-timer-throttling"
  "--disable-backgrounding-occluded-windows"
  "--disable-breakpad"
  "--disable-component-update"
  "--disable-default-apps"
  "--disable-extensions"
  "--disable-hang-monitor"
  "--disable-sync"
  
  # 禁用更新检查
  "--disable-component-extensions-with-background-pages"
  "--disable-features=TranslateUI,BlinkGenPropertyTrees"
  
  # 性能优化
  "--disable-ipc-flooding-protection"
  "--disable-renderer-backgrounding"
  "--disable-backgrounding-occluded-windows"
  "--disable-features=site-per-process"
  
  # 远程调试
  "--remote-debugging-port=18800"
  
  # 用户数据目录
  "--user-data-dir=$USER_DATA_DIR"
  
  # 禁用GPU（可选，如果遇到渲染问题）
  # "--disable-gpu"
)

# 启动Chrome
echo "启动优化后的Chrome..."
"$CHROME_PATH" "${CHROME_FLAGS[@]}" > /dev/null 2>&1 &

echo "Chrome已启动，CDP端口: 18800"
echo "用户数据目录: $USER_DATA_DIR"
