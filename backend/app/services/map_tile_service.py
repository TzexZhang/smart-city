"""
高德地图瓦片MCP客户端
提供街道地图瓦片数据，用于Cesium显示真实街道地图
"""

from typing import Dict, Any, Optional
import logging
import httpx
import os

logger = logging.getLogger(__name__)


class AmapTileClient:
    """高德地图瓦片客户端"""

    def __init__(self):
        self.api_key = os.getenv("AMAP_API_KEY")
        self.tile_url = os.getenv(
            "AMAP_TILE_URL",
            "https://webrd02.is.autonavi.com/appmaptile?style=7&x={x}&y={y}&z={z}&scale=1"
        )
        self.satellite_url = os.getenv(
            "AMAP_SATELLITE_URL",
            "https://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}&scale=1"
        )
        self.client = None

    async def get_client(self):
        """获取HTTP客户端"""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)
        return self.client

    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()
            self.client = None

    def get_tile_url(
        self,
        x: int,
        y: int,
        z: int,
        style: str = "street"
    ) -> str:
        """
        获取瓦片URL

        Args:
            x: 瓦片X坐标
            y: 瓦片Y坐标
            z: 缩放级别
            style: 地图样式 (street, satellite)

        Returns:
            瓦片URL
        """
        if style == "satellite":
            return self.satellite_url.format(x=x, y=y, z=z)
        else:
            return self.tile_url.format(x=x, y=y, z=z)

    def get_tile_provider_info(self) -> Dict[str, Any]:
        """
        获取瓦片提供者信息
        用于Cesium ImageryLayer

        Returns:
            瓦片提供者配置
        """
        return {
            "url": self.tile_url,
            "satellite_url": self.satellite_url,
            "credit": "高德地图",
            "minimumLevel": 3,
            "maximumLevel": 18,
            "projection": "EPSG:3857",
            "tilingScheme": "WebMercatorTilingScheme"
        }

    async def get_reverse_geocode(self, longitude: float, latitude: float) -> Dict[str, Any]:
        """
        逆地理编码 - 获取地址信息

        Args:
            longitude: 经度
            latitude: 纬度

        Returns:
            地址信息
        """
        if not self.api_key:
            return {
                "error": "未配置AMAP_API_KEY",
                "address": f"位置: {latitude}, {longitude}"
            }

        try:
            client = await self.get_client()

            url = "https://restapi.amap.com/v3/geocode/regeo"
            params = {
                "key": self.api_key,
                "location": f"{longitude},{latitude}",
                "extensions": "base"
            }

            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "1" and data.get("regeocode"):
                regeocode = data["regeocode"]
                return {
                    "status": "success",
                    "formatted_address": regeocode.get("formatted_address"),
                    "province": regeocode.get("addressComponent", {}).get("province"),
                    "city": regeocode.get("addressComponent", {}).get("city"),
                    "district": regeocode.get("addressComponent", {}).get("district"),
                    "street": regeocode.get("addressComponent", {}).get("street"),
                    "adcode": regeocode.get("adcode"),
                }
            else:
                return {
                    "error": data.get("info", "逆地理编码失败"),
                    "address": f"位置: {latitude}, {longitude}"
                }

        except Exception as e:
            logger.error(f"逆地理编码失败: {e}")
            return {
                "error": str(e),
                "address": f"位置: {latitude}, {longitude}"
            }

    async def search_nearby(
        self,
        longitude: float,
        latitude: float,
        keywords: str,
        radius: int = 1000
    ) -> Dict[str, Any]:
        """
        周边搜索 - 获取附近的POI

        Args:
            longitude: 经度
            latitude: 纬度
            keywords: 关键词
            radius: 搜索半径（米）

        Returns:
            POI列表
        """
        if not self.api_key:
            return {
                "error": "未配置AMAP_API_KEY",
                "pois": []
            }

        try:
            client = await self.get_client()

            url = "https://restapi.amap.com/v3/place/around"
            params = {
                "key": self.api_key,
                "location": f"{longitude},{latitude}",
                "keywords": keywords,
                "radius": str(radius),
                "output": "json"
            }

            response = await client.get(url, params=params)
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
                    "total": len(pois),
                    "pois": pois
                }
            else:
                return {
                    "error": data.get("info", "搜索失败"),
                    "pois": []
                }

        except Exception as e:
            logger.error(f"周边搜索失败: {e}")
            return {
                "error": str(e),
                "pois": []
            }


# 单例实例
amap_tile_client = AmapTileClient()


async def get_amap_tile_client() -> AmapTileClient:
    """获取高德地图瓦片客户端"""
    return amap_tile_client
