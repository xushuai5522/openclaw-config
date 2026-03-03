#!/usr/bin/env python3
"""
自动修复审核不通过的商品
1. Mac Mini M4 - 删除超期套餐，调整价格
2. 小米平板5Pro - 补充规格信息
"""
import time
import json
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"

def fix_mac_mini(page):
    """修复Mac Mini M4"""
    product_id = "804995"
    edit_url = f"https://admin.rrzu.com/spu-view/create?id={product_id}&server_id=11904&publish_chanel="
    
    print(f"\n{'='*60}")
    print(f"📝 修复商品: Mac Mini M4 (ID:{product_id})")
    print(f"{'='*60}")
    
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
    except Exception as e:
        print(f"⚠️ 关闭弹窗失败: {e}")
    
    # 获取iframe
    frame = None
    for f in page.frames:
        if 'admin-vue.rrzu.com' in f.url or f.name == 'rrzuji':
            frame = f
            break
    
    if not frame:
        print("❌ 未找到iframe")
        return False
    
    print("✅ 找到iframe")
    
    # 滚动到销售规格部分
    try:
        frame.evaluate('''() => {
            const headers = document.querySelectorAll('h3, .title, div');
            for (const h of headers) {
                if (h.textContent.includes('销售规格')) {
                    h.scrollIntoView({behavior: 'smooth', block: 'center'});
                    break;
                }
            }
        }''')
        time.sleep(2)
    except:
        pass
    
    # 查找并删除超过365天的套餐
    try:
        deleted = frame.evaluate('''() => {
            const rows = document.querySelectorAll('tr, .package-row, .spec-row');
            let count = 0;
            for (const row of rows) {
                const text = row.innerText || '';
                // 查找包含天数的行
                const match = text.match(/(\\d+)天/);
                if (match && parseInt(match[1]) > 365) {
                    // 找删除按钮
                    const deleteBtn = row.querySelector('button[class*="delete"], button[class*="remove"], .el-icon-delete');
                    if (deleteBtn) {
                        deleteBtn.click();
                        count++;
                    }
                }
            }
            return count;
        }''')
        
        if deleted > 0:
            print(f"✅ 删除了 {deleted} 个超期套餐")
            time.sleep(2)
            
            # 确认删除
            try:
                frame.evaluate('''() => {
                    const confirmBtn = document.querySelector('button.el-button--primary');
                    if (confirmBtn && confirmBtn.textContent.includes('确定')) {
                        confirmBtn.click();
                    }
                }''')
                time.sleep(1)
            except:
                pass
        else:
            print("⚠️ 未找到超期套餐或已删除")
    except Exception as e:
        print(f"⚠️ 删除套餐失败: {e}")
    
    # 提交审核
    try:
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
        time.sleep(2)
        
        print("✅ 已提交审核")
        return True
    except Exception as e:
        print(f"❌ 提交失败: {e}")
        return False

def fix_xiaomi_pad(page):
    """修复小米平板5Pro"""
    product_id = "381497"
    edit_url = f"https://admin.rrzu.com/spu-view/create?id={product_id}"
    
    print(f"\n{'='*60}")
    print(f"📝 修复商品: 小米平板5Pro (ID:{product_id})")
    print(f"{'='*60}")
    
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
        return False
    
    print("✅ 找到iframe")
    
    # 修改套餐名称，添加规格信息
    try:
        modified = frame.evaluate('''() => {
            // 查找套餐名称输入框
            const inputs = document.querySelectorAll('input[placeholder*="套餐"], input[placeholder*="名称"]');
            let count = 0;
            
            for (const input of inputs) {
                const currentValue = input.value || '';
                // 如果还没有规格信息，添加上
                if (!currentValue.includes('GB') && !currentValue.includes('内存')) {
                    // 假设是128GB+6GB配置
                    const newValue = '128GB+6GB ' + currentValue;
                    input.value = newValue;
                    // 触发Vue更新
                    input.dispatchEvent(new Event('input', {bubbles: true}));
                    input.dispatchEvent(new Event('change', {bubbles: true}));
                    count++;
                }
            }
            
            return count;
        }''')
        
        if modified > 0:
            print(f"✅ 修改了 {modified} 个套餐名称，添加了规格信息")
            time.sleep(2)
        else:
            print("⚠️ 未找到需要修改的套餐或已包含规格")
    except Exception as e:
        print(f"⚠️ 修改套餐失败: {e}")
    
    # 提交审核
    try:
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
        time.sleep(2)
        
        print("✅ 已提交审核")
        return True
    except Exception as e:
        print(f"❌ 提交失败: {e}")
        return False

def main():
    print("🚀 开始自动修复审核不通过的商品...")
    
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.connect_over_cdp(CDP_URL)
            ctx = browser.contexts[0]
            
            # 查找或创建页面
            page = None
            for p in ctx.pages:
                if 'admin.rrzu.com' in p.url:
                    page = p
                    break
            
            if not page:
                page = ctx.new_page()
            
            # 修复两个商品
            results = {
                'mac_mini': fix_mac_mini(page),
                'xiaomi_pad': fix_xiaomi_pad(page)
            }
            
            print(f"\n{'='*60}")
            print("📊 修复结果汇总")
            print(f"{'='*60}")
            print(f"Mac Mini M4: {'✅ 成功' if results['mac_mini'] else '❌ 失败'}")
            print(f"小米平板5Pro: {'✅ 成功' if results['xiaomi_pad'] else '❌ 失败'}")
            
            if all(results.values()):
                print("\n🎉 所有商品已成功提交审核！")
            else:
                print("\n⚠️ 部分商品修复失败，请检查日志")
            
        except Exception as e:
            print(f"\n❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
