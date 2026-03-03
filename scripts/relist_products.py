#!/usr/bin/env python3
"""
通过API查找并重新上架已下架的商品
"""
import requests
import json
import time
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"

def get_cookies():
    """从浏览器获取Cookie"""
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]
        cookies = ctx.cookies()
        return {c['name']: c['value'] for c in cookies if 'rrzu.com' in c['domain']}

def get_offline_products(cookies):
    """获取已下架商品列表"""
    url = 'https://admin-vue.rrzu.com/api/spu/list'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://admin.rrzu.com/'
    }
    
    params = {
        'page': 1,
        'page_size': 100,
        'status': 4  # 4=已下架
    }
    
    try:
        resp = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=10)
        data = resp.json()
        
        if data.get('code') == 0 and 'data' in data:
            products = data['data'].get('list', [])
            return products
        else:
            print(f"⚠️ API返回异常: {data}")
            return []
    except Exception as e:
        print(f"❌ 获取商品列表失败: {e}")
        return []

def relist_product(product_id, cookies):
    """重新上架商品"""
    url = f'https://admin-vue.rrzu.com/api/spu/online/{product_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://admin.rrzu.com/',
        'Content-Type': 'application/json'
    }
    
    try:
        resp = requests.post(url, headers=headers, cookies=cookies, json={}, timeout=10)
        data = resp.json()
        
        if data.get('code') == 0:
            return True, "成功"
        else:
            return False, data.get('msg', '未知错误')
    except Exception as e:
        return False, str(e)

def main():
    print("🔍 查找已下架的商品...")
    
    # 1. 获取Cookie
    try:
        cookies = get_cookies()
        print("✅ 已获取Cookie")
    except Exception as e:
        print(f"❌ 获取Cookie失败: {e}")
        print("请确保浏览器已打开人人租后台并登录")
        return
    
    # 2. 获取已下架商品
    products = get_offline_products(cookies)
    
    if not products:
        print("✅ 没有已下架的商品")
        return
    
    print(f"\n📦 找到 {len(products)} 个已下架商品:")
    for p in products:
        print(f"  - {p.get('name', '未知')} (ID:{p.get('id')})")
    
    # 3. 逐个重新上架
    print(f"\n🚀 开始重新上架...")
    
    success_count = 0
    fail_count = 0
    
    for product in products:
        product_id = product.get('id')
        product_name = product.get('name', '未知')
        
        print(f"\n{'='*60}")
        print(f"📝 处理: {product_name} (ID:{product_id})")
        
        success, msg = relist_product(product_id, cookies)
        
        if success:
            print(f"✅ 上架成功")
            success_count += 1
        else:
            print(f"❌ 上架失败: {msg}")
            fail_count += 1
        
        time.sleep(1)  # 避免请求过快
    
    # 4. 汇总
    print(f"\n{'='*60}")
    print(f"📊 处理完成:")
    print(f"  - 成功: {success_count}")
    print(f"  - 失败: {fail_count}")
    print(f"  - 总计: {len(products)}")

if __name__ == '__main__':
    main()
