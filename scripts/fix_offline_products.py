#!/usr/bin/env python3
"""
批量修改已下架商品 - 处理新标签页
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

def fix_product(ctx, list_page, list_frame, product):
    """修改单个商品"""
    print(f"\n{'='*60}")
    print(f"📝 修改: {product['name']} (ID:{product['id']})")
    print(f"{'='*60}")
    
    # 记录当前页面数量
    initial_pages = len(ctx.pages)
    
    # 点击"修改商品"
    clicked = list_frame.evaluate(f'''() => {{
        const rows = Array.from(document.querySelectorAll('tr'));
        for (const row of rows) {{
            if (row.innerText.includes('ID:{product['id']}')) {{
                const buttons = row.querySelectorAll('button');
                for (const btn of buttons) {{
                    if (btn.textContent.includes('修改商品')) {{
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
    
    if not clicked:
        print("❌ 未找到修改按钮")
        return False
    
    print("✅ 点击修改商品")
    
    # 等待新标签页打开
    edit_page = None
    for i in range(15):
        time.sleep(1)
        if len(ctx.pages) > initial_pages:
            # 找到新打开的页面
            for p in ctx.pages:
                if 'create' in p.url and p != list_page:
                    edit_page = p
                    break
            if edit_page:
                break
    
    if not edit_page:
        print("❌ 未找到编辑页面")
        return False
    
    print("✅ 找到编辑页面")
    time.sleep(3)
    
    # 获取编辑页面的iframe
    edit_frame = None
    for f in edit_page.frames:
        if 'admin-vue.rrzu.com' in f.url:
            edit_frame = f
            break
    
    if not edit_frame:
        print("❌ 未找到编辑iframe")
        edit_page.close()
        return False
    
    print("✅ 找到编辑iframe")
    
    # 关闭弹窗
    try:
        edit_frame.evaluate('''() => {
            setTimeout(() => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = btn.textContent || '';
                    if (text.includes('取消') || text.includes('关闭')) {
                        try { btn.click(); } catch(e) {}
                    }
                }
            }, 1000);
        }''')
        time.sleep(3)
    except:
        pass
    
    # 检查并修复
    print("🔧 检查并修复...")
    
    # 替换禁止词
    modified = edit_frame.evaluate('''() => {
        let count = 0;
        const inputs = document.querySelectorAll('input, textarea');
        
        for (const input of inputs) {
            let value = input.value || '';
            const original = value;
            
            value = value.replace(/租赁/g, '租用');
            value = value.replace(/出租/g, '提供使用');
            value = value.replace(/免押|免息|分期/g, '');
            value = value.replace(/最便宜|最低价|最/g, '');
            
            if (value !== original) {
                input.value = value;
                input.dispatchEvent(new Event('input', {bubbles: true}));
                input.dispatchEvent(new Event('change', {bubbles: true}));
                count++;
            }
        }
        
        return count;
    }''')
    
    if modified > 0:
        print(f"  ✅ 修改了 {modified} 处禁止词")
        time.sleep(2)
    else:
        print("  ✅ 未发现禁止词")
    
    # 提交审核
    print("📤 提交审核...")
    submitted = edit_frame.evaluate('''() => {
        const buttons = document.querySelectorAll('button');
        for (const btn of buttons) {
            if (btn.textContent.includes('提交审核')) {
                try {
                    btn.click();
                    return true;
                } catch(e) {}
            }
        }
        return false;
    }''')
    
    if submitted:
        print("  ✅ 点击提交审核")
        time.sleep(2)
        
        # 确认提交
        edit_frame.evaluate('''() => {
            const buttons = document.querySelectorAll('button');
            for (const btn of buttons) {
                const text = btn.textContent.trim();
                if (text === '确定' || text === '确认') {
                    try { btn.click(); } catch(e) {}
                }
            }
        }''')
        
        print("  ✅ 已提交")
        time.sleep(3)
        
        # 关闭编辑页面
        edit_page.close()
        return True
    else:
        print("  ❌ 未找到提交按钮")
        edit_page.close()
        return False

def main():
    print("🚀 开始批量修改已下架商品...\n")
    
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.connect_over_cdp(CDP_URL)
            ctx = browser.contexts[0]
            
            # 打开列表页
            list_page = ctx.new_page()
            list_page.goto('https://admin.rrzu.com/spu-view/list', wait_until='load', timeout=30000)
            time.sleep(5)
            
            # 关闭弹窗
            try:
                list_page.evaluate('''() => {
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
            
            # 获取列表iframe
            list_frame = None
            for f in list_page.frames:
                if 'admin-vue.rrzu.com' in f.url or f.name == 'rrzuji':
                    list_frame = f
                    break
            
            if not list_frame:
                print("❌ 未找到列表iframe")
                list_page.close()
                return
            
            # 切换到已下架标签
            list_frame.evaluate('''() => {
                const elements = Array.from(document.querySelectorAll('*'));
                for (const el of elements) {
                    if ((el.textContent || '').trim() === '已下架') {
                        try { el.click(); } catch(e) {}
                    }
                }
            }''')
            time.sleep(4)
            
            # 逐个处理
            success_count = 0
            fail_count = 0
            
            for idx, product in enumerate(PRODUCTS, 1):
                print(f"\n[{idx}/{len(PRODUCTS)}]")
                
                if fix_product(ctx, list_page, list_frame, product):
                    success_count += 1
                else:
                    fail_count += 1
                
                # 刷新列表页
                if idx < len(PRODUCTS):
                    list_page.reload(wait_until='load', timeout=30000)
                    time.sleep(5)
                    
                    # 重新获取iframe
                    list_frame = None
                    for f in list_page.frames:
                        if 'admin-vue.rrzu.com' in f.url or f.name == 'rrzuji':
                            list_frame = f
                            break
                    
                    if list_frame:
                        # 切换到已下架标签
                        list_frame.evaluate('''() => {
                            const elements = Array.from(document.querySelectorAll('*'));
                            for (const el of elements) {
                                if ((el.textContent || '').trim() === '已下架') {
                                    try { el.click(); } catch(e) {}
                                }
                            }
                        }''')
                        time.sleep(4)
            
            # 汇总
            print(f"\n{'='*60}")
            print(f"📊 处理完成:")
            print(f"  ✅ 成功: {success_count}")
            print(f"  ❌ 失败: {fail_count}")
            print(f"  📦 总计: {len(PRODUCTS)}")
            
            list_page.close()
            
        except Exception as e:
            print(f"\n❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
