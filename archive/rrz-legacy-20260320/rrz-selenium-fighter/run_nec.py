#!/usr/bin/env python3
"""
NEC服务器专用启动脚本
处理无显示器环境下的Chrome启动
"""

import os
import sys
from rrz_selenium import RRZSeleniumPublisher


def check_display():
    """检查是否有显示器"""
    display = os.environ.get('DISPLAY')
    if not display:
        print("⚠️  未检测到DISPLAY环境变量")
        print("🔧 尝试启动虚拟显示...")
        
        # 尝试使用Xvfb
        try:
            import subprocess
            subprocess.run(['which', 'Xvfb'], check=True, capture_output=True)
            
            # 启动Xvfb
            print("启动Xvfb虚拟显示...")
            os.environ['DISPLAY'] = ':99'
            subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'])
            print("✅ Xvfb已启动")
            return True
        except:
            print("❌ Xvfb未安装，建议安装: sudo apt-get install xvfb")
            print("💡 或者使用headless模式")
            return False
    else:
        print(f"✅ DISPLAY已设置: {display}")
        return True


def main():
    """NEC服务器启动入口"""
    print("🚀 NEC服务器 - 人人租自动化启动")
    print("="*50)
    
    # 检查显示环境
    has_display = check_display()
    
    # 读取配置
    phone = os.getenv('RRZ_PHONE')
    password = os.getenv('RRZ_PASSWORD')
    headless = os.getenv('HEADLESS', 'false').lower() == 'true'
    
    if not phone or not password:
        print("❌ 请先配置环境变量 RRZ_PHONE 和 RRZ_PASSWORD")
        print("💡 或创建.env文件")
        sys.exit(1)
    
    # 如果没有显示器，强制使用headless模式
    if not has_display:
        print("⚠️  无显示环境，强制使用headless模式")
        headless = True
    
    # 创建发布器
    publisher = RRZSeleniumPublisher(headless=headless)
    
    try:
        print("\n🔧 初始化浏览器...")
        publisher.setup_driver()
        
        print(f"\n🔐 登录账号: {phone}")
        if not publisher.login(phone, password):
            print("❌ 登录失败")
            sys.exit(1)
        
        print("\n✅ 登录成功！浏览器已就绪")
        print("💡 现在可以调用 publisher.publish_product() 发布商品")
        
        # 保持会话
        input("\n按回车键退出...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        publisher.close()


if __name__ == '__main__':
    main()
