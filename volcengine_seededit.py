#!/usr/bin/env python3
"""
火山引擎 SeedEdit 图生图 - 正确API格式
"""
import requests
import json

# 配置
API_KEY = "675362ca-6313-43e5-a705-3046f668e2b1"
MODEL_ID = "doubao-seededit-3-0-i2i-250628"  # 正确的模型ID
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"

def generate_image(prompt, image_url=None):
    """图生图"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": MODEL_ID,
        "prompt": prompt,
        "size": "1024x1024",
    }
    
    # 添加参考图
    if image_url:
        payload["image"] = image_url
    
    print(f"=== 图生图 ===")
    print(f"Model: {MODEL_ID}")
    print(f"Prompt: {prompt}")
    print(f"Image: {image_url}")
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=120)
        print(f"\n状态: {response.status_code}")
        print(f"内容: {response.text[:3000]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                for img in data['data']:
                    if 'url' in img:
                        print(f"\n✅ 生成成功! 图片URL: {img['url']}")
                        return img['url']
        return None
    except Exception as e:
        print(f"失败: {e}")
        return None

if __name__ == "__main__":
    print("=== 火山引擎 SeedEdit 图生图测试 ===\n")
    
    # 测试 - 使用一个示例图片URL
    test_image = "https://via.placeholder.com/1024x1024.png"
    url = generate_image("将图片转换为iPad Pro产品图", test_image)
    
    if url:
        print(f"\n🎉 测试成功!")
