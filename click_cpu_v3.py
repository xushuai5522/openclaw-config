#!/usr/bin/env python3
"""
点击rrzuji iframe内的CPU下拉框 - v3
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
                    
                    # 获取frame
                    frame = page.frame(name='rrzuji')
                    if not frame:
                        print("未获取到frame")
                        await browser.close()
                        return
                    
                    print(f"Frame URL: {frame.url}")
                    
                    # 等待frame加载
                    await frame.wait_for_load_state("domcontentloaded")
                    await asyncio.sleep(2)
                    
                    # 使用JavaScript直接执行点击
                    # 查找页面中包含"CPU"文本的元素
                    result = await frame.evaluate('''() => {
                        // 查找所有包含"CPU"文本的元素
                        const elements = document.querySelectorAll('*');
                        let cpuElement = null;
                        
                        for (let el of elements) {
                            if (el.textContent === 'CPU' && el.tagName !== 'SCRIPT') {
                                console.log('找到CPU元素:', el.tagName, el.className);
                                cpuElement = el;
                                break;
                            }
                        }
                        
                        // 尝试找到CPU下拉框 - 通常在CPU label后面
                        // 查找form表单中的字段
                        const forms = document.querySelectorAll('form');
                        console.log('找到', forms.length, '个form');
                        
                        // 查找所有输入框和选择框
                        const inputs = document.querySelectorAll('input, select, textarea');
                        console.log('找到', inputs.length, '个输入元素');
                        
                        // 尝试查找ant-select组件
                        const selects = document.querySelectorAll('.ant-select, [class*="select"]');
                        console.log('找到', selects.length, '个select组件');
                        
                        return {
                            cpuFound: cpuElement ? cpuElement.outerHTML : null,
                            formCount: forms.length,
                            inputCount: inputs.length,
                            selectCount: selects.length
                        };
                    }''')
                    
                    print(f"分析结果: {result}")
                    
                    # 尝试直接点击CPU下拉框 - 使用更精确的JavaScript
                    click_result = await frame.evaluate('''() => {
                        // 方法1: 查找label为"CPU"后面的下拉框
                        const labels = document.querySelectorAll('label, span, div');
                        let cpuLabel = null;
                        
                        for (let el of labels) {
                            if (el.textContent.trim() === 'CPU') {
                                cpuLabel = el;
                                console.log('找到CPU label:', el);
                                break;
                            }
                        }
                        
                        if (cpuLabel) {
                            // 尝试找下一个兄弟元素
                            let sibling = cpuLabel.nextElementSibling;
                            let attempts = 0;
                            while (sibling && attempts < 10) {
                                console.log('检查兄弟元素:', sibling.tagName, sibling.className);
                                // 查找clickable的元素
                                if (sibling.click) {
                                    sibling.click();
                                    console.log('点击了兄弟元素');
                                    return {success: true, method: 'sibling'};
                                }
                                // 查找子元素中的clickable元素
                                const clickable = sibling.querySelector('[class*="ant-select"], .ant-select-selection, input');
                                if (clickable && clickable.click) {
                                    clickable.click();
                                    console.log('点击了子元素');
                                    return {success: true, method: 'child'};
                                }
                                sibling = sibling.nextElementSibling;
                                attempts++;
                            }
                        }
                        
                        // 方法2: 直接查找ant-select组件
                        const allSelects = document.querySelectorAll('.ant-select');
                        console.log('找到', allSelects.length, '个ant-select');
                        
                        // 遍历查找CPU对应的下拉框
                        for (let i, select of allSelects) {
                            const html = select.outerHTML;
                            console.log(`Select ${i}:`, html.substring(0, 200));
                        }
                        
                        // 方法3: 查找CPU字段对应的下拉框
                        // 通常在型号下拉框之后
                        return {success: false, reason: '未找到CPU下拉框'};
                    }''')
                    
                    print(f"点击结果: {click_result}")
                        
        await browser.close()

asyncio.run(click_cpu())
