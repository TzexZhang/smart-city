# -*- coding: utf-8 -*-
"""AI服务 - 抽象基类和具体实现"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass
from openai import AsyncOpenAI


@dataclass
class Message:
    """消息数据类"""
    role: str
    content: str


@dataclass
class ChatCompletionResponse:
    """聊天响应数据类"""
    content: str
    model: str
    tokens_used: Dict[str, int]
    finish_reason: str
    tool_calls: List[Dict[str, Any]] = None


@dataclass
class ModelInfo:
    """模型信息"""
    code: str
    name: str
    description: str
    context_length: int
    is_free: bool
    input_price: float
    output_price: float
    supports_function_calling: bool
    supports_vision: bool
    max_tokens: int


class BaseAIProvider(ABC):
    """AI Provider抽象基类"""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        **kwargs
    ):
        self.api_key = api_key
        self.base_url = base_url or self.default_base_url
        self.client = self._init_client()

    @property
    @abstractmethod
    def provider_code(self) -> str:
        """提供商代码"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供商名称"""
        pass

    @property
    @abstractmethod
    def default_base_url(self) -> str:
        """默认API地址"""
        pass

    @abstractmethod
    def _init_client(self):
        """初始化客户端"""
        pass

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: List[Dict[str, Any]] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        """聊天补全"""
        pass

    async def stream_chat_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式聊天补全"""
        # 默认不支持流式
        raise NotImplementedError("Streaming not supported")

    async def list_models(self) -> List[ModelInfo]:
        """列出可用模型"""
        raise NotImplementedError("Model listing not supported")


class ZhipuAIProvider(BaseAIProvider):
    """智谱AI Provider"""

    @property
    def provider_code(self) -> str:
        return "zhipu"

    @property
    def provider_name(self) -> str:
        return "智谱AI"

    @property
    def default_base_url(self) -> str:
        return "https://open.bigmodel.cn/api/paas/v4"

    def _init_client(self):
        return AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def chat_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: List[Dict[str, Any]] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        # 转换消息格式
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # 调用API
        response = await self.client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            **kwargs
        )

        # 解析响应
        choice = response.choices[0]
        tool_calls = []
        if choice.message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in choice.message.tool_calls
            ]

        return ChatCompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_used={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=choice.finish_reason,
            tool_calls=tool_calls if tool_calls else None
        )

    async def stream_chat_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """流式聊天"""
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        stream = await self.client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def list_models(self) -> List[ModelInfo]:
        """列出智谱AI可用模型"""
        return [
            ModelInfo(
                code="glm-4-flash",
                name="GLM-4 Flash",
                description="智谱AI免费模型，快速响应",
                context_length=128000,
                is_free=True,
                input_price=0,
                output_price=0,
                supports_function_calling=True,
                supports_vision=False,
                max_tokens=8000
            ),
            ModelInfo(
                code="glm-4-plus",
                name="GLM-4 Plus",
                description="智谱AI增强模型，深度推理",
                context_length=128000,
                is_free=False,
                input_price=0.01,
                output_price=0.01,
                supports_function_calling=True,
                supports_vision=True,
                max_tokens=8000
            ),
            ModelInfo(
                code="glm-4-air",
                name="GLM-4 Air",
                description="智谱AI轻量模型",
                context_length=128000,
                is_free=False,
                input_price=0.001,
                output_price=0.001,
                supports_function_calling=True,
                supports_vision=False,
                max_tokens=8000
            )
        ]


class QwenAIProvider(BaseAIProvider):
    """通义千问 Provider"""

    @property
    def provider_code(self) -> str:
        return "qwen"

    @property
    def provider_name(self) -> str:
        return "通义千问"

    @property
    def default_base_url(self) -> str:
        return "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def _init_client(self):
        return AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def chat_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: List[Dict[str, Any]] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await self.client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            **kwargs
        )

        choice = response.choices[0]
        return ChatCompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_used={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=choice.finish_reason
        )

    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                code="qwen-turbo",
                name="Qwen Turbo",
                description="通义千问超高速模型",
                context_length=8000,
                is_free=True,
                input_price=0,
                output_price=0,
                supports_function_calling=True,
                supports_vision=False,
                max_tokens=2000
            ),
            ModelInfo(
                code="qwen-plus",
                name="Qwen Plus",
                description="通义千问增强版",
                context_length=32000,
                is_free=False,
                input_price=0.008,
                output_price=0.008,
                supports_function_calling=True,
                supports_vision=False,
                max_tokens=6000
            )
        ]


class DeepSeekAIProvider(BaseAIProvider):
    """DeepSeek Provider"""

    @property
    def provider_code(self) -> str:
        return "deepseek"

    @property
    def provider_name(self) -> str:
        return "DeepSeek"

    @property
    def default_base_url(self) -> str:
        return "https://api.deepseek.com/v1"

    def _init_client(self):
        return AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def chat_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: List[Dict[str, Any]] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await self.client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            **kwargs
        )

        choice = response.choices[0]
        return ChatCompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_used={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=choice.finish_reason
        )

    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                code="deepseek-chat",
                name="DeepSeek Chat",
                description="DeepSeek对话模型",
                context_length=16000,
                is_free=True,
                input_price=0.0001,
                output_price=0.0002,
                supports_function_calling=True,
                supports_vision=False,
                max_tokens=4000
            ),
            ModelInfo(
                code="deepseek-coder",
                name="DeepSeek Coder",
                description="DeepSeek代码模型",
                context_length=16000,
                is_free=True,
                input_price=0.0001,
                output_price=0.0002,
                supports_function_calling=True,
                supports_vision=False,
                max_tokens=4000
            )
        ]


class OpenAIProvider(BaseAIProvider):
    """OpenAI Provider"""

    @property
    def provider_code(self) -> str:
        return "openai"

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    @property
    def default_base_url(self) -> str:
        return "https://api.openai.com/v1"

    def _init_client(self):
        return AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def chat_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: List[Dict[str, Any]] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await self.client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            **kwargs
        )

        choice = response.choices[0]
        return ChatCompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_used={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=choice.finish_reason
        )

    async def stream_chat_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """流式聊天"""
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        stream = await self.client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                code="gpt-4o",
                name="GPT-4o",
                description="OpenAI最新多模态模型",
                context_length=128000,
                is_free=False,
                input_price=0.005,
                output_price=0.015,
                supports_function_calling=True,
                supports_vision=True,
                max_tokens=4096
            ),
            ModelInfo(
                code="gpt-4o-mini",
                name="GPT-4o Mini",
                description="OpenAI轻量级模型",
                context_length=128000,
                is_free=False,
                input_price=0.00015,
                output_price=0.0006,
                supports_function_calling=True,
                supports_vision=True,
                max_tokens=16384
            ),
            ModelInfo(
                code="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                description="OpenAI经典模型",
                context_length=16000,
                is_free=False,
                input_price=0.0005,
                output_price=0.0015,
                supports_function_calling=True,
                supports_vision=False,
                max_tokens=4096
            )
        ]


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude Provider"""

    @property
    def provider_code(self) -> str:
        return "anthropic"

    @property
    def provider_name(self) -> str:
        return "Anthropic"

    @property
    def default_base_url(self) -> str:
        return "https://api.anthropic.com/v1"

    def _init_client(self):
        # Anthropic使用不同的SDK，这里使用OpenAI兼容的base_url
        # 实际使用时需要anthropic SDK或自定义HTTP客户端
        return AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.anthropic.com/v1"  # 代理地址
        )

    async def chat_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: List[Dict[str, Any]] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await self.client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            **kwargs
        )

        choice = response.choices[0]
        return ChatCompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_used={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=choice.finish_reason
        )

    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                code="claude-3-5-sonnet-20241022",
                name="Claude 3.5 Sonnet",
                description="Anthropic最强模型",
                context_length=200000,
                is_free=False,
                input_price=0.003,
                output_price=0.015,
                supports_function_calling=True,
                supports_vision=True,
                max_tokens=8192
            ),
            ModelInfo(
                code="claude-3-haiku-20240307",
                name="Claude 3 Haiku",
                description="Anthropic快速模型",
                context_length=200000,
                is_free=False,
                input_price=0.00025,
                output_price=0.00125,
                supports_function_calling=True,
                supports_vision=True,
                max_tokens=4096
            )
        ]


class ErnieProvider(BaseAIProvider):
    """百度文心一言 Provider"""

    @property
    def provider_code(self) -> str:
        return "ernie"

    @property
    def provider_name(self) -> str:
        return "文心一言"

    @property
    def default_base_url(self) -> str:
        return "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat"

    def _init_client(self):
        return AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def chat_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: List[Dict[str, Any]] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await self.client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            **kwargs
        )

        choice = response.choices[0]
        return ChatCompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_used={
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            },
            finish_reason=choice.finish_reason
        )

    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                code="ernie-4.0-8k",
                name="ERNIE 4.0",
                description="百度文心大模型4.0",
                context_length=8000,
                is_free=False,
                input_price=0.012,
                output_price=0.012,
                supports_function_calling=True,
                supports_vision=False,
                max_tokens=2048
            ),
            ModelInfo(
                code="ernie-3.5-8k",
                name="ERNIE 3.5",
                description="百度文心大模型3.5",
                context_length=8000,
                is_free=False,
                input_price=0.008,
                output_price=0.008,
                supports_function_calling=True,
                supports_vision=False,
                max_tokens=2048
            ),
            ModelInfo(
                code="ernie-speed-8k",
                name="ERNIE Speed",
                description="百度文心快速模型",
                context_length=8000,
                is_free=True,
                input_price=0,
                output_price=0,
                supports_function_calling=False,
                supports_vision=False,
                max_tokens=2048
            )
        ]


class XingHuoProvider(BaseAIProvider):
    """讯飞星火 Provider"""

    @property
    def provider_code(self) -> str:
        return "xinghuo"

    @property
    def provider_name(self) -> str:
        return "讯飞星火"

    @property
    def default_base_url(self) -> str:
        return "https://spark-api.xf-yun.com/v1"

    def _init_client(self):
        return AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def chat_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: List[Dict[str, Any]] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await self.client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            **kwargs
        )

        choice = response.choices[0]
        return ChatCompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_used={
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            },
            finish_reason=choice.finish_reason
        )

    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                code="spark-4.0",
                name="讯飞星火 4.0",
                description="讯飞星火认知大模型V4.0",
                context_length=128000,
                is_free=False,
                input_price=0.018,
                output_price=0.018,
                supports_function_calling=True,
                supports_vision=False,
                max_tokens=4096
            ),
            ModelInfo(
                code="spark-3.5",
                name="讯飞星火 3.5",
                description="讯飞星火认知大模型V3.5",
                context_length=28000,
                is_free=False,
                input_price=0.009,
                output_price=0.009,
                supports_function_calling=True,
                supports_vision=False,
                max_tokens=4096
            ),
            ModelInfo(
                code="spark-lite",
                name="讯飞星火 Lite",
                description="讯飞星火轻量版",
                context_length=8000,
                is_free=True,
                input_price=0,
                output_price=0,
                supports_function_calling=False,
                supports_vision=False,
                max_tokens=2048
            )
        ]
