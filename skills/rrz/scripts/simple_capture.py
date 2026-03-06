#!/usr/bin/env python3
"""
简单抓包脚本 - 只监听网络请求，不做自动化操作
"""
import json
import time
import signal
import sys
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"
OUTPUT_FILE = "/Users/xs/.openclaw/workspace/skills/rrz/scripts/api_captured.json"

captured = []

def signal_handler(sig, frame):
    """处理Ctrl+C"""
    print("\n\n停止监听，保存数据...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(captured, f, ensure_ascii=False, indent=2)
    print(f"✓ 已保存 {len(captured)} 条请求到: {OUTPUT_FILE}")
    sys.exit(0)

def simple_capture():
    """简单监听网络请求"""
    global captured
    
    signal.signal(signal.SIGINT, signal_handler)
    
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
        
        print(f"✓ 已连接到页面: {page.url}")
        print("\n开始监听网络请求...")
        print("请在浏览器中手动操作：")
        print("  1. 点击商品管理")
        print("  2. 查看商品列表")
        print("  3. 点击编辑/查看商品")
        print("  4. 查看图片上传组件")
        print("\n按 Ctrl+C 停止监听\n")
        
        # 监听请求
        def handle_request(request):
            url = request.url
            # 过滤API请求
            if any(kw in url for kw in ['api', 'admin', 'upload', 'product', 'goods', 'rrzu.com']):
                # 排除静态资源
                if not any(ext in url for ext in ['.js', '.css', '.png', '.jpg', '.gif', '.woff', '.ttf']):
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
                if not any(ext in url for ext in ['.js', '.css', '.png', '.jpg', '.gif', '.woff', '.ttf']):
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
        
        # 保持监听
        while True:
            time.sleep(1)
            
    finally:
        pw.stop()

if __name__ == '__main__':
    simple_capture()
