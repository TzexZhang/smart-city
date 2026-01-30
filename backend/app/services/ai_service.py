# -*- coding: utf-8 -*-
"""AI服务统一入口"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import date, datetime

from app.models import AIProvider, AIModel, AIUsageStats, User
from app.services.ai.factory import AIProviderFactory
from app.services.ai.providers import BaseAIProvider, Message, ChatCompletionResponse
from app.core.security import decrypt_api_key


class AIService:
    """AI服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_default_provider(self, user_id: str) -> BaseAIProvider:
        """获取用户的默认AI Provider"""
        # 查询用户配置的默认Provider
        result = await self.db.execute(
            select(AIProvider).where(
                AIProvider.user_id == user_id,
                AIProvider.is_enabled == True,
                AIProvider.is_default == True
            )
        )
        provider_config = result.scalar_one_or_none()

        if not provider_config:
            # 如果没有设置默认，返回第一个启用的
            result = await self.db.execute(
                select(AIProvider)
                .where(
                    AIProvider.user_id == user_id,
                    AIProvider.is_enabled == True
                )
                .order_by(AIProvider.priority.desc())
                .limit(1)
            )
            provider_config = result.scalar_one_or_none()

        if not provider_config:
            raise ValueError("未配置可用的AI Provider，请先在设置中添加")

        # 创建Provider实例
        return AIProviderFactory.create_provider(
            provider_code=provider_config.provider_code,
            api_key=decrypt_api_key(provider_config.api_key_encrypted),
            base_url=provider_config.base_url
        )

    async def chat_completion(
        self,
        user_id: str,
        messages: List[Message],
        model: str = None,
        temperature: float = 0.7,
        tools: List[dict] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        """聊天补全"""
        provider = await self.get_user_default_provider(user_id)

        # 如果未指定模型，使用默认模型
        if not model:
            model = "glm-4-flash"

        # 调用Provider
        response = await provider.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            tools=tools,
            **kwargs
        )

        # 记录使用统计
        await self._record_usage(
            user_id=user_id,
            provider_code=provider.provider_code,
            model_code=model,
            tokens_used=response.tokens_used
        )

        return response

    async def list_available_models(
        self,
        user_id: str,
        provider_code: str = None
    ) -> List[dict]:
        """列出可用模型"""
        # 获取用户启用的Providers
        result = await self.db.execute(
            select(AIProvider).where(
                AIProvider.user_id == user_id,
                AIProvider.is_enabled == True
            )
        )
        user_providers = result.scalars().all()

        if not user_providers:
            # 返回系统默认的免费模型
            return await self._get_free_models()

        models = []
        for provider_config in user_providers:
            if provider_code and provider_config.provider_code != provider_code:
                continue

            provider = AIProviderFactory.create_provider(
                provider_code=provider_config.provider_code,
                api_key=decrypt_api_key(provider_config.api_key_encrypted)
            )

            provider_models = await provider.list_models()
            models.extend([
                {
                    "code": m.code,
                    "name": m.name,
                    "description": m.description,
                    "context_length": m.context_length,
                    "is_free": m.is_free,
                    "input_price": float(m.input_price) if m.input_price else 0,
                    "output_price": float(m.output_price) if m.output_price else 0,
                    "supports_function_calling": m.supports_function_calling,
                    "supports_vision": m.supports_vision,
                    "max_tokens": m.max_tokens
                }
                for m in provider_models
            ])

        return models

    async def _record_usage(
        self,
        user_id: str,
        provider_code: str,
        model_code: str,
        tokens_used: dict
    ):
        """记录使用统计"""
        from sqlalchemy.dialects.mysql import insert

        stmt = insert(AIUsageStats).values(
            user_id=user_id,
            provider_code=provider_code,
            model_code=model_code,
            date=date.today(),
            request_count=1,
            input_tokens=tokens_used.get("input_tokens", 0),
            output_tokens=tokens_used.get("output_tokens", 0),
            total_tokens=tokens_used.get("total_tokens", 0),
            estimated_cost=0.0  # TODO: 根据价格计算
        )

        # MySQL的ON DUPLICATE KEY UPDATE语法
        stmt = stmt.prefix_with("IGNORE")
        await self.db.execute(stmt)

        # 更新统计数据
        result = await self.db.execute(
            select(AIUsageStats).where(
                AIUsageStats.user_id == user_id,
                AIUsageStats.provider_code == provider_code,
                AIUsageStats.model_code == model_code,
                AIUsageStats.date == date.today()
            )
        )
        stats = result.scalar_one_or_none()

        if stats:
            await self.db.execute(
                update(AIUsageStats)
                .where(AIUsageStats.id == stats.id)
                .values(
                    request_count=stats.request_count + 1,
                    input_tokens=stats.input_tokens + tokens_used.get("input_tokens", 0),
                    output_tokens=stats.output_tokens + tokens_used.get("output_tokens", 0),
                    total_tokens=stats.total_tokens + tokens_used.get("total_tokens", 0)
                )
            )

        await self.db.commit()

    async def _get_free_models(self) -> List[dict]:
        """获取免费模型列表"""
        return [
            {
                "code": "glm-4-flash",
                "name": "GLM-4 Flash",
                "description": "智谱AI免费模型，快速响应",
                "context_length": 128000,
                "is_free": True,
                "input_price": 0,
                "output_price": 0,
                "supports_function_calling": True,
                "supports_vision": False,
                "max_tokens": 8000
            }
        ]
