#!/usr/bin/env python3
"""
Playwright v8 - More robust approach with keyboard and mouse
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
            if target_page:
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
        
        print(f"Frame: {frame.url}")
        
        # Wait for frame to load
        await frame.wait_for_load_state('domcontentloaded')
        await asyncio.sleep(3)
        
        # Try using keyboard to navigate and select
        # Step 1: Tab to CPU field and press Enter/Down to open
        try:
            # Use evaluate to find the CPU dropdown and trigger it
            result = await frame.evaluate('''
                () => {
                    // Find the CPU row and click on its ant-select
                    const rows = document.querySelectorAll('.ant-form-item');
                    for (let row of rows) {
                        const label = row.querySelector('.ant-form-item-label > label');
                        if (label && label.textContent === 'CPU') {
                            const selectWrapper = row.querySelector('.ant-select');
                            if (selectWrapper) {
                                // Try different ways to trigger
                                selectWrapper.focus();
                                return 'cpu-focus-done';
                            }
                        }
                    }
                    return 'cpu-not-found';
                }
            ''')
            print(f"CPU focus: {result}")
            
            # Now try clicking using mouse events
            await frame.evaluate('''
                () => {
                    const rows = document.querySelectorAll('.ant-form-item');
                    for (let row of rows) {
                        const label = row.querySelector('.ant-form-item-label > label');
                        if (label && label.textContent === 'CPU') {
                            const selectWrapper = row.querySelector('.ant-select');
                            if (selectWrapper) {
                                // Create and dispatch events
                                const rect = selectWrapper.getBoundingClientRect();
                                const events = [
                                    new MouseEvent('mouseover', { bubbles: true, clientX: rect.x + 10, clientY: rect.y + 10 }),
                                    new MouseEvent('mousedown', { bubbles: true, clientX: rect.x + 10, clientY: rect.y + 10 }),
                                    new MouseEvent('mouseup', { bubbles: true, clientX: rect.x + 10, clientY: rect.y + 10 }),
                                    new MouseEvent('click', { bubbles: true, clientX: rect.x + 10, clientY: rect.y + 10 })
                                ];
                                events.forEach(e => selectWrapper.dispatchEvent(e));
                                return 'cpu-click-done';
                            }
                        }
                    }
                    return 'cpu-click-failed';
                }
            ''')
            print("CPU click dispatched")
            
            await asyncio.sleep(1)
            
            # Check for dropdown
            dropdown = await frame.evaluate('''
                () => {
                    const dropdown = document.querySelector('.ant-select-dropdown');
                    if (!dropdown) return 'no-dropdown';
                    const items = dropdown.querySelectorAll('.ant-select-item');
                    if (items.length === 0) return 'empty-dropdown';
                    return 'dropdown-open-' + items.length + '-items';
                }
            ''')
            print(f"Dropdown status: {dropdown}")
            
        except Exception as e:
            print(f"CPU error: {e}")
        
        print("Done!")

if __name__ == '__main__':
    asyncio.run(main())
