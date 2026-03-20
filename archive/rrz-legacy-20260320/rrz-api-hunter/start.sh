#!/bin/bash
# 人人租API抓包 - 一键启动脚本

echo "🎯 人人租API猎手"
echo "==============================================="
echo ""
echo "📋 请选择抓包方案："
echo ""
echo "1. 浏览器控制台注入（推荐⭐）"
echo "   - 最简单，直接在浏览器中运行"
echo "   - 实时显示API调用"
echo ""
echo "2. Playwright自动抓包"
echo "   - 需要浏览器已打开人人租后台"
echo "   - 自动生成分析报告"
echo ""
echo "3. 查看使用说明"
echo ""
read -p "请输入选项 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "📝 方案1：浏览器控制台注入"
        echo "==============================================="
        echo ""
        echo "步骤："
        echo "1. 打开浏览器，访问 https://admin.rrzu.com"
        echo "2. 登录账号：15162152584 / 152584"
        echo "3. 按 F12 打开开发者工具"
        echo "4. 切换到 Console 标签"
        echo "5. 复制下面的代码，粘贴到控制台并回车"
        echo ""
        echo "按回车键显示代码..."
        read
        echo ""
        cat api_interceptor.js
        echo ""
        echo "==============================================="
        echo "6. 在页面中操作（点击商品列表、发布商品等）"
        echo "7. 操作完成后，在控制台运行："
        echo "   exportApiLog()"
        echo "8. 会自动下载JSON文件"
        echo "9. 将文件放到 captured/ 目录"
        echo ""
        ;;
    2)
        echo ""
        echo "🤖 方案2：Playwright自动抓包"
        echo "==============================================="
        echo ""
        echo "启动抓包工具..."
        python3 api_hunter.py
        ;;
    3)
        echo ""
        cat PROGRESS.md
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac
