#!/usr/bin/env python3
"""
人人租后台自动化测试脚本
使用 Playwright 直接控制浏览器
"""

import asyncio
from playwright.async_api import async_playwright
import sys

async def test_rrz():
    async with async_playwright() as p:
        # 启动浏览器（使用优化参数）
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-background-networking',
                '--disable-background-timer-throttling',
                '--disable-component-update',
                '--disable-extensions',
                '--no-first-run',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        # 注入反检测脚本
        await page.add_init_script(path='/Users/xs/.openclaw/workspace/extensions/browser-enhancement/anti-detect.js')
        
        print("✓ 浏览器已启动，反检测脚本已注入")
        
        # 访问人人租后台
        print("→ 正在访问人人租后台...")
        await page.goto('https://admin.rrzu.com/spu-view/list', wait_until='networkidle')
        
        print("✓ 页面加载完成")
        
        # 等待iframe加载
        await page.wait_for_timeout(3000)
        
        # 截图
        screenshot_path = '/Users/xs/.openclaw/workspace/rrz-test.png'
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✓ 截图已保存: {screenshot_path}")
        
        # 检查是否需要登录
        title = await page.title()
        print(f"✓ 页面标题: {title}")
        
        # 保持浏览器打开，等待手动操作
        print("\n浏览器将保持打开状态，按 Ctrl+C 关闭...")
        try:
            await page.wait_for_timeout(600000)  # 等待10分钟
        except KeyboardInterrupt:
            print("\n正在关闭浏览器...")
        
        await browser.close()
        print("✓ 测试完成")

if __name__ == '__main__':
    asyncio.run(test_rrz())
