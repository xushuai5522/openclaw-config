#!/usr/bin/env python3
"""
正确点击CPU下拉框
"""
import asyncio
from playwright.async_api import async_playwright

async def click_correct_dropdown():
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
                    
                    # 先点击页面其他位置取消品牌下拉框的激活状态
                    print("取消激活状态")
                    await frame.click('.ant-form-item-label', timeout=3000)
                    await asyncio.sleep(0.5)
                    
                    # 找到CPU下拉框并点击
                    # 根据DOM结构，CPU的form_item_289
                    print("点击CPU下拉框")
                    cpu_click = await frame.evaluate('''() => {
                        // 找到CPU label
                        var labels = document.querySelectorAll('.ant-form-item-label label[title="CPU"]');
                        if (labels.length === 0) {
                            // 尝试其他方式
                            var allLabels = document.querySelectorAll('.ant-form-item-label label');
                            for (var i = 0; i < allLabels.length; i++) {
                                if (allLabels[i].textContent.trim() === 'CPU') {
                                    labels = [allLabels[i]];
                                    break;
                                }
                            }
                        }
                        
                        if (labels.length > 0) {
                            // 找到form-item
                            var formItem = labels[0].closest('.ant-form-item');
                            if (formItem) {
                                // 找到ant-select元素
                                var select = formItem.querySelector('.ant-select');
                                if (select) {
                                    select.click();
                                    return {success: true, msg: '点击了CPU下拉框'};
                                }
                            }
                        }
                        
                        // 备用：直接通过ID查找
                        var input = document.getElementById('form_item_289');
                        if (input) {
                            var parent = input.parentElement;
                            while (parent) {
                                if (parent.classList && parent.classList.contains('ant-select')) {
                                    parent.click();
                                    return {success: true, msg: '通过ID点击了CPU'};
                                }
                                parent = parent.parentElement;
                            }
                        }
                        
                        return {success: false, msg: '未找到CPU下拉框'};
                    }''')
                    
                    print(f"CPU点击: {cpu_click}")
                    await asyncio.sleep(1)
                    
                    # 检查下拉菜单
                    dropdown = await frame.query_selector('.ant-select-dropdown')
                    if dropdown:
                        # 获取选项
                        options = await frame.evaluate('''() => {
                            var dropdown = document.querySelector('.ant-select-dropdown:not([style*="display: none"])');
                            if (!dropdown) {
                                // 检查所有下拉菜单
                                dropdown = document.querySelector('.ant-select-dropdown');
                            }
                            if (dropdown) {
                                var items = dropdown.querySelectorAll('.ant-select-item-option-content');
                                var result = [];
                                for (var i = 0; i < items.length; i++) {
                                    result.push(items[i].textContent.trim());
                                }
                                return {count: result.length, items: result};
                            }
                            return {error: '无下拉菜单'};
                        }''')
                        print(f"CPU选项: {options}")
                        
                        # 选择"骁龙8 Gen 2"
                        if 'items' in options:
                            for item in options['items']:
                                if '骁龙8' in item:
                                    print(f"选择: {item}")
                                    await frame.evaluate('''(text) => {
                                        var items = document.querySelectorAll('.ant-select-item-option-content');
                                        for (var i = 0; i < items.length; i++) {
                                            if (items[i].textContent.trim().indexOf(text) !== -1) {
                                                items[i].click();
                                            }
                                        }
                                    }''', item)
                                    break
                    
                    await asyncio.sleep(1)
                    
                    # 同样方法填写机身储存
                    print("\n点击机身储存下拉框")
                    storage_click = await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label[title="机身储存"]');
                        if (labels.length === 0) {
                            var allLabels = document.querySelectorAll('.ant-form-item-label label');
                            for (var i = 0; i < allLabels.length; i++) {
                                if (allLabels[i].textContent.trim() === '机身储存') {
                                    labels = [allLabels[i]];
                                    break;
                                }
                            }
                        }
                        
                        if (labels.length > 0) {
                            var formItem = labels[0].closest('.ant-form-item');
                            if (formItem) {
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
                    
                    # 获取并选择机身储存选项
                    storage_options = await frame.evaluate('''() => {
                        var dropdown = document.querySelector('.ant-select-dropdown:not([style*="display: none"])');
                        if (dropdown) {
                            var items = dropdown.querySelectorAll('.ant-select-item-option-content');
                            var result = [];
                            for (var i = 0; i < items.length; i++) {
                                result.push(items[i].textContent.trim());
                            }
                            return {count: result.length, items: result};
                        }
                        return {error: '无下拉菜单'};
                    }''')
                    
                    print(f"机身储存选项: {storage_options}")
                    
                    if 'items' in storage_options:
                        for item in storage_options['items']:
                            if '256GB' in item and '定制版' not in item:
                                print(f"选择: {item}")
                                await frame.evaluate('''(text) => {
                                    var items = document.querySelectorAll('.ant-select-item-option-content');
                                    for (var i = 0; i < items.length; i++) {
                                        if (items[i].textContent.trim().indexOf(text) !== -1) {
                                            items[i].click();
                                        }
                                    }
                                }''', item)
                                break
                    
                    await asyncio.sleep(1)
                    
                    # 填写运行内存
                    print("\n点击运行内存下拉框")
                    ram_click = await frame.evaluate('''() => {
                        var labels = document.querySelectorAll('.ant-form-item-label label[title="运行内存"]');
                        if (labels.length === 0) {
                            var allLabels = document.querySelectorAll('.ant-form-item-label label');
                            for (var i = 0; i < allLabels.length; i++) {
                                if (allLabels[i].textContent.trim() === '运行内存') {
                                    labels = [allLabels[i]];
                                    break;
                                }
                            }
                        }
                        
                        if (labels.length > 0) {
                            var formItem = labels[0].closest('.ant-form-item');
                            if (formItem) {
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
                    await asyncio.sleep(1)
                    
                    # 获取并选择运行内存选项
                    ram_options = await frame.evaluate('''() => {
                        var dropdown = document.querySelector('.ant-select-dropdown:not([style*="display: none"])');
                        if (dropdown) {
                            var items = dropdown.querySelectorAll('.ant-select-item-option-content');
                            var result = [];
                            for (var i = 0; i < items.length; i++) {
                                result.push(items[i].textContent.trim());
                            }
                            return {count: result.length, items: result};
                        }
                        return {error: '无下拉菜单'};
                    }''')
                    
                    print(f"运行内存选项: {ram_options}")
                    
                    if 'items' in ram_options:
                        for item in ram_options['items']:
                            if '8GB' in item:
                                print(f"选择: {item}")
                                await frame.evaluate('''(text) => {
                                    var items = document.querySelectorAll('.ant-select-item-option-content');
                                    for (var i = 0; i < items.length; i++) {
                                        if (items[i].textContent.trim().indexOf(text) !== -1) {
                                            items[i].click();
                                        }
                                    }
                                }''', item)
                                break
                    
                    print("\n完成!")
                        
        await browser.close()

asyncio.run(click_correct_dropdown())
