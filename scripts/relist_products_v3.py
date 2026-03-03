#!/usr/bin/env python3
"""
方案4：使用已登录的浏览器，但创建新页面避免干扰
"""
import time
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"

def main():
    print("🚀 连接浏览器...")
    
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.connect_over_cdp(CDP_URL)
            ctx = browser.contexts[0]
            
            # 创建新页面（避免复用导致的问题）
            page = ctx.new_page()
            
            print("📝 打开人人租后台...")
            try:
                page.goto('https://admin.rrzu.com/spu-view/list', 
                         wait_until='load', timeout=30000)
            except Exception as e:
                print(f"⚠️ 页面加载超时，继续尝试: {e}")
            
            time.sleep(5)
            
            # 检查是否需要登录
            if 'login' in page.url.lower():
                print("❌ 需要登录，请先在浏览器中登录人人租后台")
                page.close()
                return
            
            print("✅ 已登录")
            
            # 关闭弹窗（忽略错误）
            try:
                page.evaluate('''() => {
                    setTimeout(() => {
                        const buttons = document.querySelectorAll('button');
                        for (const btn of buttons) {
                            const text = btn.textContent || '';
                            if (text.includes('取消') || text.includes('关闭') || text.includes('跳过')) {
                                try { btn.click(); } catch(e) {}
                            }
                        }
                    }, 1000);
                }''')
                time.sleep(3)
            except:
                pass
            
            # 获取iframe
            print("🔍 查找iframe...")
            frame = None
            max_retries = 5
            for i in range(max_retries):
                for f in page.frames:
                    if 'admin-vue.rrzu.com' in f.url or f.name == 'rrzuji':
                        frame = f
                        break
                if frame:
                    break
                print(f"  重试 {i+1}/{max_retries}...")
                time.sleep(2)
            
            if not frame:
                print("❌ 未找到iframe")
                page.close()
                return
            
            print("✅ 找到iframe")
            
            # 点击"已下架"标签
            print("📑 切换到已下架标签...")
            try:
                # 等待页面加载
                time.sleep(3)
                
                clicked = frame.evaluate('''() => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    for (const el of elements) {
                        const text = (el.textContent || '').trim();
                        // 精确匹配"已下架"
                        if (text === '已下架' && 
                            (el.tagName === 'SPAN' || el.tagName === 'DIV' || el.classList.contains('el-tabs__item'))) {
                            try {
                                el.click();
                                return true;
                            } catch(e) {
                                console.error(e);
                            }
                        }
                    }
                    return false;
                }''')
                
                if clicked:
                    print("✅ 切换成功")
                    time.sleep(4)
                else:
                    print("⚠️ 未找到已下架标签，可能已经在该标签页")
            except Exception as e:
                print(f"⚠️ 切换标签失败: {e}")
            
            # 提取已下架商品
            print("📦 提取已下架商品...")
            products = frame.evaluate('''() => {
                const rows = Array.from(document.querySelectorAll('tr'));
                const products = [];
                
                for (const row of rows) {
                    const text = row.innerText || '';
                    const idMatch = text.match(/ID:(\\d+)/);
                    
                    if (idMatch) {
                        // 检查是否包含"已下架"状态
                        if (text.includes('已下架')) {
                            const product = {
                                id: idMatch[1],
                                name: ''
                            };
                            
                            const nameEl = row.querySelector('a');
                            if (nameEl) product.name = nameEl.innerText.trim();
                            
                            products.push(product);
                        }
                    }
                }
                
                return products;
            }''')
            
            print(f"\n找到 {len(products)} 个已下架商品:")
            for p in products:
                print(f"  - {p['name']} (ID:{p['id']})")
            
            if not products:
                print("\n✅ 没有已下架的商品")
                page.close()
                return
            
            # 逐个重新上架
            print(f"\n🚀 开始重新上架...")
            
            success_count = 0
            fail_count = 0
            
            for idx, product in enumerate(products, 1):
                print(f"\n[{idx}/{len(products)}] {product['name']} (ID:{product['id']})")
                
                try:
                    # 查找并点击上架按钮
                    clicked = frame.evaluate(f'''() => {{
                        const rows = Array.from(document.querySelectorAll('tr'));
                        for (const row of rows) {{
                            const text = row.innerText || '';
                            if (text.includes('ID:{product['id']}')) {{
                                const buttons = row.querySelectorAll('button');
                                for (const btn of buttons) {{
                                    const btnText = (btn.textContent || '').trim();
                                    // 精确匹配"上架"，排除"下架"
                                    if (btnText === '上架' || btnText.includes('重新上架')) {{
                                        try {{
                                            btn.click();
                                            return true;
                                        }} catch(e) {{
                                            console.error(e);
                                        }}
                                    }}
                                }}
                            }}
                        }}
                        return false;
                    }}''')
                    
                    if clicked:
                        print("  ✅ 点击上架按钮")
                        time.sleep(2)
                        
                        # 确认上架
                        confirmed = frame.evaluate('''() => {
                            const buttons = document.querySelectorAll('button');
                            for (const btn of buttons) {
                                const text = (btn.textContent || '').trim();
                                if (text === '确定' || text === '确认') {
                                    try {
                                        btn.click();
                                        return true;
                                    } catch(e) {}
                                }
                            }
                            return false;
                        }''')
                        
                        if confirmed:
                            print("  ✅ 已确认上架")
                            success_count += 1
                        else:
                            print("  ⚠️ 未找到确认按钮（可能已自动确认）")
                            success_count += 1
                        
                        time.sleep(2)
                    else:
                        print("  ❌ 未找到上架按钮")
                        fail_count += 1
                        
                except Exception as e:
                    print(f"  ❌ 处理失败: {e}")
                    fail_count += 1
            
            # 汇总
            print(f"\n{'='*60}")
            print(f"📊 处理完成:")
            print(f"  ✅ 成功: {success_count}")
            print(f"  ❌ 失败: {fail_count}")
            print(f"  📦 总计: {len(products)}")
            
            # 关闭页面
            time.sleep(2)
            page.close()
            print("\n✅ 任务完成")
            
        except Exception as e:
            print(f"\n❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
