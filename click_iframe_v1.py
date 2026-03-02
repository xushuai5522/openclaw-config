#!/usr/bin/env python3
"""
使用Playwright连接到现有Chrome并点击iframe内的元素
"""
import asyncio
import json
import os
import sys

# 连接到已有的Chrome
async def click_iframe_element():
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # 连接到已运行的Chrome
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
            
            # 获取所有上下文和页面
            contexts = browser.contexts
            print(f"找到 {len(contexts)} 个浏览器上下文")
            
            for ctx in contexts:
                pages = ctx.pages
                print(f"上下文中有 {len(pages)} 个页面")
                
                for page in pages:
                    url = page.url
                    print(f"页面URL: {url}")
                    
                    if "id=801233" in url:
                        print("找到目标商品页面!")
                        
                        # 查找iframe
                        frames = page.frames
                        print(f"页面有 {len(frames)} 个frame")
                        
                        # 尝试在主frame中查找元素
                        # 先尝试点击CPU下拉框
                        try:
                            # 等待页面加载完成
                            await page.wait_for_load_state("networkidle")
                            
                            # 使用JavaScript点击CPU下拉框
                            # 先获取iframe
                            iframe_element = await page.query_selector('iframe')
                            if iframe_element:
                                print("找到iframe元素")
                                frame = await iframe_element.content_frame()
                                if frame:
                                    print("获取到iframe的content_frame")
                                    
                                    # 尝试点击CPU下拉框
                                    cpu_dropdown = await frame.query_selector('div[data-fieldid="cpu"]')
                                    if cpu_dropdown:
                                        print("找到CPU下拉框元素")
                                        await cpu_dropdown.click()
                                        print("点击了CPU下拉框")
                                    else:
                                        print("未找到CPU下拉框，尝试其他方式")
                                        # 尝试通过其他选择器
                                        all_divs = await frame.query_selector_all('div')
                                        print(f"iframe内找到 {len(all_divs)} 个div")
                            else:
                                print("未找到iframe，尝试直接在主页面查找")
                                
                                # 尝试直接在page中查找
                                cpu = await page.query_selector('[data-fieldid="cpu"], [placeholder="请选择CPU"]')
                                if cpu:
                                    print("直接找到CPU元素")
                                    await cpu.click()
                                    
                        except Exception as e:
                            print(f"点击CPU出错: {e}")
                            import traceback
                            traceback.print_exc()
                        
                        return True
            
            await browser.close()
            return False
            
    except Exception as e:
        print(f"连接Chrome失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(click_iframe_element())
    print(f"执行结果: {result}")
