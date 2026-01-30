# -*- coding: utf-8 -*-
"""用户管理API"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import get_db
from app.core.deps import get_current_user
from app.models import User, UserConfig
from app.schemas import UserConfigResponse

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/me/config", response_model=dict)
async def get_user_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户配置"""
    result = await db.execute(
        select(UserConfig).where(UserConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    if not config:
        # 创建默认配置
        config = UserConfig(user_id=current_user.id)
        db.add(config)
        await db.commit()
        await db.refresh(config)

    return {
        "code": 200,
        "data": {
            "provider": config.provider,
            "model_name": config.model_name,
            "persona": config.persona,
            "temperature": float(config.temperature) if config.temperature else 0.7,
            "top_p": float(config.top_p) if config.top_p else 0.9,
            "auto_execute": config.auto_execute,
            "default_city": config.default_city
        }
    }


@router.put("/me/config")
async def update_user_config(
    config_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户配置"""
    result = await db.execute(
        select(UserConfig).where(UserConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    if not config:
        config = UserConfig(user_id=current_user.id)
        db.add(config)

    # 更新配置
    if "provider" in config_data:
        config.provider = config_data["provider"]
    if "model_name" in config_data:
        config.model_name = config_data["model_name"]
    if "persona" in config_data:
        config.persona = config_data["persona"]
    if "temperature" in config_data:
        config.temperature = config_data["temperature"]
    if "top_p" in config_data:
        config.top_p = config_data["top_p"]
    if "auto_execute" in config_data:
        config.auto_execute = config_data["auto_execute"]
    if "default_city" in config_data:
        config.default_city = config_data["default_city"]

    await db.commit()

    return {
        "code": 200,
        "message": "配置更新成功"
    }
