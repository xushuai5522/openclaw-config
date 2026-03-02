#!/usr/bin/env python3
"""
Optimized Playwright v6 - Better dropdown handling
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
        
        # Get the frame
        frame = target_page.frame(url=lambda u: 'admin-vue.rrzu.com' in u)
        if not frame:
            print("Frame not found")
            await browser.close()
            return
        
        print(f"Using frame: {frame.url}")
        
        # Wait for frame to load
        await frame.wait_for_load_state('domcontentloaded')
        await asyncio.sleep(2)
        
        # Fill CPU
        try:
            # Click CPU field
            await frame.evaluate('''
                () => {
                    const labels = document.querySelectorAll('.ant-form-item-label > label');
                    for (let label of labels) {
                        if (label.textContent === 'CPU') {
                            const parent = label.parentElement.parentElement;
                            const select = parent.querySelector('.ant-select');
                            if (select) {
                                select.click();
                            }
                        }
                    }
                }
            ''')
            print("Clicked CPU dropdown")
            
            await asyncio.sleep(1)
            
            # Now check what's in the dropdown
            dropdown_items = await frame.evaluate('''
                () => {
                    const dropdown = document.querySelector('.ant-select-dropdown');
                    if (!dropdown) return 'no-dropdown';
                    
                    const items = dropdown.querySelectorAll('.ant-select-item, .ant-select-item-option-content');
                    const texts = [];
                    for (let item of items) {
                        texts.push(item.textContent.trim());
                    }
                    return texts.join(', ');
                }
            ''')
            print(f"Dropdown items: {dropdown_items}")
            
            # Try to select the first option or find 骁龙
            select_result = await frame.evaluate('''
                () => {
                    const dropdown = document.querySelector('.ant-select-dropdown');
                    if (!dropdown) return 'no-dropdown';
                    
                    // Try finding by text content
                    const allElements = dropdown.querySelectorAll('*');
                    for (let el of allElements) {
                        const text = el.textContent || '';
                        if (text.includes('骁龙') || text.includes('8 Gen')) {
                            el.click();
                            return 'clicked: ' + text;
                        }
                    }
                    
                    // If not found, try clicking first selectable item
                    const firstItem = dropdown.querySelector('.ant-select-item-option, .ant-select-item');
                    if (firstItem) {
                        firstItem.click();
                        return 'clicked first item';
                    }
                    return 'no-item-found';
                }
            ''')
            print(f"CPU select: {select_result}")
            
        except Exception as e:
            print(f"CPU error: {e}")
        
        await asyncio.sleep(0.5)
        
        # Fill Storage - try clicking then selecting
        try:
            await frame.evaluate('''
                () => {
                    const labels = document.querySelectorAll('.ant-form-item-label > label');
                    for (let label of labels) {
                        if (label.textContent === '机身储存') {
                            const parent = label.parentElement.parentElement;
                            const select = parent.querySelector('.ant-select');
                            if (select) {
                                select.click();
                            }
                        }
                    }
                }
            ''')
            print("Clicked Storage dropdown")
            
            await asyncio.sleep(1)
            
            select_result = await frame.evaluate('''
                () => {
                    const dropdown = document.querySelector('.ant-select-dropdown');
                    if (!dropdown) return 'no-dropdown';
                    
                    const allElements = dropdown.querySelectorAll('*');
                    for (let el of allElements) {
                        const text = el.textContent || '';
                        if (text.includes('256GB') || text.includes('GB')) {
                            el.click();
                            return 'clicked: ' + text;
                        }
                    }
                    
                    const firstItem = dropdown.querySelector('.ant-select-item-option, .ant-select-item');
                    if (firstItem) {
                        firstItem.click();
                        return 'clicked first item';
                    }
                    return 'no-item-found';
                }
            ''')
            print(f"Storage select: {select_result}")
            
        except Exception as e:
            print(f"Storage error: {e}")
        
        await asyncio.sleep(0.5)
        
        # Fill RAM
        try:
            await frame.evaluate('''
                () => {
                    const labels = document.querySelectorAll('.ant-form-item-label > label');
                    for (let label of labels) {
                        if (label.textContent === '运行内存') {
                            const parent = label.parentElement.parentElement;
                            const select = parent.querySelector('.ant-select');
                            if (select) {
                                select.click();
                            }
                        }
                    }
                }
            ''')
            print("Clicked RAM dropdown")
            
            await asyncio.sleep(1)
            
            select_result = await frame.evaluate('''
                () => {
                    const dropdown = document.querySelector('.ant-select-dropdown');
                    if (!dropdown) return 'no-dropdown';
                    
                    const allElements = dropdown.querySelectorAll('*');
                    for (let el of allElements) {
                        const text = el.textContent || '';
                        if (text.includes('8GB')) {
                            el.click();
                            return 'clicked: ' + text;
                        }
                    }
                    
                    const firstItem = dropdown.querySelector('.ant-select-item-option, .ant-select-item');
                    if (firstItem) {
                        firstItem.click();
                        return 'clicked first item';
                    }
                    return 'no-item-found';
                }
            ''')
            print(f"RAM select: {select_result}")
            
        except Exception as e:
            print(f"RAM error: {e}")
        
        print("Done!")

if __name__ == '__main__':
    asyncio.run(main())
