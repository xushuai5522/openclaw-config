#!/usr/bin/env python3
"""
智能图片爬虫 - 基于浏览器的图片获取方案
支持从任意网页获取产品图片
"""

import os
import time
from playwright.sync_api import sync_playwright
from PIL import Image
import urllib.parse

class SmartImageCrawler:
    """智能图片爬虫"""
    
    def __init__(self, output_dir="/Users/xs/.openclaw/workspace/product_images"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.browser = None
        self.page = None
    
    def open_page(self, url: str, wait: int = 3):
        """打开页面"""
        if not self.browser:
            pw = sync_playwright().start()
            self.browser = pw.chromium.launch(headless=True)
            self.context = self.browser.new_context()
        
        self.page = self.context.new_page()
        self.page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(wait)
        return self
    
    def extract_images(self, min_width=300):
        """提取页面中所有图片"""
        images = self.page.evaluate(f'''
            () => {{
                const results = [];
                document.querySelectorAll('img').forEach((img, i) => {{
                    if (img.width >= {min_width} && img.src && img.src.startsWith('http')) {{
                        results.push({{
                            index: i,
                            src: img.src,
                            width: img.width,
                            height: img.height,
                            alt: img.alt || ''
                        }});
                    }}
                }});
                return results;
            }}
        ''')
        return images
    
    def search_and_extract(self, keyword: str, engine="bing", max_images=5):
        """搜索并提取图片"""
        # 编码关键词
        kw = urllib.parse.quote(keyword)
        
        # 选择搜索引擎
        if engine == "bing":
            search_url = f"https://www.bing.com/images/search?q={kw}"
        elif engine == "google":
            search_url = f"https://www.google.com/search?q={kw}&tbm=isch"
        elif engine == "baidu":
            search_url = f"https://image.baidu.com/search/index?word={kw}"
        else:
            search_url = f"https://www.bing.com/images/search?q={kw}"
        
        # 打开搜索页面
        self.open_page(search_url)
        
        # 提取图片
        images = self.extract_images(min_width=200)
        
        return images[:max_images]
    
    def download_image(self, url: str, timeout: int = 30):
        """下载图片"""
        import requests
        try:
            resp = requests.get(url, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            if resp.status_code == 200:
                return resp.content
        except Exception as e:
            print(f"下载失败: {e}")
        return None
    
    def save_image(self, content, filename: str):
        """保存图片"""
        if not content:
            return None
        
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(content)
        return filepath
    
    def process_to_white_background(self, image_path: str, target_size: int = 800) -> str:
        """处理成白底图"""
        img = Image.open(image_path)
        
        # 转换为RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 缩放
        img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        
        # 创建白底
        bg = Image.new('RGB', (target_size, target_size), (255, 255, 255))
        bg.paste(img, ((target_size - img.width) // 2, (target_size - img.height) // 2))
        
        # 保存
        output_path = image_path.replace('.jpg', '_processed.jpg').replace('.png', '_processed.jpg')
        bg.save(output_path, 'JPEG', quality=95)
        return output_path
    
    def crawl_product_images(self, keyword: str, max_images: int = 3) -> list:
        """爬取产品图片完整流程"""
        print(f"搜索: {keyword}")
        
        # 搜索图片
        images = self.search_and_extract(keyword, max_images=max_images)
        print(f"找到 {len(images)} 张图片")
        
        results = []
        
        for i, img_info in enumerate(images):
            print(f"\n处理图片 {i+1}: {img_info['src'][:50]}...")
            
            # 尝试直接下载
            content = self.download_image(img_info['src'])
            
            if content:
                # 保存原图
                ext = '.jpg' if 'jpg' in img_info['src'].lower() else '.png'
                filename = f"{keyword.replace(' ', '_')[:20]}_{i+1}{ext}"
                filepath = self.save_image(content, filename)
                
                if filepath:
                    # 处理成白底图
                    try:
                        processed = self.process_to_white_background(filepath)
                        print(f"  保存: {filepath}")
                        print(f"  处理: {processed}")
                        results.append(processed)
                    except Exception as e:
                        print(f"  处理失败: {e}")
            else:
                # 下载失败，尝试截图
                print(f"  下载失败，尝试截图...")
                screenshot_path = self.screenshot_from_browser(img_info['src'], keyword, i)
                if screenshot_path:
                    results.append(screenshot_path)
        
        return results
    
    def screenshot_from_browser(self, image_url: str, keyword: str, index: int) -> str:
        """用浏览器打开图片URL并截图"""
        try:
            # 用新标签页打开图片
            img_page = self.context.new_page()
            img_page.goto(image_url, timeout=15000)
            time.sleep(2)
            
            filename = f"{keyword.replace(' ', '_')[:20]}_{index+1}_screenshot.png"
            filepath = os.path.join(self.output_dir, filename)
            
            img_page.screenshot(path=filepath, full_page=False)
            img_page.close()
            
            # 处理成白底图
            return self.process_to_white_background(filepath)
        except Exception as e:
            print(f"  截图失败: {e}")
        return None
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            sync_playwright().stop()


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 smart_image_crawler.py <关键词>")
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    crawler = SmartImageCrawler()
    results = crawler.crawl_product_images(keyword, max_images=3)
    
    print(f"\n完成! 共获取 {len(results)} 张图片:")
    for r in results:
        print(f"  - {r}")
    
    crawler.close()


if __name__ == "__main__":
    main()
