"""
MCP客户端基类
定义MCP客户端的通用接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging
import httpx
from .config import MCPServerConfig

logger = logging.getLogger(__name__)


class MCPClientBase(ABC):
    """MCP客户端基类"""

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.timeout = config.timeout
        self.client = None

    @abstractmethod
    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用MCP工具

        Args:
            tool_name: 工具名称
            parameters: 工具参数

        Returns:
            工具执行结果
        """
        pass

    @abstractmethod
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        列出可用的工具

        Returns:
            工具列表
        """
        pass

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            服务是否可用
        """
        try:
            await self.list_tools()
            return True
        except Exception as e:
            logger.warning(f"MCP服务 {self.config.name} 健康检查失败: {e}")
            return False


class HTTPMCPClient(MCPClientBase):
    """基于HTTP的MCP客户端"""

    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self._build_headers()
        )

    def _build_headers(self) -> Dict[str, str]:
        """构建HTTP请求头"""
        headers = {
            "Content-Type": "application/json",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """通过HTTP调用MCP工具"""
        try:
            url = f"{self.config.endpoint}/tools/{tool_name}"
            response = await self.client.post(url, json=parameters)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP调用失败: {e}")
            return {"error": str(e)}

    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出HTTP MCP服务提供的工具"""
        try:
            url = f"{self.config.endpoint}/tools"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("tools", [])
        except httpx.HTTPError as e:
            logger.error(f"获取工具列表失败: {e}")
            return []

    async def close(self):
        """关闭客户端连接"""
        if self.client:
            await self.client.aclose()


class BuiltinMCPClient(MCPClientBase):
    """内置MCP客户端（模拟实现）"""

    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self._tools = self._initialize_tools()

    def _initialize_tools(self) -> Dict[str, Any]:
        """初始化内置工具"""
        if self.config.name == "@modelcontextprotocol/server-fetch":
            return {
                "fetch_webpage": {
                    "name": "fetch_webpage",
                    "description": "获取网页内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "网页URL"
                            }
                        },
                        "required": ["url"]
                    }
                }
            }
        elif self.config.name == "@modelcontextprotocol/server-memory":
            return {
                "store_memory": {
                    "name": "store_memory",
                    "description": "存储记忆",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string"},
                            "value": {"type": "string"}
                        },
                        "required": ["key", "value"]
                    }
                },
                "retrieve_memory": {
                    "name": "retrieve_memory",
                    "description": "检索记忆",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string"}
                        },
                        "required": ["key"]
                    }
                }
            }
        return {}

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用内置MCP工具"""
        try:
            if tool_name == "fetch_webpage":
                return await self._fetch_webpage(parameters.get("url"))
            elif tool_name == "store_memory":
                return await self._store_memory(parameters.get("key"), parameters.get("value"))
            elif tool_name == "retrieve_memory":
                return await self._retrieve_memory(parameters.get("key"))
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"调用内置工具失败: {e}")
            return {"error": str(e)}

    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出内置工具"""
        return list(self._tools.values())

    async def _fetch_webpage(self, url: str) -> Dict[str, Any]:
        """获取网页内容（简化实现）"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                return {
                    "url": url,
                    "content": response.text[:10000],  # 限制长度
                    "status": "success"
                }
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "status": "error"
            }

    async def _store_memory(self, key: str, value: str) -> Dict[str, Any]:
        """存储记忆（简化实现，使用内存字典）"""
        if not hasattr(self, '_memory'):
            self._memory = {}
        self._memory[key] = value
        return {"status": "stored", "key": key}

    async def _retrieve_memory(self, key: str) -> Dict[str, Any]:
        """检索记忆"""
        if not hasattr(self, '_memory'):
            self._memory = {}
        value = self._memory.get(key)
        return {
            "key": key,
            "value": value,
            "found": value is not None
        }
