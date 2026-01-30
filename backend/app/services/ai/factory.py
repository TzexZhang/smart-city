# -*- coding: utf-8 -*-
"""AI服务工厂"""

from typing import Dict, Type
from app.services.ai.providers import BaseAIProvider, ZhipuAIProvider, QwenAIProvider, DeepSeekAIProvider


class AIProviderFactory:
    """AI Provider工厂"""

    _providers: Dict[str, Type[BaseAIProvider]] = {
        "zhipu": ZhipuAIProvider,
        "qwen": QwenAIProvider,
        "deepseek": DeepSeekAIProvider,
    }

    @classmethod
    def register_provider(cls, code: str, provider_class: Type[BaseAIProvider]):
        """注册新的Provider"""
        cls._providers[code] = provider_class

    @classmethod
    def create_provider(
        cls,
        provider_code: str,
        api_key: str,
        base_url: str = None,
        **kwargs
    ) -> BaseAIProvider:
        """创建Provider实例"""
        provider_class = cls._providers.get(provider_code)

        if not provider_class:
            raise ValueError(f"不支持的Provider: {provider_code}")

        return provider_class(
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )

    @classmethod
    def list_supported_providers(cls) -> list:
        """列出支持的Provider"""
        return list(cls._providers.keys())
