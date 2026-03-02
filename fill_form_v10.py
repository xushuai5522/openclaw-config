#!/usr/bin/env python3
"""
点击CPU下拉框并选择选项
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
                    
                    # 步骤1: 点击CPU下拉框
                    print("步骤1: 点击CPU下拉框")
                    cpu_click = await frame.evaluate('''() => {
                        var select = document.querySelector('div[data-fieldid="cpu"] .ant-select');
                        if (!select) {
                            // 找到CPU label后面的下拉框
                            var labels = document.querySelectorAll('.ant-form-item-label label');
                            for (var i = 0; i < labels.length; i++) {
                                if (labels[i].textContent.trim() === 'CPU') {
                                    var formItem = labels[i].closest('.ant-form-item');
                                    var select = formItem.querySelector('.ant-select');
                                    if (select) {
                                        select.click();
                                        return {success: true};
                                    }
                                }
                            }
                        }
                        if (select) {
                            select.click();
                            return {success: true};
                        }
                        return {success: false, msg: '未找到CPU下拉框'};
                    }''')
                    
                    print(f"CPU点击: {cpu_click}")
                    await asyncio.sleep(1)
                    
                    # 检查下拉菜单是否出现
                    dropdown = await frame.query_selector('.ant-select-dropdown')
                    if dropdown:
                        print("CPU下拉菜单已打开!")
                        
                        # 选择"骁龙8 Gen 2"
                        print("尝试选择骁龙8 Gen 2")
                        await frame.click('text=骁龙8', timeout=5000)
                        print("点击了选项")
                    else:
                        print("CPU下拉菜单未打开，尝试强制打开")
                        
                        # 尝试强制打开
                        force_open = await frame.evaluate('''() => {
                            var input = document.getElementById('form_item_289');
                            if (input) {
                                // 尝试打开下拉框
                                input.focus();
                                input.dispatchEvent(new Event('mousedown'));
                                input.dispatchEvent(new Event('click'));
                                
                                // 尝试模拟按下键
                                input.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowDown', bubbles: true}));
                                return {success: true, msg: '尝试打开'};
                            }
                            return {success: false};
                        }''')
                        print(f"强制打开: {force_open}")
                        await asyncio.sleep(1)
                        
                        # 再次检查
                        dropdown = await frame.query_selector('.ant-select-dropdown')
                        if dropdown:
                            print("下拉菜单现在打开了!")
                    
                    # 步骤2: 点击机身储存下拉框
                    print("\n步骤2: 点击机身储存下拉框")
                    storage_click = await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === '机身储存') {
                                var formItem = labels[i].closest('.ant-form-item');
                                var select = formItem.querySelector('.ant-select');
                                if (select) {
                                    select.click();
                                    return {success: true};
                                }
                            }
                        }
                        return {success: false};
                    }''')
                    
                    print(f"机身储存点击: {storage_click}")
                    await asyncio.sleep(1)
                    
                    # 步骤3: 点击运行内存下拉框  
                    print("\n步骤3: 点击运行内存下拉框")
                    ram_click = await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === '运行内存') {
                                var formItem = labels[i].closest('.ant-form-item');
                                var select = formItem.querySelector('.ant-select');
                                if (select) {
                                    select.click();
                                    return {success: true};
                                }
                            }
                        }
                        return {success: false};
                    }''')
                    
                    print(f"运行内存点击: {ram_click}")
                    
                    print("\n完成点击操作")
                        
        await browser.close()

asyncio.run(fill_form())
