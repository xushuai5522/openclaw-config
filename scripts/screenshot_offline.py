#!/usr/bin/env python3
"""
截图查看已下架商品的实际按钮
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
            
      # 截图
            page.screenshot(path='/Users/xs/.openclaw/workspace/temp/offline_products.png', full_page=True)
            print("✅ 截图已保存: temp/offline_products.png")
            
            # 提取第一个商品的所有按钮文字
            buttons = frame.evaluate('''() => {
                const rows = Array.from(document.querySelectorAll('tr'));
                for (const row of rows) {
                    if (row.innerText.includes('ID:195292')) {
                        const btns = row.querySelectorAll('button, a');
                        return Array.from(btns).map(b => b.textContent.trim());
                    }
                }
                return [];
            }''')
            
            print(f"\n第一个商品的按钮: {buttons}")
        
        page.close()

if __name__ == '__main__':
    main()
