#!/bin/bash
# 快速启动脚本 - 用于本地测试

echo "🚀 人人租Selenium自动化 - 快速启动"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  虚拟环境不存在，请先运行: ./deploy.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查配置
if [ ! -f ".env" ]; then
    echo "⚠️  配置文件不存在，请先创建: cp config.example.env .env"
    exit 1
fi

# 加载配置
export $(cat .env | grep -v '^#' | xargs)

# 显示菜单
echo "请选择操作："
echo "1. 运行基础测试"
echo "2. 运行主程序（单个商品）"
echo "3. 批量发布（从JSON）"
echo "4. 查看使用示例"
echo ""

read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo "🧪 运行基础测试..."
        python test_simple.py
        ;;
    2)
        echo "🚀 启动主程序..."
        python rrz_selenium.py
        ;;
    3)
        echo "📦 批量发布..."
        if [ -f "products.json" ]; then
            python batch_publish.py products.json
        else
            echo "⚠️  products.json不存在，使用示例文件"
            python batch_publish.py products_example.json
        fi
        ;;
    4)
        echo "📖 查看使用示例..."
        python examples.py
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac
