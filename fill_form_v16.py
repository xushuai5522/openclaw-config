#!/usr/bin/env python3
"""
强制点击被遮挡的元素
"""
import asyncio
from playwright.async_api import async_playwright

async def force_click():
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
                    
                    # 按Escape取消激活
                    await page.keyboard.press('Escape')
                    await asyncio.sleep(0.5)
                    
                    # 先滚动到CPU区域
                    print("滚动到CPU区域")
                    await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === 'CPU') {
                                var formItem = labels[i].closest('.ant-form-item');
                                if (formItem) {
                                    formItem.scrollIntoViewIfNeeded();
                                }
                            }
                        }
                    }''')
                    
                    await asyncio.sleep(0.5)
                    
                    # 使用force=True强制点击
                    print("尝试强制点击CPU下拉框")
                    
                    # 先获取CPU下拉框的信息
                    cpu_info = await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === 'CPU') {
                                var formItem = labels[i].closest('.ant-form-item');
                                if (formItem) {
                                    var select = formItem.querySelector('.ant-select');
                                    if (select) {
                                        var rect = select.getBoundingClientRect();
                                        return {
                                            found: true,
                                            rect: {x: rect.x, y: rect.y, w: rect.width, h: rect.height}
                                        };
                                    }
                                }
                            }
                        }
                        return {found: false};
                    }''')
                    
                    print(f"CPU元素信息: {cpu_info}")
                    
                    # 使用locator并force=True
                    try:
                        # 找到所有ant-select，获取CPU对应的那个
                        selects = await frame.locator('.ant-select').all()
                        print(f"找到 {len(selects)} 个ant-select")
                        
                        # CPU应该是第3个（索引2）- 品牌、型号、CPU
                        if len(selects) >= 3:
                            cpu_select = selects[2]
                            print("尝试点击第3个ant-select (CPU)")
                            await cpu_select.click(force=True, timeout=5000)
                            print("点击成功!")
                    except Exception as e:
                        print(f"点击失败: {e}")
                    
                    await asyncio.sleep(1)
                    
                    # 检查下拉菜单
                    dropdowns = await frame.query_selector_all('.ant-select-dropdown')
                    for i, d in enumerate(dropdowns):
                        style = await d.get_attribute('style')
                        if style and 'display: none' not in style:
                            print(f"\n下拉菜单 {i} 可见!")
                            items = await d.query_selector_all('.ant-select-item-option-content')
                            for item in items[:10]:
                                text = await item.text_content()
                                print(f"  选项: {text.strip()}")
                    
                    print("\n完成")
                        
        await browser.close()

asyncio.run(force_click())
