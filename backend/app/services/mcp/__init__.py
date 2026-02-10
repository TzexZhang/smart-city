"""
MCP服务层
提供统一的MCP客户端管理和调用接口
"""

from typing import Dict, List, Optional, Any
import logging
from .config import MCPConfig, MCPServerConfig
from .base_client import MCPClientBase, HTTPMCPClient, BuiltinMCPClient
from .geocoding_client import AmapGeocodingClient
from .search_client import DataEnhancementClient
from .weather_client import OpenWeatherMapClient

logger = logging.getLogger(__name__)


class MCPManager:
    """MCP管理器，统一管理所有MCP客户端"""

    def __init__(self):
        self.clients: Dict[str, MCPClientBase] = {}
        self._initialize_builtin_clients()

    def _initialize_builtin_clients(self):
        """初始化内置MCP客户端"""
        for config in MCPConfig.list_servers():
            if config.endpoint.startswith("builtin://"):
                self.clients[config.name] = BuiltinMCPClient(config)

    def get_client(self, name: str) -> Optional[MCPClientBase]:
        """获取指定MCP客户端"""
        return self.clients.get(name)

    def add_client(self, name: str, client: MCPClientBase) -> None:
        """添加MCP客户端"""
        self.clients[name] = client

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用指定MCP服务器的工具

        Args:
            server_name: MCP服务器名称
            tool_name: 工具名称
            parameters: 工具参数

        Returns:
            工具执行结果
        """
        client = self.get_client(server_name)
        if not client:
            return {"error": f"MCP服务器未找到: {server_name}"}

        return await client.call_tool(tool_name, parameters)

    async def list_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        列出所有MCP服务器的工具

        Returns:
            按服务器分组的工具列表
        """
        all_tools = {}
        for name, client in self.clients.items():
            try:
                tools = await client.list_tools()
                all_tools[name] = tools
            except Exception as e:
                logger.warning(f"获取 {name} 的工具列表失败: {e}")
                all_tools[name] = []

        return all_tools

    async def health_check_all(self) -> Dict[str, bool]:
        """
        检查所有MCP服务器的健康状态

        Returns:
            每个服务器的健康状态
        """
        health_status = {}
        for name, client in self.clients.items():
            try:
                health_status[name] = await client.health_check()
            except Exception as e:
                logger.warning(f"检查 {name} 健康状态失败: {e}")
                health_status[name] = False

        return health_status

    async def close_all(self):
        """关闭所有客户端连接"""
        for client in self.clients.values():
            if hasattr(client, 'close'):
                await client.close()


# 全局MCP管理器实例
mcp_manager = MCPManager()


async def get_mcp_manager() -> MCPManager:
    """获取MCP管理器实例"""
    return mcp_manager


__all__ = [
    'MCPManager',
    'get_mcp_manager',
    'MCPConfig',
    'MCPServerConfig',
    'MCPClientBase',
    'HTTPMCPClient',
    'BuiltinMCPClient',
    'AmapGeocodingClient',
    'DataEnhancementClient',
    'OpenWeatherMapClient',
]
