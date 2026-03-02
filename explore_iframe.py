#!/usr/bin/env python3
"""
探索iframe结构
"""
import asyncio
from playwright.async_api import async_playwright

async def explore_iframe():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        
        for ctx in browser.contexts:
            for page in ctx.pages:
                if "id=801233" in page.url:
                    print(f"当前URL: {page.url}")
                    
                    # 获取所有iframe
                    iframes = await page.query_selector_all('iframe')
                    print(f"找到 {len(iframes)} 个iframe")
                    
                    for i, iframe in enumerate(iframes):
                        attrs = await iframe.evaluate('''(el) => {
                            return {
                                id: el.id,
                                name: el.name,
                                src: el.src,
                                class: el.className
                            };
                        }''')
                        print(f"Iframe {i}: {attrs}")
                    
                    # 尝试获取frame
                    try:
                        frame = page.frame(name='iframe') or page.frame(url=lambda u: 'iframe' in u)
                        if frame:
                            print(f"Frame URL: {frame.url}")
                            
                            # 获取frame内的HTML
                            html = await frame.content()
                            print(f"Frame HTML长度: {len(html)}")
                            print(f"Frame HTML前500字符: {html[:500]}")
                    except Exception as e:
                        print(f"获取frame失败: {e}")
                    
                    # 尝试直接在页面中搜索包含"CPU"文本的元素
                    cpu_elements = await page.query_selector_all('text=CPU')
                    print(f"找到 {len(cpu_elements)} 个包含'CPU'的元素")
                    
                    # 尝试查找类目属性区域
                    category_section = await page.query_selector_all('.category-attrs, [class*="category"], [class*="attr"]')
                    print(f"找到 {len(category_section)} 个类目属性元素")
                    
        await browser.close()

asyncio.run(explore_iframe())
