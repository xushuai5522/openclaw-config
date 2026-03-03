#!/usr/bin/env python3
"""
调试：点击修改按钮后截图
"""
import time
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]
        page = ctx.new_page()
        
        page.goto('https://admin.rrzu.com/spu-view/list', wait_until='load', timeout=30000)
        time.sleep(5)
        
        # 关闭弹窗
        try:
            page.evaluate('''() => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = btn.textContent || '';
                    if (text.includes('取消') || text.includes('关闭') || text.includes('跳过')) {
                        try { btn.click(); } catch(e) {}
                    }
                }
            }''')
            time.sleep(2)
        except:
            pass
        
        # 获取iframe
        frame = None
        for f in page.frames:
            if 'admin-vue.rrzu.com' in f.url or f.name == 'rrzuji':
                frame = f
                break
        
        if frame:
            # 切换到已下架标签
            frame.evaluate('''() => {
                const elements = Array.from(document.querySelectorAll('*'));
                for (const el of elements) {
                    if ((el.textContent || '').trim() === '已下架') {
                        try { el.click(); } catch(e) {}
                    }
                }
            }''')
            time.sleep(4)
            
            print("📸 点击修改按钮前...")
            page.screenshot(path='/Users/xs/.openclaw/workspace/temp/before_click.png', full_page=True)
            
            # 点击第一个商品的修改按钮
            clicked = frame.evaluate('''() => {
                const rows = Array.from(document.querySelectorAll('tr'));
                for (const row of rows) {
                    if (row.innerText.includes('ID:195292')) {
                        const buttons = row.querySelectorAll('button');
                        for (const btn of buttons) {
                            if (btn.textContent.includes('修改商品')) {
                                try {
                                    btn.click();
                                    return true;
                                } catch(e) {}
                            }
                        }
                    }
                }
                return false;
            }''')
            
            if clicked:
                print("✅ 点击了修改按钮")
                time.sleep(5)
                
                print("📸 点击后...")
                page.screenshot(path='/Users/xs/.openclaw/workspace/temp/after_click.png', full_page=True)
                
                print(f"\n当前页面数量: {len(ctx.pages)}")
                print("页面URL:")
                for p in ctx.pages:
                    print(f"  - {p.url}")
        
        page.close()

if __name__ == '__main__':
    main()
