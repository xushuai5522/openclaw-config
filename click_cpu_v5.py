#!/usr/bin/env python3
"""
点击rrzuji iframe内的CPU下拉框 - v5 (更精确)
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
                        continue
                    
                    await frame.wait_for_load_state("domcontentloaded")
                    await asyncio.sleep(2)
                    
                    # 详细分析CPU区域的HTML结构
                    analysis = await frame.evaluate('''() => {
                        var result = {};
                        
                        // 找到所有包含CPU的行
                        var allDivs = document.querySelectorAll('div.ant-row, div.ant-col, .ant-form-item');
                        var cpuSection = null;
                        
                        for (var i = 0; i < allDivs.length; i++) {
                            var div = allDivs[i];
                            if (div.textContent.indexOf('CPU') !== -1 && div.textContent.indexOf('机身储存') === -1) {
                                cpuSection = div;
                                break;
                            }
                        }
                        
                        if (cpuSection) {
                            result.cpuHTML = cpuSection.outerHTML.substring(0, 1500);
                            
                            // 查找所有ant-select元素
                            var selects = cpuSection.querySelectorAll('.ant-select');
                            result.selectCount = selects.length;
                            
                            // 查找form_item_289相关元素
                            var cpuInputWrapper = document.getElementById('form_item_289');
                            if (cpuInputWrapper) {
                                result.cpuInputWrapper = cpuInputWrapper.outerHTML.substring(0, 500);
                            }
                            
                            // 查找下一个ant-form-item
                            var nextItem = cpuSection.nextElementSibling;
                            if (nextItem) {
                                result.nextItemHTML = nextItem.outerHTML.substring(0, 800);
                            }
                        }
                        
                        return result;
                    }''')
                    
                    print("CPU区域分析:")
                    print(f"  CPU HTML: {analysis.get('cpuHTML', 'N/A')[:500]}")
                    print(f"  Select数量: {analysis.get('selectCount', 0)}")
                    print(f"  CPU输入框包装器: {analysis.get('cpuInputWrapper', 'N/A')}")
                    print(f"  下一个表单项: {analysis.get('nextItemHTML', 'N/A')[:300]}")
                    
                    # 尝试使用不同的点击方式
                    click_result = await frame.evaluate('''() => {
                        // 找到CPU行的下一个兄弟元素（包含下拉框）
                        var allDivs = document.querySelectorAll('div.ant-row, div.ant-col, .ant-form-item');
                        var cpuSection = null;
                        
                        for (var i = 0; i < allDivs.length; i++) {
                            if (allDivs[i].textContent.trim().startsWith('CPU') && allDivs[i].textContent.indexOf('机身储存') === -1) {
                                cpuSection = allDivs[i];
                                break;
                            }
                        }
                        
                        if (cpuSection) {
                            // 查找CPU后面的下拉框
                            var next = cpuSection.nextElementSibling;
                            while (next) {
                                var select = next.querySelector('.ant-select, .ant-select-selection');
                                if (select) {
                                    console.log('找到CPU下拉框');
                                    // 尝试触发真实的点击事件
                                    var rect = select.getBoundingClientRect();
                                    var centerX = rect.left + rect.width / 2;
                                    var centerY = rect.top + rect.height / 2;
                                    
                                    // 模拟鼠标移动和点击
                                    select.dispatchEvent(new MouseEvent('mousedown', {
                                        bubbles: true,
                                        cancelable: true,
                                        clientX: centerX,
                                        clientY: centerY
                                    }));
                                    
                                    select.dispatchEvent(new MouseEvent('mouseup', {
                                        bubbles: true,
                                        cancelable: true,
                                        clientX: centerX,
                                        clientY: centerY
                                    }));
                                    
                                    select.click();
                                    return {success: true, method: 'nextSibling'};
                                }
                                next = next.nextElementSibling;
                            }
                        }
                        
                        // 备用：直接查找ID
                        var cpuInput = document.getElementById('form_item_289');
                        if (cpuInput) {
                            console.log('尝试点击form_item_289');
                            var parent = cpuInput.parentElement;
                            while (parent) {
                                var sel = parent.querySelector('.ant-select');
                                if (sel) {
                                    sel.click();
                                    return {success: true, method: 'form_item_289'};
                                }
                                parent = parent.parentElement;
                            }
                        }
                        
                        return {success: false, msg: '未找到'};
                    }''')
                    
                    print(f"点击结果: {click_result}")
                    await asyncio.sleep(1)
                    
        await browser.close()

asyncio.run(click_cpu())
