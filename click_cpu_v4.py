#!/usr/bin/env python3
"""
点击rrzuji iframe内的CPU下拉框 - v4 (修复语法)
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
                    
                    frame = page.frame(name='rrzuji')
                    if not frame:
                        print("未获取到frame")
                        await browser.close()
                        return
                    
                    # 等待加载
                    await frame.wait_for_load_state("domcontentloaded")
                    await asyncio.sleep(2)
                    
                    # 点击CPU下拉框
                    click_result = await frame.evaluate('''() => {
                        // 查找label为"CPU"的元素
                        var labels = document.querySelectorAll('label[title="CPU"], div.ant-form-item-label label');
                        var cpuLabel = null;
                        
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.trim() === 'CPU') {
                                cpuLabel = labels[i];
                                break;
                            }
                        }
                        
                        if (!cpuLabel) {
                            // 尝试其他方式
                            var allDivs = document.querySelectorAll('div');
                            for (var j = 0; j < allDivs.length; j++) {
                                if (allDivs[j].textContent.trim() === 'CPU') {
                                    cpuLabel = allDivs[j];
                                    break;
                                }
                            }
                        }
                        
                        if (cpuLabel) {
                            console.log('找到CPU label');
                            
                            // 找到对应的form-item-control
                            var formItem = cpuLabel.closest('.ant-form-item');
                            if (formItem) {
                                console.log('找到form-item');
                                
                                // 查找下拉框
                                var control = formItem.querySelector('.ant-form-item-control');
                                if (control) {
                                    var select = control.querySelector('.ant-select, input');
                                    if (select) {
                                        console.log('找到select元素，尝试点击');
                                        select.click();
                                        return {success: true, msg: '点击成功'};
                                    }
                                }
                                
                                // 尝试直接点击
                                var controlNode = formItem.nextElementSibling;
                                if (controlNode && controlNode.querySelector) {
                                    var selectBtn = controlNode.querySelector('.ant-select');
                                    if (selectBtn) {
                                        selectBtn.click();
                                        return {success: true, msg: '点击下一个兄弟元素成功'};
                                    }
                                }
                            }
                        }
                        
                        // 备用方案：直接通过form_item_289点击
                        var cpuInput = document.getElementById('form_item_289');
                        if (cpuInput) {
                            console.log('通过ID找到CPU输入框');
                            cpuInput.click();
                            return {success: true, msg: '点击ID元素成功'};
                        }
                        
                        return {success: false, msg: '未找到CPU下拉框'};
                    }''')
                    
                    print(f"点击结果: {click_result}")
                    
                    # 等待看是否打开了下拉框
                    await asyncio.sleep(1)
                    
                    # 检查是否有下拉菜单出现
                    dropdown = await frame.query_selector('.ant-select-dropdown:not([style*="display: none"])')
                    if dropdown:
                        print("下拉菜单已打开!")
                    else:
                        print("下拉菜单未打开")
                        
        await browser.close()

asyncio.run(click_cpu())
