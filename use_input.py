#!/usr/bin/env python3
"""
使用input触发下拉菜单
"""
import asyncio
from playwright.async_api import async_playwright

async def use_input():
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
                    
                    # 先按Escape取消激活
                    await page.keyboard.press('Escape')
                    await asyncio.sleep(0.3)
                    
                    # 获取所有输入框
                    inputs = await frame.query_selector_all('input.ant-select-selection-search-input')
                    print(f"找到 {len(inputs)} 个搜索输入框")
                    
                    # CPU输入框是第3个 (索引2) - 品牌、型号、CPU
                    if len(inputs) >= 3:
                        cpu_input = inputs[2]
                        print(f"找到CPU输入框，尝试聚焦")
                        
                        # 聚焦到CPU输入框
                        await cpu_input.focus()
                        await asyncio.sleep(0.5)
                        
                        # 输入搜索内容
                        print("输入搜索: 骁龙8")
                        await page.keyboard.type('骁龙8', delay=50)
                        await asyncio.sleep(1)
                        
                        # 检查下拉菜单
                        dropdowns = await frame.query_selector_all('.ant-select-dropdown')
                        for d in dropdowns:
                            style = await d.get_attribute('style')
                            if style and 'display: none' not in style:
                                print(f"找到打开的下拉菜单!")
                                items = await d.query_selector_all('.ant-select-item-option-content')
                                for item in items:
                                    text = await item.text_content()
                                    print(f"  选项: {text.strip()}")
                                break
                        else:
                            print("下拉菜单未打开")
                            
                            # 尝试按键打开菜单
                            print("尝试按键打开")
                            await page.keyboard.press('ArrowDown')
                            await asyncio.sleep(0.5)
                            
                            dropdowns = await frame.query_selector_all('.ant-select-dropdown')
                            for d in dropdowns:
                                style = await d.get_attribute('style')
                                if style and 'display: none' not in style:
                                    print(f"下拉菜单现在打开了!")
                                    items = await d.query_selector_all('.ant-select-item-option-content')
                                    for item in items:
                                        text = await item.text_content()
                                        print(f"  选项: {text.strip()}")
                                    break
                    
                    print("\n完成")
                        
        await browser.close()

asyncio.run(use_input())
