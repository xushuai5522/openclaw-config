#!/usr/bin/env python3
"""
Playwright v9 - Try native click and force
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp('http://127.0.0.1:18800')
            print("Connected")
        except Exception as e:
            print(f"Connect failed: {e}")
            return
        
        # Find target page
        target_page = None
        for ctx in browser.contexts:
            for page in ctx.pages:
                if 'id=801233' in page.url:
                    target_page = page
                    break
        
        if not target_page:
            print("Target page not found")
            await browser.close()
            return
        
        # Get the frame
        frame = target_page.frame(url=lambda u: 'admin-vue.rrzu.com' in u)
        if not frame:
            print("Frame not found")
            await browser.close()
            return
        
        # Wait and try native click with force
        await frame.wait_for_load_state('domcontentloaded')
        await asyncio.sleep(2)
        
        # Try using Playwright's native click with force
        try:
            # Try to find and click the CPU select
            cpu_select = frame.locator('.ant-select').first
            await cpu_select.click(force=True, timeout=5000)
            print("Native click done")
            
            await asyncio.sleep(1)
            
            # Check for dropdown
            dropdown_visible = await frame.locator('.ant-select-dropdown').is_visible(timeout=2000)
            print(f"Dropdown visible: {dropdown_visible}")
            
            if dropdown_visible:
                # Select option
                option = frame.locator('.ant-select-dropdown .ant-select-item').filter(has_text='骁龙').first
                await option.click()
                print("Option selected!")
        except Exception as e:
            print(f"Error: {e}")
            
            # Try alternative - use keyboard
            print("Trying keyboard approach...")
            await frame.keyboard.press('Tab')
            await frame.keyboard.press('Tab')
            await frame.keyboard.press('Tab')
            await frame.keyboard.press('Tab')
            await frame.keyboard.press('Tab')
            await frame.keyboard.press('ArrowDown')
            await asyncio.sleep(0.5)
            await frame.keyboard.press('Enter')
            print("Keyboard done")
        
        print("Done!")

if __name__ == '__main__':
    asyncio.run(main())
