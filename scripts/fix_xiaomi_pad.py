#!/usr/bin/env python3
"""
单独修复小米平板5Pro - 添加规格信息
"""
import time
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"

def main():
    print("🚀 修复小米平板5Pro...")
    
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.connect_over_cdp(CDP_URL)
            ctx = browser.contexts[0]
            
            # 创建新页面（避免复用导致的问题）
            page = ctx.new_page()
            
            product_id = "381497"
            edit_url = f"https://admin.rrzu.com/spu-view/create?id={product_id}"
            
            print(f"📝 打开编辑页面...")
            page.goto(edit_url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(5)
            
            # 关闭弹窗
            try:
                page.evaluate('''() => {
                    const buttons = document.querySelectorAll('button');
                    for (const btn of buttons) {
                        const text = btn.textContent || '';
                        if (text.includes('取消') || text.includes('关闭') || text.includes('跳过')) {
                            btn.click();
                            break;
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
                return
            
            print("✅ 找到iframe")
            
            # 先查看当前套餐名称
            current_packages = frame.evaluate('''() => {
                const inputs = document.querySelectorAll('input');
                const packages = [];
                for (const input of inputs) {
                    const value = input.value || '';
                    if (value.includes('归还') || value.includes('续租')) {
                        packages.push(value);
                    }
                }
                return packages;
            }''')
            
            print(f"📦 当前套餐: {current_packages}")
            
            # 修改套餐名称，添加规格
            modified = frame.evaluate('''() => {
                const inputs = document.querySelectorAll('input');
                let count = 0;
                
                for (const input of inputs) {
                    const value = input.value || '';
                    // 找到套餐名称输入框
                    if ((value.includes('归还') || value.includes('续租')) && !value.includes('GB')) {
                        // 添加规格：128GB+6GB
                        const newValue = '128GB+6GB ' + value;
                        
                        // 设置新值
                        input.value = newValue;
                        
                        // 触发Vue事件
                        input.dispatchEvent(new Event('input', {bubbles: true}));
                        input.dispatchEvent(new Event('change', {bubbles: true}));
                        input.dispatchEvent(new Event('blur', {bubbles: true}));
                        
                        count++;
                    }
                }
                
                return count;
            }''')
            
            print(f"✅ 修改了 {modified} 个套餐名称")
            time.sleep(2)
            
            # 再次查看修改后的套餐
            updated_packages = frame.evaluate('''() => {
                const inputs = document.querySelectorAll('input');
                const packages = [];
                for (const input of inputs) {
                    const value = input.value || '';
                    if (value.includes('归还') || value.includes('续租')) {
                        packages.push(value);
                    }
                }
                return packages;
            }''')
            
            print(f"📦 修改后套餐: {updated_packages}")
            
            # 提交审核
            print("📤 提交审核...")
            frame.evaluate('''() => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    if (btn.textContent.includes('提交审核')) {
                        btn.click();
                        break;
                    }
                }
            }''')
            time.sleep(2)
            
            # 确认提交
            frame.evaluate('''() => {
                const confirmBtn = document.querySelector('button.el-button--primary');
                if (confirmBtn && confirmBtn.textContent.includes('确定')) {
                    confirmBtn.click();
                }
            }''')
            time.sleep(3)
            
            print("✅ 已提交审核")
            
            # 关闭页面
            page.close()
            
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
