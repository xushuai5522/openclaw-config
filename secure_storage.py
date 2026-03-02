#!/usr/bin/env python3
"""
敏感信息加密模块
使用 Fernet (AES-128) 加密，保护账号密码等敏感信息
密钥基于设备唯一标识生成，无法在其他设备解密
"""
import os
import base64
import hashlib
import json
from cryptography.fernet import Fernet

# 全局加密器
_cipher = None

def get_device_key():
    """生成设备唯一的加密密钥"""
    import uuid
    import getpass
    
    # 获取设备唯一标识 (Mac地址)
    device_id = str(uuid.getnode())
    username = getpass.getuser()
    
    # 生成密钥
    combined = f"{device_id}-{username}-openclaw-secure-v1"
    key = hashlib.sha256(combined.encode()).digest()
    return base64.urlsafe_b64encode(key)

def get_cipher():
    """获取加密器（延迟初始化）"""
    global _cipher
    if _cipher is None:
        key = get_device_key()
        _cipher = Fernet(key)
    return _cipher

def encrypt(plaintext: str) -> str:
    """加密字符串"""
    cipher = get_cipher()
    encrypted = cipher.encrypt(plaintext.encode())
    return base64.b64encode(encrypted).decode()

def decrypt(encrypted: str) -> str:
    """解密字符串"""
    cipher = get_cipher()
    decoded = base64.b64decode(encrypted.encode())
    decrypted = cipher.decrypt(decoded)
    return decrypted.decode()

# 加密存储
class SecureStorage:
    """加密存储类"""
    
    def __init__(self, storage_file: str):
        self.storage_file = storage_file
        self.data = {}
        self.load()
    
    def load(self):
        """加载加密数据"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    self.data = json.load(f)
            except:
                self.data = {}
    
    def save(self):
        """保存加密数据"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def set(self, key: str, value: str):
        """加密存储值"""
        self.data[key] = encrypt(value)
        self.save()
    
    def get(self, key: str, default=None) -> str:
        """解密获取值"""
        if key in self.data:
            try:
                return decrypt(self.data[key])
            except:
                return default
        return default
    
    def delete(self, key: str):
        """删除值"""
        if key in self.data:
            del self.data[key]
            self.save()
    
    def list_keys(self) -> list:
        """列出所有键（不解密）"""
        return list(self.data.keys())

# 使用示例
if __name__ == "__main__":
    storage = SecureStorage(os.path.expanduser("~/.openclaw/credentials/secure.enc"))
    
    # 存储敏感信息
    storage.set("github_token", "ghp_xxxxx")
    storage.set("rrz_password", "152584")
    storage.set("api_key", "sk-xxx")
    
    # 读取时自动解密
    print("GitHub Token:", storage.get("github_token"))
    print("RRZ Password:", storage.get("rrz_password"))
    print("Keys:", storage.list_keys())
    
    print("\n✅ SecureStorage 测试成功!")
