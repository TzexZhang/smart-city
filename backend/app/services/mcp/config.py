"""
MCP配置管理
管理MCP服务器的配置和连接信息
"""

from typing import Dict, List, Optional
from pydantic import BaseModel
import os


class MCPServerConfig(BaseModel):
    """MCP服务器配置"""
    name: str
    endpoint: str
    enabled: bool = True
    timeout: int = 30
    api_key: Optional[str] = None
    description: str = ""


class MCPConfig:
    """MCP配置管理器"""

    # 内置MCP服务配置
    BUILTIN_SERVERS = {
        "fetch": MCPServerConfig(
            name="@modelcontextprotocol/server-fetch",
            endpoint="builtin://fetch",
            enabled=True,
            timeout=30,
            description="网页内容抓取服务"
        ),
        "memory": MCPServerConfig(
            name="@modelcontextprotocol/server-memory",
            endpoint="builtin://memory",
            enabled=True,
            timeout=10,
            description="对话历史记忆服务"
        ),
    }

    # 自定义MCP服务配置
    CUSTOM_SERVERS: Dict[str, MCPServerConfig] = {}

    @classmethod
    def get_server(cls, name: str) -> Optional[MCPServerConfig]:
        """获取指定服务器配置"""
        if name in cls.BUILTIN_SERVERS:
            return cls.BUILTIN_SERVERS[name]
        if name in cls.CUSTOM_SERVERS:
            return cls.CUSTOM_SERVERS[name]
        return None

    @classmethod
    def list_servers(cls) -> List[MCPServerConfig]:
        """列出所有可用的MCP服务器"""
        servers = []
        for server in cls.BUILTIN_SERVERS.values():
            if server.enabled:
                servers.append(server)
        for server in cls.CUSTOM_SERVERS.values():
            if server.enabled:
                servers.append(server)
        return servers

    @classmethod
    def add_custom_server(cls, config: MCPServerConfig) -> None:
        """添加自定义MCP服务器"""
        cls.CUSTOM_SERVERS[config.name] = config

    @classmethod
    def remove_server(cls, name: str) -> bool:
        """移除MCP服务器"""
        if name in cls.CUSTOM_SERVERS:
            del cls.CUSTOM_SERVERS[name]
            return True
        return False

    @classmethod
    def from_env(cls) -> None:
        """从环境变量加载配置"""
        # 高德地图API配置（用于地理编码MCP）
        amap_api_key = os.getenv("AMAP_API_KEY")
        if amap_api_key:
            cls.add_custom_server(MCPServerConfig(
                name="amap-geocoding",
                endpoint=os.getenv("AMAP_ENDPOINT", "https://restapi.amap.com/v3"),
                enabled=True,
                timeout=10,
                api_key=amap_api_key,
                description="高德地图地理编码服务"
            ))

        # OpenWeatherMap API配置（用于天气MCP）
        weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        if weather_api_key:
            cls.add_custom_server(MCPServerConfig(
                name="openweathermap",
                endpoint=os.getenv("OPENWEATHER_ENDPOINT", "https://api.openweathermap.org/data/2.5"),
                enabled=True,
                timeout=10,
                api_key=weather_api_key,
                description="OpenWeatherMap天气服务"
            ))


# 初始化时从环境变量加载
MCPConfig.from_env()
