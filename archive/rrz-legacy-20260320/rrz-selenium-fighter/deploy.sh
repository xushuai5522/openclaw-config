#!/bin/bash
# NEC服务器部署脚本

set -e

echo "🚀 开始部署人人租Selenium自动化到NEC服务器"

# 检查Python版本
echo "📋 检查Python环境..."
python3 --version || { echo "❌ Python3未安装"; exit 1; }

# 创建虚拟环境
echo "🔧 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
source venv/bin/activate

# 升级pip
echo "📦 升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📦 安装依赖包..."
pip install -r requirements.txt

# 检查Chrome是否安装
echo "🔍 检查Chrome浏览器..."
if command -v google-chrome &> /dev/null; then
    echo "✅ Chrome已安装: $(google-chrome --version)"
elif command -v chromium-browser &> /dev/null; then
    echo "✅ Chromium已安装: $(chromium-browser --version)"
else
    echo "⚠️  未检测到Chrome，将尝试安装..."
    
    # 检测系统类型
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        echo "检测到Debian/Ubuntu系统"
        sudo apt-get update
        sudo apt-get install -y wget gnupg
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
    elif [ -f /etc/redhat-release ]; then
        # CentOS/RHEL
        echo "检测到CentOS/RHEL系统"
        sudo yum install -y wget
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
        sudo yum install -y ./google-chrome-stable_current_x86_64.rpm
        rm google-chrome-stable_current_x86_64.rpm
    else
        echo "❌ 未知系统类型，请手动安装Chrome"
        exit 1
    fi
fi

# 运行测试
echo "🧪 运行基础测试..."
python test_simple.py

echo ""
echo "✅ 部署完成！"
echo ""
echo "下一步："
echo "1. 复制配置文件: cp config.example.env .env"
echo "2. 编辑.env文件，填入真实账号密码"
echo "3. 运行主程序: python rrz_selenium.py"
echo ""
