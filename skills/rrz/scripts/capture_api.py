#!/usr/bin/env python3
"""
人人租API抓包脚本 - 监听网络请求并记录API调用
"""
import json
import time
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"
OUTPUT_FILE = "/Users/xs/.openclaw/workspace/skills/rrz/scripts/api_captured.json"

def capture_requests():
    """连接浏览器并监听网络请求"""
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
            print("未找到人人租后台页面，请先在浏览器中打开 https://admin.rrzu.com")
            return
        
        print(f"已连接到页面: {page.url}")
        print("开始监听网络请求...")
        print("请在浏览器中操作（创建/编辑商品、上传图片等）")
        print("按 Ctrl+C 停止监听\n")
        
        # 监听请求
        def handle_request(request):
            url = request.url
            # 只记录API请求
            if any(keyword in url for keyword in ['api', 'admin-vue.rrzu.com', 'upload', 'product', 'goods']):
                req_data = {
                    'timestamp': time.time(),
                    'method': request.method,
                    'url': url,
                    'headers': dict(request.headers),
                    'post_data': request.post_data if request.method == 'POST' else None
                }
                captured.append(req_data)
                print(f"[{request.method}] {url}")
        
        # 监听响应
        def handle_response(response):
            url = response.url
            if any(keyword in url for keyword in ['api', 'admin-vue.rrzu.com', 'upload', 'product', 'goods']):
                try:
                    # 尝试获取响应体
                    body = response.body()
                    # 查找对应的请求
                    for req in captured:
                        if req['url'] == url and 'response' not in req:
                            req['response'] = {
                                'status': response.status,
                                'headers': dict(response.headers),
                                'body': body.decode('utf-8', errors='ignore')[:5000]  # 限制长度
                            }
                            break
                except Exception as e:
                    pass
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # 保持监听
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n停止监听，保存数据...")
            
    finally:
        # 保存捕获的数据
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(captured, f, ensure_ascii=False, indent=2)
        print(f"已保存 {len(captured)} 条请求到: {OUTPUT_FILE}")
        pw.stop()

if __name__ == '__main__':
    capture_requests()
