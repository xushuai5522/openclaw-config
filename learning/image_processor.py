#!/usr/bin/env python3
"""
电商图片处理工具
1. 从闲鱼数据获取商品图片
2. 去除水印
3. 裁剪成白底图（满足平台要求：600x600px以上，纯白底）
"""

import os
import json
import requests
from PIL import Image, ImageEnhance
import urllib.parse

# 闲鱼数据目录
XIANYU_DIR = "/Users/xs/.openclaw/workspace/xianyu-monitor/jsonl"
OUTPUT_DIR = "/Users/xs/.openclaw/workspace/product_images"

def get_product_images(keyword: str, max_products: int = 3):
    """从闲鱼数据获取商品图片URL"""
    
    # 查找匹配的jsonl文件
    files = os.listdir(XIANYU_DIR)
    matched_file = None
    
    for f in files:
        if keyword.lower() in f.lower() and f.endswith('.jsonl'):
            matched_file = os.path.join(XIANYU_DIR, f)
            break
    
    if not matched_file:
        print(f"未找到匹配 {keyword} 的数据文件")
        return []
    
    # 读取数据
    images = []
    with open(matched_file, 'r') as f:
        for i, line in enumerate(f):
            if i >= max_products:
                break
            try:
                data = json.loads(line)
                info = data.get('商品信息', {})
                main_img = info.get('商品主图链接', '')
                if main_img:
                    images.append({
                        'title': info.get('商品标题', ''),
                        'price': info.get('当前售价', ''),
                        'url': main_img
                    })
            except:
                continue
    
    return images


def download_image(url: str, output_path: str) -> bool:
    """下载图片"""
    try:
        # 处理特殊格式
        url = url.replace('heic', 'jpg')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(resp.content)
            return True
    except Exception as e:
        print(f"下载失败: {e}")
    return False


def remove_watermark(img: Image.Image) -> Image.Image:
    """去除水印（简单版：边缘裁剪）"""
    width, height = img.size
    
    # 如果图片有明显的边缘水印，裁剪掉边缘
    # 常见水印位置：右下角
    crop_box = (0, 0, int(width * 0.95), int(height * 0.95))
    
    return img.crop(crop_box)


def make_white_background(img: Image.Image, target_size: int = 800) -> Image.Image:
    """
    将图片转换为白底图
    满足平台要求：600x600px以上，纯白底
    """
    # 转换为RGB模式
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # 调整图片大小（保持比例）
    width, height = img.size
    if width > height:
        new_width = target_size
        new_height = int(height * target_size / width)
    else:
        new_height = target_size
        new_width = int(width * target_size / height)
    
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # 创建白底图
    background = Image.new('RGB', (target_size, target_size), (255, 255, 255))
    
    # 居中粘贴
    paste_x = (target_size - new_width) // 2
    paste_y = (target_size - new_height) // 2
    background.paste(img, (paste_x, paste_y))
    
    return background


def process_product(keyword: str) -> list:
    """处理商品图片"""
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 获取图片URL
    print(f"搜索: {keyword}")
    products = get_product_images(keyword)
    
    if not products:
        print(f"未找到商品: {keyword}")
        return []
    
    print(f"找到 {len(products)} 个商品")
    
    output_files = []
    
    for i, product in enumerate(products):
        print(f"\n处理 {i+1}: {product['title'][:30]}")
        
        # 下载图片
        temp_path = f"/tmp/temp_product_{i}.jpg"
        if download_image(product['url'], temp_path):
            try:
                # 打开图片
                img = Image.open(temp_path)
                print(f"  原始尺寸: {img.size}")
                
                # 去除水印
                img = remove_watermark(img)
                
                # 转换为白底图
                img = make_white_background(img, target_size=800)
                print(f"  处理后尺寸: {img.size}")
                
                # 保存
                safe_name = keyword.replace(' ', '_')[:20]
                output_path = f"{OUTPUT_DIR}/{safe_name}_{i+1}.jpg"
                img.save(output_path, 'JPEG', quality=95)
                print(f"  保存到: {output_path}")
                output_files.append(output_path)
                
            except Exception as e:
                print(f"  处理失败: {e}")
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    return output_files


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
    else:
        keyword = "DDR4 16G 笔记本内存"
    
    process_product(keyword)
