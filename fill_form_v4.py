#!/usr/bin/env python3
"""
Optimized Playwright v4 - Wait for iframe content to load
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
        await asyncio.sleep(3)
        
        # Check all frames
        print("Checking frames...")
        for i, f in enumerate(target_page.frames):
            print(f"Frame {i}: {f.url}")
        
        # The form is in the main frame (same-origin)
        # Try accessing elements directly on the page
        try:
            # Check if elements exist
            elements = await target_page.evaluate('''
                () => {
                    const selects = document.querySelectorAll('.ant-select');
                    const result = [];
                    for (let s of selects) {
                        const placeholder = s.getAttribute('placeholder') || s.querySelector('.ant-select-selection-placeholder')?.textContent;
                        if (placeholder) {
                            result.push(placeholder);
                        }
                    }
                    return result;
                }
            ''')
            print(f"Found selects: {elements}")
        except Exception as e:
            print(f"Check error: {e}")
        
        # Try clicking using page.evaluate on main frame
        try:
            result = await target_page.evaluate('''
                () => {
                    // Find CPU select
                    const allElements = document.querySelectorAll('*');
                    let cpuElement = null;
                    for (let el of allElements) {
                        if (el.classList && el.classList.contains('ant-select') && el.getAttribute('placeholder') === 'CPU') {
                            cpuElement = el;
                            break;
                        }
                        // Also check for ant-select with CPU in ancestor text
                        const parent = el.parentElement;
                        if (parent && parent.classList && parent.classList.contains('ant-select')) {
                            const prev = parent.previousElementSibling;
                            if (prev && prev.textContent === 'CPU') {
                                cpuElement = parent;
                                break;
                            }
                        }
                    }
                    if (cpuElement) {
                        cpuElement.click();
                        return 'cpu-clicked';
                    }
                    return 'cpu-not-found';
                }
            ''')
            print(f"CPU click: {result}")
        except Exception as e:
            print(f"CPU click error: {e}")
        
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
