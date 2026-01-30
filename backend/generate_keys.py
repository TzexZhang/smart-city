#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成安全密钥的辅助脚本

运行此脚本可以生成：
1. SECRET_KEY (JWT密钥)
2. ENCRYPTION_KEY (加密密钥)

使用方法：
    python generate_keys.py
"""

import secrets
import string
import base64


def generate_secret_key():
    """生成JWT SECRET_KEY (URL-safe base64编码)"""
    return secrets.token_urlsafe(32)


def generate_encryption_key():
    """生成Fernet加密密钥 (32字节的base64编码)"""
    # Fernet需要32字节的密钥，然后进行base64编码
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()


def generate_database_password(length=16):
    """生成数据库密码"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def main():
    print("=" * 60)
    print("智慧城市数字孪生系统 - 安全密钥生成工具")
    print("=" * 60)
    print()

    # 生成JWT SECRET_KEY
    print("【1】生成 JWT SECRET_KEY")
    print("-" * 40)
    secret_key = generate_secret_key()
    print(f"SECRET_KEY={secret_key}")
    print()

    # 生成加密密钥
    print("【2】生成加密密钥 (ENCRYPTION_KEY)")
    print("-" * 40)
    encryption_key = generate_encryption_key()
    print(f"ENCRYPTION_KEY={encryption_key}")
    print()

    # 生成数据库密码（可选）
    print("【3】生成数据库密码 (可选)")
    print("-" * 40)
    db_password = generate_database_password()
    print(f"数据库密码建议: {db_password}")
    print()

    print("=" * 60)
    print("请将上述密钥复制到 .env 文件中")
    print("注意：请妥善保管这些密钥，不要泄露！")
    print("=" * 60)


if __name__ == "__main__":
    main()
