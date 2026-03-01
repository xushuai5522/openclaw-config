#!/usr/bin/env python3
"""
基于Playwright的图片爬虫
自动从网页提取并下载图片
"""

import os
import asyncio
from playwright.async_api import async_playwright
import requests
from PIL import Image
import hashlib
import re

class ImageCrawler:
    def __init__(self, output_dir="./images"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.downloaded = set()
        
    async def crawl(self, url: str, max_images: int = 10):
        """爬取网页图片"""
        
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            
            # 设置User-Agent
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            
            print(f"访问: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            # 等待商品加载
            await page.wait_for_timeout(5000)
            # 滚动页面触发加载更多
            await page.evaluate('window.scrollBy(0, 500)')
            await page.wait_for_timeout(2000)
            
            # 提取所有图片URL
            img_urls = await page.evaluate('''
                () => {
                    const urls = new Set();
                    
                    // 1. img标签
                    document.querySelectorAll('img').forEach(img => {
                        if (img.src && img.width > 200) {
                            urls.add(img.src);
                        }
                    });
                    
                    // 2. picture/source标签
                    document.querySelectorAll('source').forEach(source => {
                        if (source.srcset) {
                            const src = source.srcset.split(' ')[0];
                            if (src.startsWith('http')) {
                                urls.add(src);
                            }
                        }
                    });
                    
                    // 3. background-image
                    const elements = document.querySelectorAll('*');
                    elements.forEach(el => {
                        const style = el.getAttribute('style');
                        if (style && style.includes('url(')) {
                            const match = style.match(/url\(["\']?(http[^\"\')]+)["\']?\)/);
                            if (match) urls.add(match[1]);
                        }
                    });
                    
                    return Array.from(urls);
                }
            ''')
            
            print(f"找到 {len(img_urls)} 个图片URL")
            
            # 下载图片
            count = 0
            for img_url in img_urls:
                if count >= max_images:
                    break
                    
                # 过滤无效URL
                if not img_url or not img_url.startswith('http'):
                    continue
                if any(x in img_url.lower() for x in ['gif', 'icon', 'logo', 'avatar']):
                    continue
                    
                try:
                    if await self.download_image(img_url):
                        count += 1
                        print(f"下载成功 ({count}/{max_images}): {img_url[:50]}...")
                except Exception as e:
                    print(f"下载失败: {e}")
            
            await browser.close()
            print(f"完成! 共下载 {count} 张图片")
            
    async def download_image(self, url: str) -> bool:
        """下载单张图片"""
        try:
            # 生成文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
            ext = self.get_ext(url)
            filename = f"image_{url_hash}.{ext}"
            filepath = os.path.join(self.output_dir, filename)
            
            # 避免重复下载
            if url in self.downloaded:
                return False
            self.downloaded.add(url)
            
            # 下载
            resp = requests.get(url, timeout=30, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            
            if resp.status_code != 200:
                return False
                
            # 保存
            with open(filepath, 'wb') as f:
                f.write(resp.content)
                
            # 处理成白底图
            self.process_image(filepath)
            
            return True
            
        except Exception as e:
            return False
            
    def get_ext(self, url: str) -> str:
        """获取文件扩展名"""
        ext = re.search(r'\.(jpg|jpeg|png|webp|png)(\?|$)', url, re.I)
        return ext.group(1) if ext else 'jpg'
        
    def process_image(self, filepath: str):
        """处理图片成白底图"""
        try:
            img = Image.open(filepath)
            
            # 转为RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 缩放
            target = 800
            img.thumbnail((target, target), Image.Resampling.LANCZOS)
            
            # 白底
            bg = Image.new('RGB', (target, target), (255, 255, 255))
            bg.paste(img, ((target - img.width) // 2, (target - img.height) // 2))
            
            bg.save(filepath, 'JPEG', quality=95)
            
        except Exception as e:
            print(f"图片处理失败: {e}")


async def main():
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://www.apple.com.cn/mac-studio/"
        
    max_images = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    crawler = ImageCrawler(output_dir="./product_images")
    await crawler.crawl(url, max_images=max_images)


if __name__ == "__main__":
    asyncio.run(main())
