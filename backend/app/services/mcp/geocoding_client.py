"""
地理编码MCP客户端
基于高德地图API提供位置解析服务
"""

from typing import Dict, Any, Optional
import logging
import httpx
from .base_client import MCPClientBase
from .config import MCPServerConfig

logger = logging.getLogger(__name__)


class AmapGeocodingClient(MCPClientBase):
    """高德地图地理编码客户端"""

    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.endpoint
        self.client = httpx.AsyncClient(timeout=10)

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用地理编码工具"""
        try:
            if tool_name == "geocode":
                return await self.geocode(parameters.get("address"))
            elif tool_name == "reverse_geocode":
                return await self.reverse_geocode(
                    parameters.get("longitude"),
                    parameters.get("latitude")
                )
            elif tool_name == "search_around":
                return await self.search_around(
                    parameters.get("longitude"),
                    parameters.get("latitude"),
                    parameters.get("keywords"),
                    parameters.get("radius", 1000)
                )
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"地理编码调用失败: {e}")
            return {"error": str(e)}

    async def list_tools(self) -> list:
        """列出可用的地理编码工具"""
        return [
            {
                "name": "geocode",
                "description": "地址转坐标（地理编码）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "地址描述"
                        }
                    },
                    "required": ["address"]
                }
            },
            {
                "name": "reverse_geocode",
                "description": "坐标转地址（逆地理编码）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "longitude": {"type": "number"},
                        "latitude": {"type": "number"}
                    },
                    "required": ["longitude", "latitude"]
                }
            },
            {
                "name": "search_around",
                "description": "周边搜索",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "longitude": {"type": "number"},
                        "latitude": {"type": "number"},
                        "keywords": {"type": "string"},
                        "radius": {"type": "number", "default": 1000}
                    },
                    "required": ["longitude", "latitude", "keywords"]
                }
            }
        ]

    async def geocode(self, address: str) -> Dict[str, Any]:
        """
        地理编码：将地址转换为经纬度坐标

        Args:
            address: 地址描述

        Returns:
            包含经纬度的结果
        """
        try:
            url = f"{self.base_url}/geocode/geo"
            params = {
                "key": self.api_key,
                "address": address
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "1" and data.get("geocodes"):
                geocode = data["geocodes"][0]
                location = geocode.get("location", "").split(",")
                return {
                    "status": "success",
                    "address": address,
                    "formatted_address": geocode.get("formatted_address"),
                    "longitude": float(location[0]) if len(location) > 0 else None,
                    "latitude": float(location[1]) if len(location) > 1 else None,
                    "level": geocode.get("level"),
                    "confidence": geocode.get("confidence")
                }
            else:
                return {
                    "status": "error",
                    "address": address,
                    "error": "无法解析该地址"
                }
        except Exception as e:
            logger.error(f"地理编码失败: {e}")
            return {
                "status": "error",
                "address": address,
                "error": str(e)
            }

    async def reverse_geocode(
        self,
        longitude: float,
        latitude: float
    ) -> Dict[str, Any]:
        """
        逆地理编码：将经纬度转换为地址

        Args:
            longitude: 经度
            latitude: 纬度

        Returns:
            包含地址信息的结果
        """
        try:
            url = f"{self.base_url}/geocode/regeo"
            params = {
                "key": self.api_key,
                "location": f"{longitude},{latitude}"
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "1" and data.get("regeocode"):
                regeocode = data["regeocode"]
                return {
                    "status": "success",
                    "longitude": longitude,
                    "latitude": latitude,
                    "formatted_address": regeocode.get("formatted_address"),
                    "addressComponent": regeocode.get("addressComponent", {}),
                    "pois": regeocode.get("pois", [])
                }
            else:
                return {
                    "status": "error",
                    "longitude": longitude,
                    "latitude": latitude,
                    "error": "无法解析该坐标"
                }
        except Exception as e:
            logger.error(f"逆地理编码失败: {e}")
            return {
                "status": "error",
                "longitude": longitude,
                "latitude": latitude,
                "error": str(e)
            }

    async def search_around(
        self,
        longitude: float,
        latitude: float,
        keywords: str,
        radius: int = 1000
    ) -> Dict[str, Any]:
        """
        周边搜索：查找指定位置周边的POI

        Args:
            longitude: 中心点经度
            latitude: 中心点纬度
            keywords: 搜索关键词
            radius: 搜索半径（米）

        Returns:
            周边POI列表
        """
        try:
            url = f"{self.base_url}/place/around"
            params = {
                "key": self.api_key,
                "location": f"{longitude},{latitude}",
                "keywords": keywords,
                "radius": radius,
                "output": "json"
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "1":
                pois = []
                for poi in data.get("pois", []):
                    location = poi.get("location", "").split(",")
                    pois.append({
                        "name": poi.get("name"),
                        "type": poi.get("type"),
                        "address": poi.get("address"),
                        "longitude": float(location[0]) if len(location) > 0 else None,
                        "latitude": float(location[1]) if len(location) > 1 else None,
                        "distance": poi.get("distance"),
                    })

                return {
                    "status": "success",
                    "center": {"longitude": longitude, "latitude": latitude},
                    "keywords": keywords,
                    "radius": radius,
                    "count": len(pois),
                    "pois": pois
                }
            else:
                return {
                    "status": "error",
                    "keywords": keywords,
                    "error": data.get("info", "搜索失败")
                }
        except Exception as e:
            logger.error(f"周边搜索失败: {e}")
            return {
                "status": "error",
                "keywords": keywords,
                "error": str(e)
            }

    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()
