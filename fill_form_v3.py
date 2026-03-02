#!/usr/bin/env python3
"""
Optimized Playwright v3 - Direct frame access
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
        
        # Get all frames
        frames = target_page.frames
        print(f"Total frames: {len(frames)}")
        
        # Find the content frame (not the main frame)
        frame = None
        for f in frames:
            if f != target_page.main_frame:
                frame = f
                print(f"Using frame: {f.url}")
                break
        
        if not frame:
            print("No iframe frame found")
            await browser.close()
            return
        
        # Wait a bit for frame to load
        await asyncio.sleep(2)
        
        # Try to find and click CPU dropdown
        try:
            # Use evaluate to find the element in the frame
            result = await frame.evaluate('''
                () => {
                    const selects = document.querySelectorAll('.ant-select');
                    let cpuSelect = null;
                    for (let s of selects) {
                        const placeholder = s.getAttribute('placeholder');
                        if (placeholder === 'CPU') {
                            cpuSelect = s;
                            break;
                        }
                    }
                    if (cpuSelect) {
                        cpuSelect.click();
                        return 'cpu-clicked';
                    }
                    return 'cpu-not-found';
                }
            ''')
            print(f"CPU click result: {result}")
            
            if result == 'cpu-clicked':
                await asyncio.sleep(0.5)
                
                # Try to select option
                select_result = await frame.evaluate('''
                    () => {
                        const dropdown = document.querySelector('.ant-select-dropdown:not(.ant-select-dropdown-hidden)');
                        if (dropdown) {
                            const options = dropdown.querySelectorAll('.ant-select-item-option-content');
                            for (let opt of options) {
                                if (opt.textContent.includes('骁龙8')) {
                                    opt.click();
                                    return 'selected: ' + opt.textContent;
                                }
                            }
                            return 'no-snapdragon-option';
                        }
                        return 'no-dropdown';
                    }
                ''')
                print(f"CPU select result: {select_result}")
                
        except Exception as e:
            print(f"CPU error: {e}")
        
        await asyncio.sleep(0.5)
        
        # Fill Storage
        try:
            result = await frame.evaluate('''
                () => {
                    const selects = document.querySelectorAll('.ant-select');
                    let storageSelect = null;
                    for (let s of selects) {
                        const placeholder = s.getAttribute('placeholder');
                        if (placeholder === '机身储存') {
                            storageSelect = s;
                            break;
                        }
                    }
                    if (storageSelect) {
                        storageSelect.click();
                        return 'storage-clicked';
                    }
                    return 'storage-not-found';
                }
            ''')
            print(f"Storage click result: {result}")
            
            if result == 'storage-clicked':
                await asyncio.sleep(0.5)
                select_result = await frame.evaluate('''
                    () => {
                        const dropdown = document.querySelector('.ant-select-dropdown:not(.ant-select-dropdown-hidden)');
                        if (dropdown) {
                            const options = dropdown.querySelectorAll('.ant-select-item-option-content');
                            for (let opt of options) {
                                if (opt.textContent.includes('256GB')) {
                                    opt.click();
                                    return 'selected: ' + opt.textContent;
                                }
                            }
                        }
                        return 'failed';
                    }
                ''')
                print(f"Storage select result: {select_result}")
                
        except Exception as e:
            print(f"Storage error: {e}")
        
        await asyncio.sleep(0.5)
        
        # Fill RAM
        try:
            result = await frame.evaluate('''
                () => {
                    const selects = document.querySelectorAll('.ant-select');
                    let ramSelect = null;
                    for (let s of selects) {
                        const placeholder = s.getAttribute('placeholder');
                        if (placeholder === '运行内存') {
                            ramSelect = s;
                            break;
                        }
                    }
                    if (ramSelect) {
                        ramSelect.click();
                        return 'ram-clicked';
                    }
                    return 'ram-not-found';
                }
            ''')
            print(f"RAM click result: {result}")
            
            if result == 'ram-clicked':
                await asyncio.sleep(0.5)
                select_result = await frame.evaluate('''
                    () => {
                        const dropdown = document.querySelector('.ant-select-dropdown:not(.ant-select-dropdown-hidden)');
                        if (dropdown) {
                            const options = dropdown.querySelectorAll('.ant-select-item-option-content');
                            for (let opt of options) {
                                if (opt.textContent.includes('8GB')) {
                                    opt.click();
                                    return 'selected: ' + opt.textContent;
                                }
                            }
                        }
                        return 'failed';
                    }
                ''')
                print(f"RAM select result: {select_result}")
                
        except Exception as e:
            print(f"RAM error: {e}")
        
        print("Done!")

if __name__ == '__main__':
    asyncio.run(main())
