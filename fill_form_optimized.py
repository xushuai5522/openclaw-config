#!/usr/bin/env python3
"""
Optimized Playwright script to fill the form in iframe
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch browser with minimal memory
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-background-networking',
                '--disable-default-apps',
                '--disable-sync',
                '--disable-translate',
                '--metrics-recording-only',
                '--mute-audio',
                '--no-first-run',
                '--safebrowsing-disable-auto-update',
            ]
        )
        
        # Connect to existing browser via CDP
        try:
            browser = await p.chromium.connect_over_cdp('http://127.0.0.1:18800')
        except Exception as e:
            print(f"Connect failed: {e}")
            await browser.close()
            return
        
        # Close all contexts except the one we need
        for ctx in browser.contexts:
            for page in ctx.pages:
                if 'admin.rrzu.com/spu-view/create?id=801233' not in page.url:
                    await page.close()
        
        # Get the target page
        context = browser.contexts[0]
        page = None
        for p in context.pages:
            if 'admin.rrzu.com/spu-view/create' in p.url:
                page = p
                break
        
        if not page:
            print("Target page not found")
            await browser.close()
            return
        
        # Wait for iframe and switch to it
        await page.wait_for_selector('iframe', timeout=10000)
        frame = page.frames[1]  # Usually the second frame is the content frame
        
        print(f"Frame URL: {frame.url}")
        
        # Fill CPU field
        try:
            cpu_select = frame.locator('.ant-select[placeholder="CPU"]').first
            await cpu_select.click()
            await frame.wait_for_timeout(500)
            
            # Select 骁龙8 Gen 2
            option = frame.locator('.ant-select-dropdown .ant-select-item-option-content:has-text("骁龙8")').first
            await option.click()
            print("CPU selected: 骁龙8 Gen 2")
        except Exception as e:
            print(f"CPU error: {e}")
        
        await frame.wait_for_timeout(500)
        
        # Fill Storage field
        try:
            storage_select = frame.locator('.ant-select[placeholder="机身储存"]').first
            await storage_select.click()
            await frame.wait_for_timeout(500)
            
            option = frame.locator('.ant-select-dropdown .ant-select-item-option-content:has-text("256GB")').first
            await option.click()
            print("Storage selected: 256GB")
        except Exception as e:
            print(f"Storage error: {e}")
        
        await frame.wait_for_timeout(500)
        
        # Fill RAM field
        try:
            ram_select = frame.locator('.ant-select[placeholder="运行内存"]').first
            await ram_select.click()
            await frame.wait_for_timeout(500)
            
            option = frame.locator('.ant-select-dropdown .ant-select-item-option-content:has-text("8GB")').first
            await option.click()
            print("RAM selected: 8GB")
        except Exception as e:
            print(f"RAM error: {e}")
        
        print("Done!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
