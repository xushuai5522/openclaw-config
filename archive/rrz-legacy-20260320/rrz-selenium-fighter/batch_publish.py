#!/usr/bin/env python3
"""
批量发布脚本 - 从JSON文件读取商品列表并批量发布
"""

import json
import os
import sys
import time
from rrz_selenium import RRZSeleniumPublisher


def load_products(json_file):
    """从JSON文件加载商品列表"""
    if not os.path.exists(json_file):
        print(f"❌ 文件不存在: {json_file}")
        return []
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('products', [])


def batch_publish(products, phone, password, headless=False):
    """批量发布商品"""
    publisher = RRZSeleniumPublisher(headless=headless)
    
    try:
        # 初始化并登录
        publisher.setup_driver()
        
        if not publisher.login(phone, password):
            print("❌ 登录失败，终止批量发布")
            return
        
        print(f"\n📦 开始批量发布 {len(products)} 个商品\n")
        
        success_count = 0
        fail_count = 0
        
        for idx, product in enumerate(products, 1):
            print(f"\n{'='*60}")
            print(f"[{idx}/{len(products)}] 发布商品: {product.get('title', '未命名')}")
            print('='*60)
            
            try:
                # 获取图片路径
                image_paths = product.get('images', [])
                
                # 发布商品
                if publisher.publish_product(product, image_paths):
                    success_count += 1
                    print(f"✅ 第{idx}个商品发布成功")
                else:
                    fail_count += 1
                    print(f"❌ 第{idx}个商品发布失败")
                
                # 间隔时间，避免频繁操作
                if idx < len(products):
                    wait_time = 5
                    print(f"\n⏳ 等待{wait_time}秒后继续...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                fail_count += 1
                print(f"❌ 第{idx}个商品发布异常: {e}")
                continue
        
        # 汇总结果
        print(f"\n{'='*60}")
        print("批量发布完成")
        print('='*60)
        print(f"✅ 成功: {success_count}")
        print(f"❌ 失败: {fail_count}")
        print(f"📊 总计: {len(products)}")
        
    finally:
        publisher.close()


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("用法: python batch_publish.py <products.json>")
        print("示例: python batch_publish.py products_example.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    # 读取配置
    phone = os.getenv('RRZ_PHONE')
    password = os.getenv('RRZ_PASSWORD')
    headless = os.getenv('HEADLESS', 'false').lower() == 'true'
    
    if not phone or not password:
        print("❌ 请先配置环境变量 RRZ_PHONE 和 RRZ_PASSWORD")
        sys.exit(1)
    
    # 加载商品列表
    products = load_products(json_file)
    
    if not products:
        print("❌ 没有找到商品数据")
        sys.exit(1)
    
    print(f"📋 已加载 {len(products)} 个商品")
    
    # 确认发布
    confirm = input(f"\n确认批量发布这 {len(products)} 个商品吗？(y/n): ")
    if confirm.lower() != 'y':
        print("❌ 已取消")
        sys.exit(0)
    
    # 开始批量发布
    batch_publish(products, phone, password, headless)


if __name__ == '__main__':
    main()
