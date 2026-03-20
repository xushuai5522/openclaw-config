#!/usr/bin/env python3
"""
自动化抓包脚本 - 自动执行操作并记录API
"""
import json
import time
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"
OUTPUT_FILE = "/Users/xs/.openclaw/workspace/skills/rrz/scripts/api_captured.json"

def auto_capture():
    """自动执行操作并抓包"""
    captured = []
    
    pw = sync_playwright().start()
    try:
        browser = pw.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]
        
        # 找到人人租后台页面
        page = None
        for p in ctx.pages:
            if 'admin.rrzu.com' in p.url:
                page = p
                break
        
        if not page:
            print("❌ 未找到人人租后台页面")
            return
        
        print(f"✓ 已连接到页面: {page.url}\n")
        
        # 监听网络请求
        def handle_request(request):
            url = request.url
            if any(kw in url for kw in ['api', 'admin', 'upload', 'product', 'goods', 'rrzu.com']):
                req_data = {
                    'timestamp': time.time(),
                    'method': request.method,
                    'url': url,
                    'headers': dict(request.headers),
                    'post_data': request.post_data if request.method == 'POST' else None
                }
                captured.append(req_data)
                print(f"[{request.method}] {url}")
        
        def handle_response(response):
            url = response.url
            if any(kw in url for kw in ['api', 'admin', 'upload', 'product', 'goods', 'rrzu.com']):
                try:
                    body = response.body()
                    for req in captured:
                        if req['url'] == url and 'response' not in req:
                            req['response'] = {
                                'status': response.status,
                                'headers': dict(response.headers),
                                'body': body.decode('utf-8', errors='ignore')[:10000]
                            }
                            break
                except:
                    pass
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        print("开始执行自动化操作...\n")
        
        # 步骤1：等待页面加载
        print("1. 等待页面加载...")
        time.sleep(2)
        
        # 步骤2：尝试导航到商品管理
        print("2. 导航到商品管理...")
        try:
            # 查找商品管理菜单
            page.wait_for_timeout(1000)
            
            # 尝试点击商品管理相关链接
            selectors = [
                'text=商品管理',
                'text=商品列表',
                'a[href*="product"]',
                'a[href*="goods"]'
            ]
            
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        print(f"   找到元素: {selector}")
                        element.click()
                        time.sleep(3)
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"   导航失败: {e}")
        
        # 步骤3：等待商品列表加载
        print("3. 等待商品列表加载...")
        time.sleep(3)
        
        # 步骤4：尝试查看商品详情
        print("4. 尝试查看商品详情...")
        try:
            # 查找查看/编辑按钮
            buttons = [
                'text=查看',
                'text=编辑',
                'text=详情',
                'button:has-text("查看")',
                'button:has-text("编辑")'
            ]
            
            for btn in buttons:
                try:
                    element = page.locator(btn).first
                    if element.is_visible(timeout=2000):
                        print(f"   找到按钮: {btn}")
                        element.click()
                        time.sleep(3)
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"   查看详情失败: {e}")
        
        # 步骤5：等待详情页加载
        print("5. 等待详情页加载...")
        time.sleep(3)
        
        # 步骤6：滚动页面触发更多请求
        print("6. 滚动页面...")
        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)
        except:
            pass
        
        print("\n✓ 自动化操作完成")
        print(f"✓ 共捕获 {len(captured)} 条请求\n")
        
    finally:
        # 保存数据
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(captured, f, ensure_ascii=False, indent=2)
        print(f"✓ 数据已保存到: {OUTPUT_FILE}")
        pw.stop()

if __name__ == '__main__':
    auto_capture()
