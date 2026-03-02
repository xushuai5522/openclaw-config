#!/usr/bin/env python3
"""
完整填写表单 - CPU、机身储存、运行内存
"""
import asyncio
from playwright.async_api import async_playwright

async def fill_form():
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
                    
                    # ====== 步骤1: 填写CPU ======
                    print("\n=== 填写CPU ===")
                    
                    # 先按Escape取消激活
                    await page.keyboard.press('Escape')
                    await asyncio.sleep(0.3)
                    
                    # 获取所有搜索输入框
                    inputs = await frame.query_selector_all('input.ant-select-selection-search-input')
                    print(f"找到 {len(inputs)} 个搜索输入框")
                    
                    # CPU输入框是第3个 (索引2)
                    cpu_input = inputs[2]
                    await cpu_input.focus()
                    await asyncio.sleep(0.3)
                    
                    # 输入搜索内容
                    print("输入搜索: 骁龙8")
                    await page.keyboard.type('骁龙8', delay=50)
                    await asyncio.sleep(1)
                    
                    # 检查并选择
                    dropdowns = await frame.query_selector_all('.ant-select-dropdown')
                    for d in dropdowns:
                        style = await d.get_attribute('style')
                        if style and 'display: none' not in style:
                            items = await d.query_selector_all('.ant-select-item-option-content')
                            print(f"找到 {len(items)} 个选项")
                            for item in items:
                                text = await item.text_content()
                                print(f"  - {text.strip()}")
                                if '骁龙8' in text:
                                    print(f"  >>> 选择: {text.strip()}")
                                    await item.click()
                                    break
                            break
                    
                    await asyncio.sleep(1)
                    
                    # ====== 步骤2: 填写机身储存 ======
                    print("\n=== 填写机身储存 ===")
                    
                    await page.keyboard.press('Escape')
                    await asyncio.sleep(0.3)
                    
                    inputs = await frame.query_selector_all('input.ant-select-selection-search-input')
                    # 机身储存是第4个 (索引3)
                    storage_input = inputs[3]
                    await storage_input.focus()
                    await asyncio.sleep(0.3)
                    
                    print("输入搜索: 256GB")
                    await page.keyboard.type('256GB', delay=50)
                    await asyncio.sleep(1)
                    
                    dropdowns = await frame.query_selector_all('.ant-select-dropdown')
                    for d in dropdowns:
                        style = await d.get_attribute('style')
                        if style and 'display: none' not in style:
                            items = await d.query_selector_all('.ant-select-item-option-content')
                            print(f"找到 {len(items)} 个选项")
                            for item in items:
                                text = await item.text_content()
                                print(f"  - {text.strip()}")
                                if '256GB' in text and '定制版' not in text:
                                    print(f"  >>> 选择: {text.strip()}")
                                    await item.click()
                                    break
                            break
                    
                    await asyncio.sleep(1)
                    
                    # ====== 步骤3: 填写运行内存 ======
                    print("\n=== 填写运行内存 ===")
                    
                    await page.keyboard.press('Escape')
                    await asyncio.sleep(0.3)
                    
                    inputs = await frame.query_selector_all('input.ant-select-selection-search-input')
                    # 运行内存是第5个 (索引4)
                    ram_input = inputs[4]
                    await ram_input.focus()
                    await asyncio.sleep(0.3)
                    
                    print("输入搜索: 8GB")
                    await page.keyboard.type('8GB', delay=50)
                    await asyncio.sleep(1)
                    
                    dropdowns = await frame.query_selector_all('.ant-select-dropdown')
                    for d in dropdowns:
                        style = await d.get_attribute('style')
                        if style and 'display: none' not in style:
                            items = await d.query_selector_all('.ant-select-item-option-content')
                            print(f"找到 {len(items)} 个选项")
                            for item in items:
                                text = await item.text_content()
                                print(f"  - {text.strip()}")
                                if '8GB' in text and '哈利' not in text:
                                    print(f"  >>> 选择: {text.strip()}")
                                    await item.click()
                                    break
                            break
                    
                    print("\n=== 完成 ===")
                        
        await browser.close()

asyncio.run(fill_form())
