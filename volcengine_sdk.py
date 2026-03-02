#!/usr/bin/env python3
"""
火山引擎 SeedEdit 图生图 - 使用 SDK
"""
from volcengine.base.Service import Service

class ArkService(Service):
    def __init__(self, service_info, api_info):
        super().__init__(service_info, api_info)
        # 设置aksk (这里用API Key试试看能不能行)
        self.set_aksk("675362ca-6313-43e5-a705-3046f668e2b1", "")

service_info = {
    'service': 'ark',
    'version': '2024-06-01',
    'host': 'ark.cn-beijing.volcengineapi.com',
    'header': {},
    'connection_timeout': 30,
    'socket_timeout': 30,
}

api_info = {
    'GenerateImage': {
        'method': 'POST',
        'url': '/v1/images/generations',
    },
    'ListModels': {
        'method': 'GET', 
        'url': '/v1/models',
    }
}

ark = ArkService(service_info, api_info)

# 尝试列出模型
try:
    print("=== 尝试列出模型 ===")
    resp = ark.get('ListModels', {})
    print(resp)
except Exception as e:
    print(f"失败: {e}")

# 尝试图生图
try:
    print("\n=== 尝试图生图 ===")
    body = {
        "model": "doubao-seededit-3-0-i2i",
        "prompt": "生成一张苹果iPad图片",
        "return_url": True,
    }
    resp = ark.post('GenerateImage', {}, body)
    print(resp)
except Exception as e:
    print(f"失败: {e}")
