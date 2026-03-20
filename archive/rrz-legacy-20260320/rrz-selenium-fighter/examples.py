#!/usr/bin/env python3
"""
使用示例 - 展示如何使用RRZSeleniumPublisher
"""

from rrz_selenium import RRZSeleniumPublisher
import os


def example_1_basic_publish():
    """示例1: 基础发布流程"""
    print("\n" + "="*60)
    print("示例1: 基础发布流程")
    print("="*60)
    
    # 创建发布器
    publisher = RRZSeleniumPublisher(headless=False)
    
    try:
        # 1. 初始化浏览器
        publisher.setup_driver()
        
        # 2. 登录
        phone = os.getenv('RRZ_PHONE', '13800138000')
        password = os.getenv('RRZ_PASSWORD', 'password')
        
        if not publisher.login(phone, password):
            print("登录失败")
            return
        
        # 3. 准备商品数据
        product_data = {
            'title': '测试商品 - Selenium自动发布',
            'category': '数码产品',
            'description': '这是一个通过Selenium自动发布的测试商品',
            'pricing': {
                'daily_price': 10,
                'deposit': 100,
                'stock': 5
            }
        }
        
        # 4. 准备图片（替换为实际路径）
        image_paths = [
            # 'image1.jpg',
            # 'image2.jpg',
        ]
        
        # 5. 发布商品
        publisher.publish_product(product_data, image_paths)
        
        input("\n按回车键继续...")
        
    finally:
        publisher.close()


def example_2_handle_popup():
    """示例2: 处理弹窗"""
    print("\n" + "="*60)
    print("示例2: 弹窗处理演示")
    print("="*60)
    
    publisher = RRZSeleniumPublisher(headless=False)
    
    try:
        publisher.setup_driver()
        
        # 访问一个会弹窗的测试页面
        test_html = """
        <html>
        <body>
            <h1>弹窗测试</h1>
            <button onclick="alert('这是一个测试弹窗！')">点击触发弹窗</button>
            <script>
                // 3秒后自动弹窗
                setTimeout(() => {
                    alert('自动弹窗：Selenium可以轻松处理！');
                }, 3000);
            </script>
        </body>
        </html>
        """
        
        publisher.driver.get("data:text/html," + test_html)
        print("✅ 测试页面已加载，3秒后会自动弹窗...")
        
        # 等待并处理弹窗
        import time
        time.sleep(4)
        
        if publisher.handle_alert():
            print("✅ 弹窗已成功处理！")
        
        input("\n按回车键继续...")
        
    finally:
        publisher.close()


def example_3_multiple_products():
    """示例3: 发布多个商品"""
    print("\n" + "="*60)
    print("示例3: 批量发布多个商品")
    print("="*60)
    
    publisher = RRZSeleniumPublisher(headless=False)
    
    try:
        publisher.setup_driver()
        
        # 登录
        phone = os.getenv('RRZ_PHONE', '13800138000')
        password = os.getenv('RRZ_PASSWORD', 'password')
        
        if not publisher.login(phone, password):
            return
        
        # 准备多个商品
        products = [
            {
                'title': '商品A - 测试',
                'category': '数码产品',
                'description': '第一个测试商品',
                'pricing': {'daily_price': 10, 'deposit': 100, 'stock': 5}
            },
            {
                'title': '商品B - 测试',
                'category': '数码产品',
                'description': '第二个测试商品',
                'pricing': {'daily_price': 20, 'deposit': 200, 'stock': 3}
            },
        ]
        
        # 逐个发布
        for idx, product in enumerate(products, 1):
            print(f"\n发布第{idx}个商品: {product['title']}")
            publisher.publish_product(product, [])
            
            if idx < len(products):
                import time
                print("等待5秒...")
                time.sleep(5)
        
        print("\n✅ 所有商品发布完成")
        input("\n按回车键继续...")
        
    finally:
        publisher.close()


def main():
    """主菜单"""
    print("\n🚀 人人租Selenium自动化 - 使用示例")
    print("="*60)
    print("1. 基础发布流程")
    print("2. 弹窗处理演示")
    print("3. 批量发布多个商品")
    print("0. 退出")
    print("="*60)
    
    choice = input("\n请选择示例 (0-3): ")
    
    if choice == '1':
        example_1_basic_publish()
    elif choice == '2':
        example_2_handle_popup()
    elif choice == '3':
        example_3_multiple_products()
    elif choice == '0':
        print("再见！")
    else:
        print("无效选择")


if __name__ == '__main__':
    main()
