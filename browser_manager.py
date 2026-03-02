#!/usr/bin/env python3
"""
浏览器稳定性管理模块v2
解决浏览器资源管理问题
"""
import os
import time
import subprocess

MAX_TABS = 3
CLEANUP_INTERVAL = 300

def get_chrome_count():
    """获取Chrome进程数"""
    try:
        result = subprocess.run(
            ["pgrep", "-fc", "Chrome"],
            capture_output=True,
            text=True
        )
        return int(result.stdout.strip()) if result.returncode == 0 else 0
    except:
        return 0

def cleanup_chrome():
    """清理Chrome子进程"""
    print("🧹 清理Chrome子进程...")
    subprocess.run(["pkill", "-f", "Chrome Helper"], stderr=subprocess.DEVNULL)
    time.sleep(1)
    print(f"✅ 当前进程数: {get_chrome_count()}")

def auto_cleanup():
    """自动清理（如果进程过多）"""
    count = get_chrome_count()
    print(f"Chrome进程数: {count}")
    if count > MAX_TABS:
        cleanup_chrome()
        return True
    return False

if __name__ == "__main__":
    auto_cleanup()
