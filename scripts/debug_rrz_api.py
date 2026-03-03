#!/usr/bin/env python3
"""
调试：查看人人租API实际返回内容
"""
import requests
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"

def main():
    # 获取Cookie
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]
        cookies = ctx.cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies if 'rrzu.com' in c['domain']}
    
    print(f"✅ 获取到 {len(cookie_dict)} 个Cookie")
    
    # 测试API
    url = 'https://admin-vue.rrzu.com/api/spu/list'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://admin.rrzu.com/'
    }
    
    try:
        resp = requests.get(url, headers=headers, cookies=cookie_dict, timeout=10)
        print(f"\n状态码: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('Content-Type')}")
        print(f"\n返回内容前500字符:")
        print(resp.text[:500])
        
        # 尝试解析JSON
        try:
            data = resp.json()
            print(f"\n✅ JSON解析成功")
            print(f"Keys: {list(data.keys())}")
        except:
            print(f"\n❌ 不是有效的JSON")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == '__main__':
    main()
