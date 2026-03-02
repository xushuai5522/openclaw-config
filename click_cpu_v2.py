#!/usr/bin/env python3
"""
点击rrzuji iframe内的CPU下拉框
"""
import asyncio
from playwright.async_api import async_playwright

async def click_cpu():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        
        for ctx in browser.contexts:
            for page in ctx.pages:
                if "id=801233" in page.url:
                    print("找到目标页面")
                    
                    # 等待页面完全加载
                    await page.wait_for_load_state("domcontentloaded")
                    await asyncio.sleep(2)  # 等待iframe加载
                    
                    # 尝试不同的方法获取frame
                    # 方法1: 通过name
                    frame = page.frame(name='rrzuji')
                    if frame:
                        print(f"通过name获取到frame: {frame.url}")
                    else:
                        # 方法2: 通过URL模式
                        frames = page.frames
                        for f in frames:
                            if 'admin-vue' in f.url or 'commodity/edit' in f.url:
                                frame = f
                                print(f"通过URL获取到frame: {f.url}")
                                break
                    
                    if frame:
                        print(f"Frame URL: {frame.url}")
                        
                        # 等待frame加载
                        await frame.wait_for_load_state("domcontentloaded")
                        await asyncio.sleep(1)
                        
                        # 查找包含"CPU"文本的元素
                        # 先尝试查找label
                        cpu_label = await frame.get_by_text("CPU").first()
                        if cpu_label:
                            print(f"找到CPU label: {cpu_label}")
                            # 找到label后的下一个comboBox
                            # 尝试点击label或者label后面的元素
                            
                            # 使用evaluate来点击
                            await cpu_label.click()
                            print("点击了CPU label")
                            await asyncio.sleep(1)
                            
                            # 检查是否打开了下拉框
                            # 查找所有下拉选项
                            dropdown_items = await frame.query_selector_all('.ant-select-dropdown, .ant-select-menu, [class*="dropdown"], [class*="select-menu"]')
                            print(f"找到 {len(dropdown_items)} 个下拉菜单")
                            
                        # 尝试查找类目属性区域
                        # 先滚动到类目属性区域
                        try:
                            category_attrs = await frame.get_by_text("类目属性").first()
                            if category_attrs:
                                print("找到'类目属性'区域")
                                await category_attrs.scroll_into_view_if_needed()
                                await asyncio.sleep(0.5)
                        except Exception as e:
                            print(f"滚动失败: {e}")
                        
                        # 尝试查找所有下拉框
                        combos = await frame.query_selector_all('input.ant-select-selection-search-input, .ant-select-selector, input[placeholder="请选择"]')
                        print(f"找到 {len(combos)} 个可能的下拉框")
                        
                        # 尝试查找包含"请选择"的下拉框
                        for i, combo in enumerate(combos):
                            try:
                                placeholder = await combo.get_attribute('placeholder')
                                aria_label = await combo.get_attribute('aria-label')
                                print(f"Combo {i}: placeholder={placeholder}, aria_label={aria_label}")
                            except:
                                pass
                                
                    else:
                        print("未获取到iframe的frame")
                        
        await browser.close()

asyncio.run(click_cpu())
