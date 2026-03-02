#!/usr/bin/env python3
"""
图片处理工作流 - 完整版
"""
import os
import sys
import time
import requests

# 添加API稳定性模块路径
sys.path.insert(0, '/Users/xs/.openclaw/workspace')
from api_stability import call_api_with_retry

API_KEY = "675362ca-6313-43e5-a705-3046f668e2b1"
BASE_DIR = "/Users/xs/.openclaw/workspace/图库/电脑/MacStudio/M4Max"

def main():
    print("=== 图片处理工作流 ===\n")
    
    # 步骤1: 爬取图片
    print("步骤1: 爬取图片...")
    os.makedirs(BASE_DIR, exist_ok=True)
    
    # 尝试获取图片URL列表（从已知的店铺）
    image_urls = [
        # 店铺1 - Apple Store
        ("shop1_1", "https://gw.alicdn.com/imgextra/i4/1917047079/O1CN01EN7EeY22AEmw7hjJB_!!1917047079.jpg"),
        ("shop1_2", "https://gw.alicdn.com/imgextra/i1/1917047079/O1CN01EjvDIN22AEmvfhYfq_!!1917047079.jpg"),
        ("shop1_3", "https://gw.alicdn.com/imgextra/i3/1917047079/O1CN01rTt1qJ22AEmw7hnSa_!!1917047079.jpg"),
    ]
    
    # 下载图片
    for name, url in image_urls:
        path = f"{BASE_DIR}/{name}.jpg"
        if not os.path.exists(path):
            print(f"  下载 {name}...")
            os.system(f"curl -sL -o {path} '{url}'")
    
    # 步骤2: AI初筛
    print("\n步骤2: AI初筛...")
    valid_images = []
    max_retries = 5
    retry_count = 0
    
    while len(valid_images) < 6 and retry_count < max_retries:
        print(f"  尝试 {retry_count + 1}/{max_retries}...")
        
        # 筛选图片
        for name, url in image_urls:
            result = call_api_with_retry(
                "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "doubao-seed-1-6-vision-250815",
                    "messages": [{"role": "user", "content": [
                        {"type": "text", "text": "判断是否为Mac Studio实体商品主图，输出：是/否"},
                        {"type": "image_url", "image_url": {"url": url}}
                    ]}],
                    "max_tokens": 50
                },
                timeout=180
            )
            
            if result:
                content = result.get('choices',[{}])[0].get('message',{}).get('content','')
                if "是" in content:
                    valid_images.append((name, url))
                    print(f"    {name}: ✅")
        
        print(f"  有效图片: {len(valid_images)}/6")
        
        if len(valid_images) < 6:
            print(f"  数量不足，继续尝试... ({retry_count + 1}/{max_retries})")
            retry_count += 1
            time.sleep(5)
    
    print(f"\n=== 初筛完成 ===")
    print(f"有效图片: {len(valid_images)}")
    
    if len(valid_images) >= 3:
        print("✅ 满足最低要求(3张)，继续后续流程")
    else:
        print(f"⚠️ 仍然不足6张，但有{len(valid_images)}张可用")

if __name__ == "__main__":
    main()
