#!/usr/bin/env python3
"""
使用Playwright原生点击
"""
import asyncio
from playwright.async_api import async_playwright

async def native_click():
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
                    
                    # 先获取当前状态
                    status = await frame.evaluate('''() => {
                        var active = document.querySelector('.ant-select.ant-select-focused, .ant-select-focused');
                        return {
                            activeElement: active ? active.outerHTML.substring(0, 200) : 'none'
                        };
                    }''')
                    print(f"当前激活元素: {status}")
                    
                    # 按Escape取消
                    await frame.keyboard.press('Escape')
                    await asyncio.sleep(0.5)
                    
                    # 使用frame.locator找到CPU下拉框并点击
                    print("使用locator点击CPU")
                    try:
                        # 找到CPU下拉框
                        cpu_locator = frame.locator('div.ant-form-item').filter(has_text='CPU').locator('.ant-select')
                        if await cpu_locator.count() > 0:
                            print(f"找到CPU下拉框: {await cpu_locator.count()} 个")
                            await cpu_locator.first.click(force=True, timeout=5000)
                            print("点击成功")
                    except Exception as e:
                        print(f"locator点击失败: {e}")
                    
                    await asyncio.sleep(1)
                    
                    # 检查下拉菜单
                    dropdowns = await frame.query_selector_all('.ant-select-dropdown')
                    print(f"找到 {len(dropdowns)} 个下拉菜单")
                    
                    for i, d in enumerate(dropdowns):
                        style = await d.get_attribute('style')
                        print(f"下拉菜单{i}: style = {style[:100] if style else 'none'}")
                        if style and 'display: none' not in style:
                            print("  -> 可见!")
                            items = await d.query_selector_all('.ant-select-item-option-content')
                            for item in items:
                                text = await item.text_content()
                                print(f"    选项: {text.strip()}")
                    
                    # 尝试另一种方式 - 使用frame.locator直接通过文本查找
                    print("\n尝试使用get_by_text")
                    try:
                        # 找到label并点击
                        cpu_label = frame.get_by_text("CPU", exact=True).first
                        await cpu_label.scroll_into_view_if_needed()
                        await asyncio.sleep(0.3)
                        
                        # 找到下一个comboBox
                        # 这需要找到CPU label的父元素，然后找下一个
                        print("点击CPU label")
                    except Exception as e:
                        print(f"get_by_text失败: {e}")
                    
                    print("\n完成")
                        
        await browser.close()

asyncio.run(native_click())
