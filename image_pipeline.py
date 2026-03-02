#!/usr/bin/env python3
"""
图片处理工作流 - 一键自动化
爬取 -> AI初筛 -> 抠图 -> 白底 -> AI审核 -> 命名
"""
import os, sys, json, base64, requests
from PIL import Image
from rembg import remove

# 配置
ZHONGZHUAN_API = "https://www.zhongzhuan.win/v1"
ZHONGZHUAN_KEY = "sk-5e5rZgZ17IiakvNWPDFCKfdSzhlvQ1AlZtv5zfnPcE9FUuYk"

def call_vision_api(image_path: str, prompt: str) -> str:
    """调用Vision API"""
    with open(image_path, 'rb') as f:
        img_data = base64.b64encode(f.read()).decode()
    
    resp = requests.post(
        f"{ZHONGZHUAN_API}/chat/completions",
        headers={"Authorization": f"Bearer {ZHONGZHUAN_KEY}", "Content-Type": "application/json"},
        json={"model": "aws.amazon/claude-opus-4-5:once",
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}}
            ]}],
            "max_tokens": 800},
        timeout=120
    )
    
    if resp.status_code == 200:
        return resp.json().get('choices',[{}])[0].get('message',{}).get('content','')
    return ""

def ai_filter(image_path: str) -> bool:
    """AI初筛 - 判断是否为商品主图"""
    prompt = "判断是否为合格的电商商品主图。标准：1.完整的实体商品 2.纯白底 3.商品在画面中央 4.无额外文字。输出是或否"
    result = call_vision_api(image_path, prompt)
    return "是" in result

def ai_audit(image_path: str) -> dict:
    """AI审核"""
    prompt = """审核图片是否符合人人租要求：
1. 底色是否纯白？
2. 尺寸是否>=600x600？
3. 是否有文字/水印？
4. 成色是几成新？
输出格式：简要说明后给出"通过"或"不通过" """
    result = call_vision_api(image_path, prompt)
    passed = "通过" in result and "不通过" not in result
    return {"passed": passed, "result": result}

def make_white_bg(input_path: str, output_path: str, size: int = 800) -> bool:
    """抠图 + 白底处理"""
    try:
        img = Image.open(input_path)
        # 抠图
        output = remove(img)
        # 叠加白底
        white_bg = Image.new('RGBA', (size, size), (255, 255, 255, 255))
        white_bg.paste(output, ((size-output.width)//2, (size-output.height)//2))
        white_bg.convert('RGB').save(output_path, 'JPEG', quality=95)
        return True
    except Exception as e:
        print(f"白底处理失败: {e}")
        return False

def process_workflow(image_urls: list, product_name: str, output_dir: str = "./output"):
    """执行完整工作流"""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📦 开始处理: {product_name}")
    print(f"📊 待处理图片数: {len(image_urls)}")
    
    passed_images = []
    
    for i, url in enumerate(image_urls):
        print(f"\n--- 处理第 {i+1}/{len(image_urls)} 张 ---")
        
        # 下载图片（简化版，需要自己实现）
        temp_path = f"{output_dir}/temp_{i}.jpg"
        # TODO: 实现图片下载
        
        # AI初筛
        if not ai_filter(temp_path):
            print(f"❌ AI初筛不通过")
            continue
        
        # 白底处理
        white_path = f"{output_dir}/white_{i}.jpg"
        if not make_white_bg(temp_path, white_path):
            print(f"❌ 白底处理失败")
            continue
        
        # AI审核
        audit = ai_audit(white_path)
        if not audit["passed"]:
            print(f"❌ AI审核不通过: {audit['result'][:100]}")
            continue
        
        # 命名
        final_name = f"{product_name}_{i+1}.jpg"
        final_path = f"{output_dir}/{final_name}"
        os.rename(white_path, final_path)
        
        print(f"✅ 通过！保存为: {final_name}")
        passed_images.append(final_path)
    
    print(f"\n🎉 完成！通过 {len(passed_images)}/{len(image_urls)} 张")
    return passed_images

if __name__ == "__main__":
    # 示例用法
    test_urls = ["https://example.com/image1.jpg"]
    process_workflow(test_urls, "测试商品")
