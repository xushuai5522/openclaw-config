#!/usr/bin/env python3
"""
人人租页面结构分析工具
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def analyze_login_page():
    """分析登录页面结构"""
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    chromedriver_path = os.path.expanduser('~/bin/chromedriver')
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print("🔍 打开登录页面...")
        driver.get('https://admin.rrzu.com/')
        time.sleep(5)
        
        # 截图
        screenshot_path = '/Users/xs/.openclaw/workspace/projects/rrz-mac-runner/login_page.png'
        driver.save_screenshot(screenshot_path)
        print(f"📸 截图已保存: {screenshot_path}")
        
        # 保存HTML
        html_path = '/Users/xs/.openclaw/workspace/projects/rrz-mac-runner/login_page.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"📄 HTML已保存: {html_path}")
        
        # 查找所有input元素
        print("\n📋 所有input元素:")
        inputs = driver.find_elements('tag name', 'input')
        for i, inp in enumerate(inputs):
            try:
                print(f"  [{i}] type={inp.get_attribute('type')} placeholder={inp.get_attribute('placeholder')} name={inp.get_attribute('name')}")
            except:
                pass
        
        # 查找所有button元素
        print("\n📋 所有button元素:")
        buttons = driver.find_elements('tag name', 'button')
        for i, btn in enumerate(buttons):
            try:
                print(f"  [{i}] text={btn.text} class={btn.get_attribute('class')}")
            except:
                pass
        
        print("\n⏳ 浏览器将在30秒后关闭...")
        time.sleep(30)
        
    finally:
        driver.quit()

if __name__ == '__main__':
    analyze_login_page()
