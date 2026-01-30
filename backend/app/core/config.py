# -*- coding: utf-8 -*-
"""应用配置模块"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置 - 所有配置从.env文件读取"""

    # 应用基础配置
    APP_NAME: str = "智慧城市数字孪生系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置 - 必须在.env中配置
    DATABASE_URL: str

    # JWT配置 - 必须在.env中配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS配置 - 必须在.env中配置
    CORS_ORIGINS: list

    # Redis配置（可选）
    REDIS_URL: Optional[str] = None

    # API限流配置
    RATE_LIMIT_PER_MINUTE: int = 60

    # 加密配置 - 必须在.env中配置（32字节）
    ENCRYPTION_KEY: str

    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
