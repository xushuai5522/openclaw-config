#!/usr/bin/env python3
"""
Script to fill in the product form on rrzuji.com merchant backend
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch browser (use existing Chrome profile)
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.launch_persistent_context(
            user_data_dir='/Users/xs/.openclaw/browser/openclaw/user-data',
        )
        page = await context.new_page()
        
        # Navigate to the product edit page
        await page.goto('https://admin.rrzu.com/spu-view/create?id=801233')
        await page.wait_for_load_state('networkidle')
        
        # Wait for iframe to load
        await asyncio.sleep(3)
        
        # Try to find and interact with the form
        # The form is inside an iframe
        frames = page.frames
        print(f"Number of frames: {len(frames)}")
        
        for i, frame in enumerate(frames):
            print(f"Frame {i}: {frame.url}")
        
        # Try to find the main content frame
        main_frame = None
        for frame in frames:
            if 'admin-vue' in frame.url or frame.url == 'about:blank':
                continue
            if 'spu-view' in frame.url:
                main_frame = frame
                break
        
        if main_frame:
            print(f"Using frame: {main_frame.url}")
            
            # Fill in CPU - try to find the dropdown
            try:
                # Wait for the dropdown to be visible
                await main_frame.wait_for_selector('.ant-select-selection', timeout=10000)
                
                # Click on CPU dropdown
                cpu_dropdown = await main_frame.query_selector_all('input[placeholder="请选择"]')
                print(f"Found {len(cpu_dropdown)} dropdowns with 请选择")
                
                if cpu_dropdown:
                    # Click the first dropdown (CPU)
                    await cpu_dropdown[0].click()
                    await asyncio.sleep(1)
                    
                    # Select 骁龙8 Gen 2
                    options = await main_frame.query_selector_all('.ant-select-dropdown .ant-select-item')
                    for opt in options:
                        text = await opt.inner_text()
                        print(f"Option: {text}")
                        if '骁龙8 Gen 2' in text:
                            await opt.click()
                            break
            except Exception as e:
                print(f"Error: {e}")
        
        await asyncio.sleep(5)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
