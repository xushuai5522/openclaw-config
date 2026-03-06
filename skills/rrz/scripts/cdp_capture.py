#!/usr/bin/env python3
"""
人人租API实战抓包 - 使用CDP直接获取网络日志
"""
import json
import time
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"
OUTPUT_FILE = "/Users/xs/.openclaw/workspace/skills/rrz/scripts/api_captured.json"

def capture_with_cdp():
    """使用CDP协议直接获取网络日志"""
    
    print("正在连接浏览器...")
    pw = sync_playwright().start()
    
    try:
        browser = pw.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        
        # 找到人人租页面
        page = None
        for p in context.pages:
            if 'admin.rrzu.com' in p.url or 'rrzu.com' in p.url:
                page = p
                break
        
        if not page:
            print("❌ 未找到人人租页面，请先打开 https://admin.rrzu.com")
            return
        
        print(f"✓ 找到页面: {page.url}\n")
        
        # 获取CDP session
        cdp = context.new_cdp_session(page)
        
        # 启用网络监控
        print("启用网络监控...")
        cdp.send('Network.enable')
        
        captured_requests = []
        
        # 监听网络请求
        def on_request(params):
            request = params
            url = request.get('request', {}).get('url', '')
            
            # 过滤API请求
            if any(kw in url for kw in ['api', 'admin', 'upload', 'product', 'goods']):
                if not any(ext in url for ext in ['.js', '.css', '.png', '.jpg', '.woff']):
                    req_data = {
                        'requestId': request.get('requestId'),
                        'timestamp': request.get('timestamp'),
                        'url': url,
                        'method': request.get('request', {}).get('method'),
                        'headers': request.get('request', {}).get('headers'),
                        'postData': request.get('request', {}).get('postData')
                    }
                    captured_requests.append(req_data)
                    print(f"[{req_data['method']}] {url}")
        
        def on_response(params):
            request_id = params.get('requestId')
            response = params.get('response', {})
            
            # 找到对应的请求并添加响应信息
            for req in captured_requests:
                if req.get('requestId') == request_id and 'response' not in req:
                    req['response'] = {
                        'status': response.get('status'),
                        'headers': response.get('headers')
                    }
                    break
        
        def on_response_body(params):
            request_id = params.get('requestId')
            
            # 获取响应体
            try:
                result = cdp.send('Network.getResponseBody', {'requestId': request_id})
                body = result.get('body', '')
                
                for req in captured_requests:
                    if req.get('requestId') == request_id:
                        if 'response' not in req:
                            req['response'] = {}
                        req['response']['body'] = body[:10000]  # 限制长度
                        break
            except:
                pass
        
        cdp.on('Network.requestWillBeSent', on_request)
        cdp.on('Network.responseReceived', on_response)
        cdp.on('Network.loadingFinished', on_response_body)
        
        print("\n✓ 网络监控已启动")
        print("\n请在浏览器中执行以下操作：")
        print("  1. 刷新页面或点击商品管理")
        print("  2. 查看商品列表")
        print("  3. 点击编辑某个商品")
        print("  4. 查看商品详情")
        print("  5. 滚动页面查看更多内容")
        print("\n监听30秒后自动保存...\n")
        
        # 监听30秒
        for i in range(30):
            time.sleep(1)
            if (i + 1) % 5 == 0:
                print(f"已监听 {i+1} 秒，捕获 {len(captured_requests)} 条请求...")
        
        print(f"\n✓ 监听完成，共捕获 {len(captured_requests)} 条请求")
        
        # 保存数据
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(captured_requests, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 数据已保存到: {OUTPUT_FILE}")
        
        # 禁用网络监控
        cdp.send('Network.disable')
        cdp.detach()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pw.stop()

if __name__ == '__main__':
    capture_with_cdp()
