#!/usr/bin/env python3
"""
修复键盘事件 - 使用page而非frame
"""
import asyncio
from playwright.async_api import async_playwright

async def fix_keyboard():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        
        for ctx in browser.contexts:
            for page in ctx.pages:
                if "id=801233" in page.url:
                    print("找到目标页面")
                    
                    frame = page.frame(name='rrzuji')
                    if not frame:
                        continue
                    
                    await frame.wait_for_load_state("domcontentloaded")
                    await asyncio.sleep(2)
                    
                    # 先按Escape取消当前激活
                    print("按Escape取消激活")
                    await page.keyboard.press('Escape')
                    await asyncio.sleep(0.5)
                    
                    # 检查激活状态
                    status = await frame.evaluate('''() => {
                        var active = document.querySelector('.ant-select-focused');
                        return {
                            activeElement: active ? '有' : '无'
                        };
                    }''')
                    print(f"激活状态: {status}")
                    
                    # 使用JavaScript点击CPU下拉框
                    print("\n点击CPU下拉框")
                    cpu_click = await frame.evaluate('''() => {
                        // 找到CPU下拉框
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === 'CPU') {
                                var formItem = labels[i].closest('.ant-form-item');
                                if (formItem) {
                                    var select = formItem.querySelector('.ant-select');
                                    if (select) {
                                        // 使用原生click
                                        select.focus();
                                        return {success: true};
                                    }
                                }
                            }
                        }
                        return {success: false};
                    }''')
                    
                    print(f"CPU focus: {cpu_click}")
                    
                    # 现在尝试点击
                    await asyncio.sleep(0.5)
                    
                    # 获取CPU下拉框元素
                    cpu_element = await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === 'CPU') {
                                var formItem = labels[i].closest('.ant-form-item');
                                if (formItem) {
                                    return formItem.querySelector('.ant-select');
                                }
                            }
                        }
                        return null;
                    }''')
                    
                    if cpu_element:
                        print(f"找到CPU元素，尝试点击")
                        # 再次按Escape确保没有激活元素
                        await page.keyboard.press('Escape')
                        await asyncio.sleep(0.3)
                        
                        # 使用locator点击
                        cpu_locator = frame.locator('.ant-select').nth(2)  # 尝试第3个ant-select
                        try:
                            await cpu_locator.click(timeout=3000)
                            print("点击成功!")
                        except Exception as e:
                            print(f"locator点击失败: {e}")
                    
                    await asyncio.sleep(1)
                    
                    # 检查下拉菜单
                    dropdowns = await frame.query_selector_all('.ant-select-dropdown')
                    print(f"\n找到 {len(dropdowns)} 个下拉菜单")
                    
                    for i, d in enumerate(dropdowns):
                        style = await d.get_attribute('style')
                        if style and 'display: none' not in style:
                            print(f"下拉菜单 {i} 可见!")
                            items = await d.query_selector_all('.ant-select-item-option-content')
                            for item in items[:5]:
                                text = await item.text_content()
                                print(f"  选项: {text.strip()}")
                    
                    print("\n完成")
                        
        await browser.close()

asyncio.run(fix_keyboard())
