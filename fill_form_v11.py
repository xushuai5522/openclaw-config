#!/usr/bin/env python3
"""
点击CPU下拉框并查看选项
"""
import asyncio
from playwright.async_api import async_playwright

async def check_dropdown():
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
                    
                    # 点击CPU下拉框
                    print("点击CPU下拉框")
                    await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === 'CPU') {
                                var formItem = labels[i].closest('.ant-form-item');
                                var select = formItem.querySelector('.ant-select');
                                if (select) {
                                    select.click();
                                }
                            }
                        }
                    }''')
                    
                    await asyncio.sleep(1)
                    
                    # 获取下拉菜单选项
                    options = await frame.evaluate('''() => {
                        var dropdown = document.querySelector('.ant-select-dropdown');
                        if (!dropdown) {
                            return {error: '未找到下拉菜单'};
                        }
                        
                        var items = dropdown.querySelectorAll('.ant-select-item, .ant-select-menu-item');
                        var result = [];
                        for (var i = 0; i < items.length; i++) {
                            var item = items[i];
                            result.push({
                                text: item.textContent.trim(),
                                html: item.outerHTML.substring(0, 200),
                                class: item.className
                            });
                        }
                        
                        return {
                            count: items.length,
                            items: result,
                            dropdownHTML: dropdown.outerHTML.substring(0, 500)
                        };
                    }''')
                    
                    print(f"CPU下拉菜单选项: {options}")
                    
                    # 如果找到了选项，选择第一个包含"骁龙"的
                    if 'items' in options:
                        for item in options['items']:
                            if '骁龙' in item['text']:
                                print(f"选择: {item['text']}")
                                # 使用JavaScript点击
                                await frame.evaluate('''(text) => {
                                    var items = document.querySelectorAll('.ant-select-item, .ant-select-menu-item');
                                    for (var i = 0; i < items.length; i++) {
                                        if (items[i].textContent.trim().indexOf(text) !== -1) {
                                            items[i].click();
                                        }
                                    }
                                }''', item['text'])
                                break
                    
                    await asyncio.sleep(1)
                    
                    # 继续填写机身储存
                    print("\n点击机身储存下拉框")
                    await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === '机身储存') {
                                var formItem = labels[i].closest('.ant-form-item');
                                var select = formItem.querySelector('.ant-select');
                                if (select) {
                                    select.click();
                                }
                            }
                        }
                    }''')
                    
                    await asyncio.sleep(1)
                    
                    # 获取机身储存选项
                    storage_options = await frame.evaluate('''() => {
                        var dropdown = document.querySelector('.ant-select-dropdown');
                        if (!dropdown) {
                            return {error: '未找到下拉菜单'};
                        }
                        
                        var items = dropdown.querySelectorAll('.ant-select-item, .ant-select-menu-item');
                        var result = [];
                        for (var i = 0; i < items.length; i++) {
                            result.push(items[i].textContent.trim());
                        }
                        return {count: items.length, items: result};
                    }''')
                    
                    print(f"机身储存选项: {storage_options}")
                    
                    # 选择256GB
                    if 'items' in storage_options:
                        for item in storage_options['items']:
                            if '256GB' in item:
                                print(f"选择: {item}")
                                await frame.evaluate('''(text) => {
                                    var items = document.querySelectorAll('.ant-select-item, .ant-select-menu-item');
                                    for (var i = 0; i < items.length; i++) {
                                        if (items[i].textContent.trim().indexOf(text) !== -1) {
                                            items[i].click();
                                        }
                                    }
                                }''', item)
                                break
                    
                    await asyncio.sleep(1)
                    
                    # 继续填写运行内存
                    print("\n点击运行内存下拉框")
                    await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === '运行内存') {
                                var formItem = labels[i].closest('.ant-form-item');
                                var select = formItem.querySelector('.ant-select');
                                if (select) {
                                    select.click();
                                }
                            }
                        }
                    }''')
                    
                    await asyncio.sleep(1)
                    
                    # 获取运行内存选项
                    ram_options = await frame.evaluate('''() => {
                        var dropdown = document.querySelector('.ant-select-dropdown');
                        if (!dropdown) {
                            return {error: '未找到下拉菜单'};
                        }
                        
                        var items = dropdown.querySelectorAll('.ant-select-item, .ant-select-menu-item');
                        var result = [];
                        for (var i = 0; i < items.length; i++) {
                            result.push(items[i].textContent.trim());
                        }
                        return {count: items.length, items: result};
                    }''')
                    
                    print(f"运行内存选项: {ram_options}")
                    
                    # 选择8GB
                    if 'items' in ram_options:
                        for item in ram_options['items']:
                            if '8GB' in item:
                                print(f"选择: {item}")
                                await frame.evaluate('''(text) => {
                                    var items = document.querySelectorAll('.ant-select-item, .ant-select-menu-item');
                                    for (var i = 0; i < items.length; i++) {
                                        if (items[i].textContent.trim().indexOf(text) !== -1) {
                                            items[i].click();
                                        }
                                    }
                                }''', item)
                                break
                    
                    print("\n完成所有选择")
                        
        await browser.close()

asyncio.run(check_dropdown())
