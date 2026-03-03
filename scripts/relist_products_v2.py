#!/usr/bin/env python3
"""
方案3：启动独立的Chrome实例，避免CDP连接问题
"""
import time
import json
from playwright.sync_api import sync_playwright

def main():
    print("🚀 启动独立浏览器实例...")
    
    with sync_playwright() as pw:
        # 使用持久化上下文，保留登录状态
        user_data_dir = "/Users/xs/.openclaw/chrome_profile"
        
        browser = pw.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=['--start-maximized'],
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        print("📝 打开人人租后台...")
        page.goto('https://admin.rrzu.com/spu-view/list', timeout=60000)
        time.sleep(5)
        
        # 检查是否需要登录
        if 'login' in page.url.lower():
            print("⚠️ 需要登录，请手动登录后按回车继续...")
            input()
            page.goto('https://admin.rrzu.com/spu-view/list', timeout=60000)
            time.sleep(5)
        
        # 关闭弹窗
        try:
            page.evaluate('''() => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = btn.textContent || '';
                    if (text.includes('取消') || text.includes('关闭') || text.includes('跳过')) {
                        btn.click();
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
            browser.close()
            return
        
        print("✅ 找到iframe")
        
        # 点击"已下架"标签
        try:
            clicked = frame.evaluate('''() => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    const text = el.textContent || '';
                    if (text.trim() === '已下架' && el.tagName !== 'BODY') {
                        el.click();
                        return true;
                    }
                }
                return false;
            }''')
            
            if clicked:
                print("✅ 切换到已下架标签")
                time.sleep(3)
            else:
                print("⚠️ 未找到已下架标签")
        except Exception as e:
            print(f"⚠️ 切换标签失败: {e}")
        
        # 提取已下架商品
        products = frame.evaluate('''() => {
            const rows = Array.from(document.querySelectorAll('tr'));
            const products = [];
            
            for (const row of rows) {
                const text = row.innerText || '';
                const idMatch = text.match(/ID:(\\d+)/);
                
                if (idMatch && text.includes('已下架')) {
                    const product = {
                        id: idMatch[1],
                        name: ''
                    };
                    
                    const nameEl = row.querySelector('a');
                    if (nameEl) product.name = nameEl.innerText.trim();
                    
                    products.push(product);
                }
            }
            
            return products;
        }''')
        
        print(f"\n📦 找到 {len(products)} 个已下架商品:")
        for p in products:
            print(f"  - {p['name']} (ID:{p['id']})")
        
        if not products:
            print("\n✅ 没有已下架的商品")
            browser.close()
            return
        
        # 逐个重新上架
        print(f"\n🚀 开始重新上架...")
        
        success_count = 0
        fail_count = 0
        
        for product in products:
            print(f"\n{'='*60}")
            print(f"📝 处理: {product['name']} (ID:{product['id']})")
            
            try:
                # 查找并点击上架按钮
                clicked = frame.evaluate(f'''() => {{
                    const rows = Array.from(document.querySelectorAll('tr'));
                    for (const row of rows) {{
                        const text = row.innerText || '';
                        if (text.includes('ID:{product['id']}')) {{
                            const buttons = row.querySelectorAll('button, a');
                            for (const btn of buttons) {{
                                const btnText = btn.textContent || '';
                                if (btnText.includes('上架') && !btnText.includes('下架')) {{
                                    btn.click();
                                    return true;
                                }}
                            }}
                        }}
                    }}
                    return false;
                }}''')
                
                if clicked:
                    print("✅ 点击了上架按钮")
                    time.sleep(2)
                    
                    # 确认上架
                    try:
                        confirmed = frame.evaluate('''() => {
                            const buttons = document.querySelectorAll('button');
                            for (const btn of buttons) {
                                const text = btn.textContent || '';
                                if (text.includes('确定') || text.includes('确认')) {
                                    btn.click();
                                    return true;
                                }
                            }
                            return false;
                        }''')
                        
                        if confirmed:
                            print("✅ 已确认上架")
                            success_count += 1
                        else:
                            print("⚠️ 未找到确认按钮")
                            fail_count += 1
                        
                        time.sleep(2)
                    except Exception as e:
                        print(f"⚠️ 确认失败: {e}")
                        fail_count += 1
                else:
                    print("⚠️ 未找到上架按钮")
                    fail_count += 1
                    
            except Exception as e:
                print(f"❌ 处理失败: {e}")
                fail_count += 1
        
        # 汇总
        print(f"\n{'='*60}")
        print(f"📊 处理完成:")
        print(f"  - 成功: {success_count}")
        print(f"  - 失败: {fail_count}")
        print(f"  - 总计: {len(products)}")
        
        print("\n按回车关闭浏览器...")
        input()
        browser.close()

if __name__ == '__main__':
    main()
