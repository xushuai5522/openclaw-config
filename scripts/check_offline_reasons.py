#!/usr/bin/env python3
"""
查看已下架商品的下架原因
"""
import time
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"

PRODUCTS = [
    {"id": "195292", "name": "Apple TV 7代 4K播放器"},
    {"id": "195016", "name": "wacom手绘板pth660"},
    {"id": "104113", "name": "PSV 2000黑商店"},
    {"id": "110557", "name": "索尼EF 24-240mm"},
    {"id": "110560", "name": "适马30-1.4mm"}
]

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
        
        if not frame:
            print("❌ 未找到iframe")
            page.close()
            return
        
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
        
        print("📋 查看下架原因...\n")
        
        for product in PRODUCTS:
            print(f"{'='*60}")
            print(f"{product['name']} (ID:{product['id']})")
            print(f"{'='*60}")
            
            # 点击"下架原因"
            clicked = frame.evaluate(f'''() => {{
                const rows = Array.from(document.querySelectorAll('tr'));
                for (const row of rows) {{
                    if (row.innerText.includes('ID:{product['id']}')) {{
                        const buttons = row.querySelectorAll('button');
                        for (const btn of buttons) {{
                            if (btn.textContent.includes('下架原因')) {{
                                try {{
                                    btn.click();
                                    return true;
                                }} catch(e) {{}}
                            }}
                        }}
                    }}
                }}
                return false;
            }}''')
            
            if clicked:
                time.sleep(2)
                
                # 提取弹窗内容
                reason = frame.evaluate('''() => {
                    const dialog = document.querySelector('.el-dialog__body, .el-message-box__message');
                    return dialog ? dialog.innerText : '未找到原因';
                }''')
                
                print(f"原因: {reason}\n")
                
                # 关闭弹窗
                frame.evaluate('''() => {
                    const closeBtn = document.querySelector('.el-dialog__close, .el-message-box__close');
                    if (closeBtn) closeBtn.click();
                }''')
                time.sleep(1)
            else:
                print("⚠️ 未找到下架原因按钮\n")
        
        page.close()

if __name__ == '__main__':
    main()
