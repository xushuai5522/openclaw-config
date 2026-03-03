#!/usr/bin/env python3
"""
直接操作已打开的编辑页面
"""
import time
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"

def fix_edit_page(page):
    """修改单个编辑页面"""
    url = page.url
    product_id = url.split('id=')[1].split('&')[0] if 'id=' in url else '未知'
    
    print(f"\n{'='*60}")
    print(f"📝 处理商品 ID:{product_id}")
    print(f"{'='*60}")
    
    # 等待页面加载
    time.sleep(3)
    
    # 获取iframe
    frame = None
    for f in page.frames:
        if 'admin-vue.rrzu.com' in f.url:
            frame = f
            break
    
    if not frame:
        print("❌ 未找到iframe")
        return False
    
    print("✅ 找到iframe")
    
    # 关闭弹窗
    try:
        frame.evaluate('''() => {
            const buttons = document.querySelectorAll('button');
            for (const btn of buttons) {
                const text = btn.textContent || '';
                if (text.includes('取消') || text.includes('关闭')) {
                    try { btn.click(); } catch(e) {}
                }
            }
        }''')
        time.sleep(2)
    except:
        pass
    
    # 替换禁止词
    print("🔧 检查并修复...")
    modified = frame.evaluate('''() => {
        let count = 0;
        const inputs = document.querySelectorAll('input, textarea');
        
        for (const input of inputs) {
            let value = input.value || '';
            const original = value;
            
            value = value.replace(/租赁/g, '租用');
            value = value.replace(/出租/g, '提供使用');
            value = value.replace(/免押|免息|分期/g, '');
            value = value.replace(/最便宜|最低价/g, '');
            value = value.replace(/最(?!高|低|长|短)/g, '');
            
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
        print(f"  ✅ 修改了 {modified} 处")
        time.sleep(2)
    else:
        print("  ✅ 未发现需要修改的内容")
    
    # 提交审核
    print("📤 提交审核...")
    submitted = frame.evaluate('''() => {
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
        frame.evaluate('''() => {
            const buttons = document.querySelectorAll('button');
            for (const btn of buttons) {
                const text = btn.textContent.trim();
                if (text === '确定' || text === '确认') {
                    try { btn.click(); } catch(e) {}
                }
            }
        }''')
        
        print("  ✅ 已提交")
        time.sleep(2)
        return True
    else:
        print("  ❌ 未找到提交按钮")
        return False

def main():
    print("🚀 处理已打开的编辑页面...\n")
    
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.connect_over_cdp(CDP_URL)
            ctx = browser.contexts[0]
            
            # 找到所有编辑页面
            edit_pages = []
            for p in ctx.pages:
                if 'spu-view/create' in p.url and 'id=' in p.url:
                    edit_pages.append(p)
            
            print(f"找到 {len(edit_pages)} 个编辑页面\n")
            
            if not edit_pages:
                print("❌ 没有打开的编辑页面")
                return
            
            # 逐个处理
            success_count = 0
            fail_count = 0
            
            for idx, page in enumerate(edit_pages, 1):
                print(f"\n[{idx}/{len(edit_pages)}]")
                
                if fix_edit_page(page):
                    success_count += 1
                    # 关闭已处理的页面
                    time.sleep(2)
                    page.close()
                else:
                    fail_count += 1
            
            # 汇总
            print(f"\n{'='*60}")
            print(f"📊 处理完成:")
            print(f"  ✅ 成功: {success_count}")
            print(f"  ❌ 失败: {fail_count}")
            print(f"  📦 总计: {len(edit_pages)}")
            
        except Exception as e:
            print(f"\n❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
