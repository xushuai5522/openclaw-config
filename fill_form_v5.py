#!/usr/bin/env python3
"""
Optimized Playwright v5 - Use correct iframe frame
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp('http://127.0.0.1:18800')
            print("Connected to browser")
        except Exception as e:
            print(f"Connect failed: {e}")
            return
        
        # Find target page
        target_page = None
        for ctx in browser.contexts:
            for page in ctx.pages:
                if 'admin.rrzu.com/spu-view/create' in page.url and 'id=801233' in page.url:
                    target_page = page
                    break
            if target_page:
                break
        
        if not target_page:
            print("Target page not found")
            await browser.close()
            return
        
        print(f"Page: {target_page.url}")
        
        # Wait for iframe to fully load
        await target_page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        # Use frame by URL
        frame = target_page.frame(url=lambda u: 'admin-vue.rrzu.com' in u)
        
        if not frame:
            print("Frame not found by URL, trying frame[2]")
            if len(target_page.frames) > 2:
                frame = target_page.frames[2]
            else:
                print("No frame found")
                await browser.close()
                return
        
        print(f"Using frame: {frame.url}")
        
        # Wait for content in frame
        await frame.wait_for_load_state('domcontentloaded')
        await asyncio.sleep(2)
        
        # Fill CPU
        try:
            result = await frame.evaluate('''
                () => {
                    const selects = document.querySelectorAll('.ant-select[placeholder="CPU"]');
                    if (selects.length > 0) {
                        selects[0].click();
                        return 'cpu-clicked';
                    }
                    // Try finding by parent
                    const labels = document.querySelectorAll('.ant-form-item-label > label');
                    for (let label of labels) {
                        if (label.textContent === 'CPU') {
                            const parent = label.parentElement.parentElement;
                            const select = parent.querySelector('.ant-select');
                            if (select) {
                                select.click();
                                return 'cpu-clicked-v2';
                            }
                        }
                    }
                    return 'cpu-not-found';
                }
            ''')
            print(f"CPU click: {result}")
            
            if 'clicked' in result:
                await asyncio.sleep(0.5)
                # Select option
                select_result = await frame.evaluate('''
                    () => {
                        const dropdown = document.querySelector('.ant-select-dropdown');
                        if (dropdown) {
                            const options = dropdown.querySelectorAll('.ant-select-item-option-content, .ant-select-item');
                            for (let opt of options) {
                                const text = opt.textContent || opt.innerText;
                                if (text.includes('骁龙8')) {
                                    opt.click();
                                    return 'selected: ' + text;
                                }
                            }
                        }
                        return 'no-option-found';
                    }
                ''')
                print(f"CPU select: {select_result}")
                
        except Exception as e:
            print(f"CPU error: {e}")
        
        await asyncio.sleep(0.5)
        
        # Fill Storage
        try:
            result = await frame.evaluate('''
                () => {
                    const selects = document.querySelectorAll('.ant-select[placeholder="机身储存"]');
                    if (selects.length > 0) {
                        selects[0].click();
                        return 'storage-clicked';
                    }
                    return 'storage-not-found';
                }
            ''')
            print(f"Storage click: {result}")
            
            if 'clicked' in result:
                await asyncio.sleep(0.5)
                select_result = await frame.evaluate('''
                    () => {
                        const dropdown = document.querySelector('.ant-select-dropdown');
                        if (dropdown) {
                            const options = dropdown.querySelectorAll('.ant-select-item-option-content, .ant-select-item');
                            for (let opt of options) {
                                const text = opt.textContent || opt.innerText;
                                if (text.includes('256GB')) {
                                    opt.click();
                                    return 'selected: ' + text;
                                }
                            }
                        }
                        return 'no-option-found';
                    }
                ''')
                print(f"Storage select: {select_result}")
                
        except Exception as e:
            print(f"Storage error: {e}")
        
        await asyncio.sleep(0.5)
        
        # Fill RAM
        try:
            result = await frame.evaluate('''
                () => {
                    const selects = document.querySelectorAll('.ant-select[placeholder="运行内存"]');
                    if (selects.length > 0) {
                        selects[0].click();
                        return 'ram-clicked';
                    }
                    return 'ram-not-found';
                }
            ''')
            print(f"RAM click: {result}")
            
            if 'clicked' in result:
                await asyncio.sleep(0.5)
                select_result = await frame.evaluate('''
                    () => {
                        const dropdown = document.querySelector('.ant-select-dropdown');
                        if (dropdown) {
                            const options = dropdown.querySelectorAll('.ant-select-item-option-content, .ant-select-item');
                            for (let opt of options) {
                                const text = opt.textContent || opt.innerText;
                                if (text.includes('8GB')) {
                                    opt.click();
                                    return 'selected: ' + text;
                                }
                            }
                        }
                        return 'no-option-found';
                    }
                ''')
                print(f"RAM select: {select_result}")
                
        except Exception as e:
            print(f"RAM error: {e}")
        
        print("Done!")

if __name__ == '__main__':
    asyncio.run(main())
