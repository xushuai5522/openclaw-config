#!/usr/bin/env python3
"""
API调用稳定性增强模块
- 增加超时时间
- 指数退避重试机制
- 备用方案
"""
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    """创建带重试机制的session"""
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=3,  # 最多重试3次
        backoff_factor=2,  # 指数退避：2秒, 4秒, 8秒
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def call_api_with_retry(url, headers=None, json=None, timeout=180, max_retries=5):
    """带重试的API调用"""
    session = create_session()
    
    for attempt in range(max_retries):
        try:
            if json:
                response = session.post(url, headers=headers, json=json, timeout=timeout)
            else:
                response = session.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # 限流，等待更长时间
                wait_time = (attempt + 1) * 10
                print(f"限流中，等待 {wait_time}秒...")
                time.sleep(wait_time)
            else:
                print(f"错误 {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            print(f"超时 (尝试 {attempt+1}/{max_retries})")
        except requests.exceptions.ConnectionError as e:
            print(f"连接错误: {e}")
        
        # 指数退避等待
        wait_time = (2 ** attempt)
        print(f"重试前等待 {wait_time}秒...")
        time.sleep(wait_time)
    
    return None

# 测试
if __name__ == "__main__":
    api_key = "675362ca-6313-43e5-a705-3046f668e2b1"
    
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "doubao-seed-1-6-vision-250815",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 10
    }
    
    result = call_api_with_retry(url, headers=headers, json=json_data)
    print("结果:", result)
