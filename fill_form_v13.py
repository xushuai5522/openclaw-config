#!/usr/bin/env python3
"""
使用JavaScript直接点击CPU下拉框
"""
import asyncio
from playwright.async_api import async_playwright

async def click_with_js():
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
                    
                    # 使用JavaScript直接点击CPU下拉框
                    print("点击CPU下拉框")
                    cpu_click = await frame.evaluate('''() => {
                        // 按Escape取消激活状态
                        document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
                        
                        // 找到CPU下拉框
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === 'CPU') {
                                var formItem = labels[i].closest('.ant-form-item');
                                if (formItem) {
                                    var select = formItem.querySelector('.ant-select');
                                    if (select) {
                                        // 滚动到可见区域
                                        select.scrollIntoViewIfNeeded();
                                        
                                        // 使用JavaScript点击
                                        var rect = select.getBoundingClientRect();
                                        var centerX = rect.left + rect.width / 2;
                                        var centerY = rect.top + rect.height / 2;
                                        
                                        // 触发完整的点击事件序列
                                        select.dispatchEvent(new MouseEvent('mousedown', {
                                            bubbles: true,
                                            cancelable: true,
                                            view: window,
                                            clientX: centerX,
                                            clientY: centerY
                                        }));
                                        
                                        select.dispatchEvent(new MouseEvent('mouseup', {
                                            bubbles: true,
                                            cancelable: true,
                                            view: window,
                                            clientX: centerX,
                                            clientY: centerY
                                        }));
                                        
                                        select.click();
                                        
                                        return {success: true, msg: '点击了CPU'};
                                    }
                                }
                            }
                        }
                        
                        return {success: false, msg: '未找到CPU'};
                    }''')
                    
                    print(f"CPU点击: {cpu_click}")
                    await asyncio.sleep(1.5)
                    
                    # 检查下拉菜单
                    dropdown_info = await frame.evaluate('''() => {
                        var dropdowns = document.querySelectorAll('.ant-select-dropdown');
                        var result = [];
                        for (var i = 0; i < dropdowns.length; i++) {
                            var d = dropdowns[i];
                            var style = d.getAttribute('style') || '';
                            var isVisible = style.indexOf('display: none') === -1;
                            result.push({
                                visible: isVisible,
                                style: style.substring(0, 100)
                            });
                            
                            if (isVisible) {
                                var items = d.querySelectorAll('.ant-select-item-option-content');
                                var itemTexts = [];
                                for (var j = 0; j < Math.min(items.length, 20); j++) {
                                    itemTexts.push(items[j].textContent.trim());
                                }
                                result[i].items = itemTexts;
                            }
                        }
                        return result;
                    }''')
                    
                    print(f"下拉菜单状态: {dropdown_info}")
                    
                    # 如果找到了CPU选项（包含"骁龙"），则选择
                    for d in dropdown_info:
                        if d.get('items'):
                            for item in d['items']:
                                if '骁龙8' in item:
                                    print(f"选择CPU: {item}")
                                    await frame.evaluate('''(itemText) => {
                                        var items = document.querySelectorAll('.ant-select-item-option-content');
                                        for (var i = 0; i < items.length; i++) {
                                            if (items[i].textContent.trim() === itemText) {
                                                items[i].click();
                                            }
                                        }
                                    }''', item)
                                    break
                    
                    await asyncio.sleep(1)
                    
                    # 继续填写机身储存
                    print("\n点击机身储存下拉框")
                    storage_click = await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === '机身储存') {
                                var formItem = labels[i].closest('.ant-form-item');
                                if (formItem) {
                                    var select = formItem.querySelector('.ant-select');
                                    if (select) {
                                        select.scrollIntoViewIfNeeded();
                                        select.click();
                                        return {success: true};
                                    }
                                }
                            }
                        }
                        return {success: false};
                    }''')
                    
                    print(f"机身储存: {storage_click}")
                    await asyncio.sleep(1)
                    
                    # 检查机身储存选项
                    storage_dropdown = await frame.evaluate('''() => {
                        var dropdowns = document.querySelectorAll('.ant-select-dropdown');
                        for (var i = 0; i < dropdowns.length; i++) {
                            var d = dropdowns[i];
                            var style = d.getAttribute('style') || '';
                            if (style.indexOf('display: none') === -1) {
                                var items = d.querySelectorAll('.ant-select-item-option-content');
                                var result = [];
                                for (var j = 0; j < items.length; j++) {
                                    result.push(items[j].textContent.trim());
                                }
                                return {items: result};
                            }
                        }
                        return {error: '未找到'};
                    }''')
                    
                    print(f"机身储存选项: {storage_dropdown}")
                    
                    if 'items' in storage_dropdown:
                        for item in storage_dropdown['items']:
                            if '256GB' in item:
                                print(f"选择机身储存: {item}")
                                await frame.evaluate('''(itemText) => {
                                    var items = document.querySelectorAll('.ant-select-item-option-content');
                                    for (var i = 0; i < items.length; i++) {
                                        if (items[i].textContent.trim() === itemText) {
                                            items[i].click();
                                        }
                                    }
                                }''', item)
                                break
                    
                    await asyncio.sleep(1)
                    
                    # 填写运行内存
                    print("\n点击运行内存下拉框")
                    ram_click = await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === '运行内存') {
                                var formItem = labels[i].closest('.ant-form-item');
                                if (formItem) {
                                    var select = formItem.querySelector('.ant-select');
                                    if (select) {
                                        select.scrollIntoViewIfNeeded();
                                        select.click();
                                        return {success: true};
                                    }
                                }
                            }
                        }
                        return {success: false};
                    }''')
                    
                    print(f"运行内存: {ram_click}")
                    await asyncio.sleep(1)
                    
                    # 检查运行内存选项
                    ram_dropdown = await frame.evaluate('''() => {
                        var dropdowns = document.querySelectorAll('.ant-select-dropdown');
                        for (var i = 0; i < dropdowns.length; i++) {
                            var d = dropdowns[i];
                            var style = d.getAttribute('style') || '';
                            if (style.indexOf('display: none') === -1) {
                                var items = d.querySelectorAll('.ant-select-item-option-content');
                                var result = [];
                                for (var j = 0; j < items.length; j++) {
                                    result.push(items[j].textContent.trim());
                                }
                                return {items: result};
                            }
                        }
                        return {error: '未找到'};
                    }''')
                    
                    print(f"运行内存选项: {ram_dropdown}")
                    
                    if 'items' in ram_dropdown:
                        for item in ram_dropdown['items']:
                            if '8GB' in item and '哈利' not in item:
                                print(f"选择运行内存: {item}")
                                await frame.evaluate('''(itemText) => {
                                    var items = document.querySelectorAll('.ant-select-item-option-content');
                                    for (var i = 0; i < items.length; i++) {
                                        if (items[i].textContent.trim() === itemText) {
                                            items[i].click();
                                        }
                                    }
                                }''', item)
                                break
                    
                    print("\n完成!")
                        
        await browser.close()

asyncio.run(click_with_js())
