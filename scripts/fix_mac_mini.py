#!/usr/bin/env python3
"""
修复审核不通过的商品 - Mac Mini M4
问题：年总租金高于购买价格 + 最高租期超过1年
"""
import time
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"
PRODUCT_ID = "804995"

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]
        
        # 打开编辑页面
        edit_url = f"https://admin.rrzu.com/spu-view/create?id={PRODUCT_ID}&server_id=11904&publish_chanel="
        
        page = None
        for p in ctx.pages:
            if 'admin.rrzu.com' in p.url:
                page = p
                break
        
        if not page:
            page = ctx.new_page()
        
        print(f"📝 打开编辑页面: {edit_url}")
        page.goto(edit_url, wait_until='networkidle', timeout=30000)
        time.sleep(3)
        
        # 关闭弹窗
        try:
            page.evaluate('''() => {
                document.querySelectorAll('button').forEach(b => {
                    const text = b.textContent || '';
                    if (text.includes('取消') || text.includes('关闭')) {
                        b.click();
                    }
                });
            }''')
            time.sleep(1)
        except:
            pass
        
        # 截图当前状态
        page.screenshot(path='/Users/xs/.openclaw/workspace/temp/mac_mini_before.png', full_page=True)
        print("📸 截图已保存: temp/mac_mini_before.png")
        
        # 获取iframe
        frame = None
        for f in page.frames:
            if 'admin-vue.rrzu.com' in f.url or f.name == 'rrzuji':
                frame = f
                break
        
        if not frame:
            print("❌ 未找到iframe")
            return
        
        print("✅ 找到iframe，准备修改...")
        
        # 修改策略：
        # 1. 删除超过365天的租期套餐
        # 2. 调整价格确保年租金 < 购买价
        
        # 先提取当前套餐信息
        packages = frame.evaluate('''() => {
            const rows = document.querySelectorAll('tr');
            const pkgs = [];
            for (const row of rows) {
                const text = row.innerText || '';
                if (text.includes('天') && text.includes('元')) {
                    pkgs.push(text);
                }
            }
            return pkgs;
        }''')
        
        print(f"📦 当前套餐: {packages}")
        
        print("\n⚠️ 需要手动操作：")
        print("1. 删除超过365天的套餐（1095天那个）")
        print("2. 确保最长租期≤365天")
        print("3. 调整价格：月租×12 < 购买价3500元")
        print("   建议月租：≤290元/月")
        
        input("\n按回车继续...")

if __name__ == '__main__':
    main()
