#!/usr/bin/env python3
"""
使用CDP直接获取Chrome网络日志
适用于已经打开的人人租后台页面
"""
import json
import requests
import time
from datetime import datetime

CDP_URL = "http://127.0.0.1:18800"

def get_targets():
    """获取所有标签页"""
    response = requests.get(f"{CDP_URL}/json")
    return response.json()

def find_rrz_target():
    """找到人人租后台的标签页"""
    targets = get_targets()
    for target in targets:
        if 'admin.rrzu.com' in target.get('url', ''):
            return target
    return None

def get_network_log(target_id):
    """获取网络日志（通过CDP命令）"""
    # 这个方法需要WebSocket连接，比较复杂
    # 改用更简单的方法：直接读取Chrome的网络日志
    pass

def main():
    """主函数"""
    print("查找人人租后台标签页...")
    target = find_rrz_target()
    
    if not target:
        print("✗ 未找到人人租后台页面")
        print("请先在浏览器中打开: https://admin.rrzu.com")
        return
    
    print(f"✓ 找到页面: {target['title']}")
    print(f"  URL: {target['url']}")
    print(f"  Target ID: {target['id']}")
    
    print("\n提示：")
    print("由于CDP网络日志获取较复杂，建议使用以下方法：")
    print("\n方法1：浏览器开发者工具")
    print("1. 在人人租后台页面按 F12")
    print("2. 切换到 Network 标签")
    print("3. 勾选 'Preserve log'")
    print("4. 进行操作（创建商品、上传图片等）")
    print("5. 右键请求 -> Copy -> Copy as cURL")
    print("6. 保存到文本文件")
    
    print("\n方法2：使用Playwright录制")
    print("运行: python3 capture_api.py")
    print("然后在浏览器中操作，脚本会自动记录")

if __name__ == '__main__':
    main()
