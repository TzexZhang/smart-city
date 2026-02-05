# -*- coding: utf-8 -*-
"""AI Provider API"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.database import get_db
from app.core.deps import get_current_user
from app.core.security import encrypt_api_key
from app.models import AIProvider
from app.schemas import AIProviderCreate

router = APIRouter(prefix="/ai", tags=["AI管理"])


@router.get("/providers")
async def list_providers(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户配置的AI Providers"""
    result = await db.execute(
        select(AIProvider).where(AIProvider.user_id == current_user.id)
    )
    providers = result.scalars().all()

    # 隐藏API Key的完整内容
    return {
        "code": 200,
        "data": [
            {
                "id": p.id,
                "provider_code": p.provider_code,
                "provider_name": p.provider_name,
                "api_key_encrypted": p.api_key_encrypted[-4:] if p.api_key_encrypted else "",
                "is_enabled": p.is_enabled,
                "is_default": p.is_default,
                "priority": p.priority
            }
            for p in providers
        ]
    }


@router.post("/providers")
async def add_provider(
    provider_data: AIProviderCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加新的AI Provider"""
    # 检查是否已存在相同provider
    result = await db.execute(
        select(AIProvider).where(
            AIProvider.user_id == current_user.id,
            AIProvider.provider_code == provider_data.provider_code
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该Provider已存在"
        )

    # 加密API Key（如果提供）
    encrypted_key = encrypt_api_key(provider_data.api_key) if provider_data.api_key else None

    new_provider = AIProvider(
        user_id=current_user.id,
        provider_code=provider_data.provider_code,
        provider_name=provider_data.provider_name,
        api_key_encrypted=encrypted_key,
        base_url=provider_data.base_url,
        is_enabled=True
    )

    db.add(new_provider)
    await db.commit()
    await db.refresh(new_provider)

    return {
        "code": 200,
        "message": "添加成功",
        "data": {
            "id": new_provider.id,
            "provider_code": new_provider.provider_code,
            "provider_name": new_provider.provider_name
        }
    }


@router.put("/providers/{provider_id}/default")
async def set_default_provider(
    provider_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """设置默认Provider"""
    # 取消其他Provider的默认状态
    await db.execute(
        update(AIProvider)
        .where(AIProvider.user_id == current_user.id)
        .values(is_default=False)
    )

    # 设置新的默认Provider
    await db.execute(
        update(AIProvider)
        .where(
            AIProvider.id == provider_id,
            AIProvider.user_id == current_user.id
        )
        .values(is_default=True)
    )

    await db.commit()

    return {
        "code": 200,
        "message": "设置成功"
    }


@router.delete("/providers/{provider_id}")
async def delete_provider(
    provider_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除AI Provider"""
    result = await db.execute(
        delete(AIProvider)
        .where(
            AIProvider.id == provider_id,
            AIProvider.user_id == current_user.id
        )
    )
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider不存在"
        )

    return {
        "code": 200,
        "message": "删除成功"
    }


@router.get("/models")
async def list_models(
    provider_code: str = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """列出可用模型"""
    from app.services.ai_service import AIService

    ai_service = AIService(db)
    models = await ai_service.list_available_models(
        user_id=current_user.id,
        provider_code=provider_code
    )

    return {
        "code": 200,
        "data": models
    }


@router.get("/usage/stats")
async def get_usage_stats(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取使用统计"""
    from app.models import AIUsageStats

    result = await db.execute(
        select(AIUsageStats).where(AIUsageStats.user_id == current_user.id)
    )
    stats = result.scalars().all()

    summary = {
        "total_requests": sum(s.request_count for s in stats),
        "total_tokens": sum(s.total_tokens for s in stats),
        "by_provider": {}
    }

    for stat in stats:
        provider = stat.provider_code
        if provider not in summary["by_provider"]:
            summary["by_provider"][provider] = {
                "tokens": 0,
                "requests": 0
            }
        summary["by_provider"][provider]["tokens"] += stat.total_tokens
        summary["by_provider"][provider]["requests"] += stat.request_count

    return {
        "code": 200,
        "data": summary
    }
