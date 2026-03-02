#!/usr/bin/env python3
"""
完成表单填写 - CPU、机身储存、运行内存
"""
import asyncio
from playwright.async_api import async_playwright

async def fill_all():
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
                    
                    # 按Escape取消激活
                    await page.keyboard.press('Escape')
                    await asyncio.sleep(0.3)
                    
                    # 滚动到CPU区域
                    await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === 'CPU') {
                                var formItem = labels[i].closest('.ant-form-item');
                                if (formItem) formItem.scrollIntoViewIfNeeded();
                            }
                        }
                    }''')
                    
                    # 点击CPU下拉框 (第3个ant-select)
                    selects = await frame.locator('.ant-select').all()
                    cpu_select = selects[2]
                    await cpu_select.click(force=True, timeout=5000)
                    await asyncio.sleep(0.8)
                    
                    # 检查下拉菜单
                    visible_dropdown = None
                    dropdowns = await frame.query_selector_all('.ant-select-dropdown')
                    for d in dropdowns:
                        style = await d.get_attribute('style')
                        if style and 'display: none' not in style:
                            visible_dropdown = d
                            break
                    
                    if visible_dropdown:
                        print("CPU下拉菜单已打开!")
                        items = await visible_dropdown.query_selector_all('.ant-select-item-option-content')
                        for item in items:
                            text = await item.text_content()
                            print(f"  选项: {text.strip()}")
                            if '骁龙8' in text:
                                print(f"  -> 选择: {text.strip()}")
                                await item.click()
                                break
                    else:
                        print("CPU下拉菜单未打开，尝试使用键盘")
                        # 尝试使用键盘打开
                        await cpu_select.click(force=True)
                        await asyncio.sleep(0.5)
                        await page.keyboard.type('骁龙8', delay=50)
                        await asyncio.sleep(0.5)
                        await page.keyboard.press('Enter')
                    
                    await asyncio.sleep(1)
                    
                    # ====== 步骤2: 填写机身储存 ======
                    print("\n=== 填写机身储存 ===")
                    
                    # 滚动到机身储存
                    await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === '机身储存') {
                                var formItem = labels[i].closest('.ant-form-item');
                                if (formItem) formItem.scrollIntoViewIfNeeded();
                            }
                        }
                    }''')
                    
                    # 点击机身储存下拉框 (第4个ant-select)
                    selects = await frame.locator('.ant-select').all()
                    if len(selects) >= 4:
                        storage_select = selects[3]
                        await storage_select.click(force=True, timeout=5000)
                        await asyncio.sleep(0.8)
                        
                        # 检查下拉菜单
                        visible_dropdown = None
                        dropdowns = await frame.query_selector_all('.ant-select-dropdown')
                        for d in dropdowns:
                            style = await d.get_attribute('style')
                            if style and 'display: none' not in style:
                                visible_dropdown = d
                                break
                        
                        if visible_dropdown:
                            print("机身储存下拉菜单已打开!")
                            items = await visible_dropdown.query_selector_all('.ant-select-item-option-content')
                            for item in items:
                                text = await item.text_content()
                                print(f"  选项: {text.strip()}")
                                if '256GB' in text and '定制版' not in text:
                                    print(f"  -> 选择: {text.strip()}")
                                    await item.click()
                                    break
                    
                    await asyncio.sleep(1)
                    
                    # ====== 步骤3: 填写运行内存 ======
                    print("\n=== 填写运行内存 ===")
                    
                    # 滚动到运行内存
                    await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === '运行内存') {
                                var formItem = labels[i].closest('.ant-form-item');
                                if (formItem) formItem.scrollIntoViewIfNeeded();
                            }
                        }
                    }''')
                    
                    # 点击运行内存下拉框 (第5个ant-select)
                    selects = await frame.locator('.ant-select').all()
                    if len(selects) >= 5:
                        ram_select = selects[4]
                        await ram_select.click(force=True, timeout=5000)
                        await asyncio.sleep(0.8)
                        
                        # 检查下拉菜单
                        visible_dropdown = None
                        dropdowns = await frame.query_selector_all('.ant-select-dropdown')
                        for d in dropdowns:
                            style = await d.get_attribute('style')
                            if style and 'display: none' not in style:
                                visible_dropdown = d
                                break
                        
                        if visible_dropdown:
                            print("运行内存下拉菜单已打开!")
                            items = await visible_dropdown.query_selector_all('.ant-select-item-option-content')
                            for item in items:
                                text = await item.text_content()
                                print(f"  选项: {text.strip()}")
                                if '8GB' in text and '哈利' not in text:
                                    print(f"  -> 选择: {text.strip()}")
                                    await item.click()
                                    break
                    
                    print("\n=== 完成 ===")
                        
        await browser.close()

asyncio.run(fill_all())
