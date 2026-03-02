#!/usr/bin/env python3
"""
Optimized Playwright - Connect to existing browser only
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Connect to existing browser via CDP only
        try:
            browser = await p.chromium.connect_over_cdp('http://127.0.0.1:18800')
            print("Connected to browser")
        except Exception as e:
            print(f"Connect failed: {e}")
            return
        
        # Find the target page
        target_page = None
        target_context = None
        
        for ctx in browser.contexts:
            for page in ctx.pages:
                print(f"Page: {page.url}")
                if 'admin.rrzu.com/spu-view/create?id=801233' in page.url:
                    target_page = page
                    target_context = ctx
                    break
            if target_page:
                break
        
        if not target_page:
            print("Target page not found, trying first page...")
            if browser.contexts and browser.contexts[0].pages:
                target_page = browser.contexts[0].pages[0]
                target_context = browser.contexts[0]
            else:
                print("No pages found")
                await browser.close()
                return
        
        print(f"Using page: {target_page.url}")
        
        # Wait for iframe
        try:
            await target_page.wait_for_selector('iframe', timeout=10000)
            print("Iframe found")
        except Exception as e:
            print(f"Iframe wait error: {e}")
            await browser.close()
            return
        
        # Get the iframe - usually the second frame
        frame = None
        for f in target_page.frames:
            if f != target_page.main_frame and 'admin.rrzu.com' in f.url:
                frame = f
                break
        
        if not frame:
            print("Frame not found, trying frame[1]")
            if len(target_page.frames) > 1:
                frame = target_page.frames[1]
            else:
                print("No iframe frame found")
                await browser.close()
                return
        
        print(f"Using frame URL: {frame.url}")
        
        # Fill CPU
        try:
            await frame.wait_for_selector('.ant-select[placeholder="CPU"]', timeout=5000)
            cpu_select = frame.locator('.ant-select[placeholder="CPU"]').first
            await cpu_select.click()
            await frame.wait_for_timeout(300)
            
            # Click option
            options = await frame.query_selector_all('.ant-select-dropdown .ant-select-item-option-content')
            for opt in options:
                text = await opt.text_content()
                if '骁龙8' in text:
                    await opt.click()
                    print(f"CPU selected: {text}")
                    break
        except Exception as e:
            print(f"CPU error: {e}")
        
        await frame.wait_for_timeout(300)
        
        # Fill Storage
        try:
            storage_select = frame.locator('.ant-select[placeholder="机身储存"]').first
            await storage_select.click()
            await frame.wait_for_timeout(300)
            
            options = await frame.query_selector_all('.ant-select-dropdown .ant-select-item-option-content')
            for opt in options:
                text = await opt.text_content()
                if '256GB' in text:
                    await opt.click()
                    print(f"Storage selected: {text}")
                    break
        except Exception as e:
            print(f"Storage error: {e}")
        
        await frame.wait_for_timeout(300)
        
        # Fill RAM
        try:
            ram_select = frame.locator('.ant-select[placeholder="运行内存"]').first
            await ram_select.click()
            await frame.wait_for_timeout(300)
            
            options = await frame.query_selector_all('.ant-select-dropdown .ant-select-item-option-content')
            for opt in options:
                text = await opt.text_content()
                if '8GB' in text:
                    await opt.click()
                    print(f"RAM selected: {text}")
                    break
        except Exception as e:
            print(f"RAM error: {e}")
        
        print("All fields filled!")
        
        # Don't close browser - keep session alive
        # await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
