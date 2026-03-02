#!/usr/bin/env python3
"""
Optimized Playwright v7 - Using native Playwright locators
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
        
        # Get the frame using Playwright's frame method
        frame = target_page.frame(url=lambda u: 'admin-vue.rrzu.com' in u)
        if not frame:
            print("Frame not found")
            await browser.close()
            return
        
        print(f"Using frame: {frame.url}")
        
        # Wait for content
        await frame.wait_for_load_state('domcontentloaded')
        await asyncio.sleep(2)
        
        # Use native Playwright locator - more reliable
        try:
            # Find CPU select by placeholder
            cpu_select = frame.locator('.ant-select').filter(has=frame.locator('.ant-select-selection-placeholder', has_text='请选择')).first
            await cpu_select.click()
            print("Clicked CPU select")
            
            # Wait for dropdown
            await frame.wait_for_selector('.ant-select-dropdown', timeout=3000)
            print("Dropdown appeared")
            
            # Click option containing 骁龙
            option = frame.locator('.ant-select-dropdown .ant-select-item').filter(has_text='骁龙').first
            await option.click()
            print("Selected CPU option")
            
        except Exception as e:
            print(f"CPU error: {e}")
        
        await asyncio.sleep(0.5)
        
        # Storage
        try:
            # Try clicking by finding the element after CPU label
            storage = frame.locator('.ant-select').nth(1)  # Second ant-select
            await storage.click()
            print("Clicked Storage")
            
            await frame.wait_for_selector('.ant-select-dropdown', timeout=3000)
            
            option = frame.locator('.ant-select-dropdown .ant-select-item').filter(has_text='256GB').first
            await option.click()
            print("Selected Storage")
            
        except Exception as e:
            print(f"Storage error: {e}")
        
        await asyncio.sleep(0.5)
        
        # RAM
        try:
            ram = frame.locator('.ant-select').nth(2)  # Third ant-select
            await ram.click()
            print("Clicked RAM")
            
            await frame.wait_for_selector('.ant-select-dropdown', timeout=3000)
            
            option = frame.locator('.ant-select-dropdown .ant-select-item').filter(has_text='8GB').first
            await option.click()
            print("Selected RAM")
            
        except Exception as e:
            print(f"RAM error: {e}")
        
        print("Done!")

if __name__ == '__main__':
    asyncio.run(main())
