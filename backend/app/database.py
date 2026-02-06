# -*- coding: utf-8 -*-
"""数据库配置和会话管理"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from app.core.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL.replace("mysql+pymysql://", "mysql+aiomysql://"),
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 创建会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 创建同步引擎（用于脚本和迁移）
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 创建同步会话工厂
SessionLocal = sessionmaker(
    sync_engine,
    autocommit=False,
    autoflush=False
)

# Base类用于模型继承
Base = declarative_base()


# 依赖注入：获取数据库会话
async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
