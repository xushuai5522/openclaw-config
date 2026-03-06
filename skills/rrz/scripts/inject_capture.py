#!/usr/bin/env python3
"""
通过浏览器注入JavaScript获取API信息
"""
from playwright.sync_api import sync_playwright
import json
import time

CDP_URL = "http://127.0.0.1:18800"

def inject_and_capture():
    """注入JS代码拦截fetch和xhr请求"""
    
    pw = sync_playwright().start()
    
    try:
        browser = pw.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        
        # 找到人人租页面
        page = None
        for p in context.pages:
            if 'rrzu.com' in p.url:
                page = p
                break
        
        if not page:
            print("❌ 未找到人人租页面")
            return
        
        print(f"✓ 找到页面: {page.url}")
        
        # 注入拦截代码
        inject_code = """
        (function() {
            window.capturedRequests = [];
            
            // 拦截fetch
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                const options = args[1] || {};
                
                window.capturedRequests.push({
                    type: 'fetch',
                    url: url,
                    method: options.method || 'GET',
                    headers: options.headers,
                    body: options.body,
                    timestamp: Date.now()
                });
                
                return originalFetch.apply(this, args);
            };
            
            // 拦截XMLHttpRequest
            const originalOpen = XMLHttpRequest.prototype.open;
            const originalSend = XMLHttpRequest.prototype.send;
            
            XMLHttpRequest.prototype.open = function(method, url) {
                this._captureData = { method, url, timestamp: Date.now() };
                return originalOpen.apply(this, arguments);
            };
            
            XMLHttpRequest.prototype.send = function(body) {
                if (this._captureData) {
                    this._captureData.body = body;
                    window.capturedRequests.push({
                        type: 'xhr',
                        ...this._captureData
                    });
                }
                return originalSend.apply(this, arguments);
            };
            
            console.log('✓ API拦截器已注入');
        })();
        """
        
        print("注入拦截代码...")
        page.evaluate(inject_code)
        
        print("\n✓ 拦截器已激活")
        print("请在浏览器中操作（刷新页面、查看商品、编辑等）")
        print("等待30秒后收集数据...\n")
        
        # 等待用户操作
        time.sleep(30)
        
        # 获取捕获的请求
        print("收集捕获的请求...")
        captured = page.evaluate("window.capturedRequests || []")
        
        print(f"\n✓ 捕获到 {len(captured)} 条请求")
        
        # 保存数据
        output_file = "/Users/xs/.openclaw/workspace/skills/rrz/scripts/api_captured.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(captured, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 数据已保存到: {output_file}")
        
        # 显示部分结果
        if captured:
            print("\n捕获的API示例：")
            for req in captured[:5]:
                print(f"  [{req.get('method')}] {req.get('url')}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pw.stop()

if __name__ == '__main__':
    inject_and_capture()
