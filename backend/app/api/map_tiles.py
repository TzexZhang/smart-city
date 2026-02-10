"""
地图瓦片API
提供高德地图街道地图瓦片服务
"""
from fastapi import APIRouter, Query
from typing import Optional
import logging

from app.services.map_tile_service import get_amap_tile_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/map", tags=["地图瓦片"])


@router.get("/tile-config")
async def get_tile_config():
    """
    获取地图瓦片配置
    返回Cesium ImageryLayer所需的配置信息
    """
    try:
        client = await get_amap_tile_client()
        provider_info = client.get_tile_provider_info()

        return {
            "status": "success",
            "provider": "amap",
            "street_url": provider_info["url"],
            "satellite_url": provider_info["satellite_url"],
            "credit": provider_info["credit"],
            "minimumLevel": provider_info["minimumLevel"],
            "maximumLevel": provider_info["maximumLevel"],
            "description": "高德地图街道地图瓦片服务"
        }
    except Exception as e:
        logger.error(f"获取瓦片配置失败: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/reverse-geocode")
async def reverse_geocode(
    longitude: float = Query(..., description="经度"),
    latitude: float = Query(..., description="纬度")
):
    """
    逆地理编码 - 获取坐标对应的地址信息
    """
    try:
        client = await get_amap_tile_client()
        result = await client.get_reverse_geocode(longitude, latitude)

        return result
    except Exception as e:
        logger.error(f"逆地理编码失败: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/search-nearby")
async def search_nearby(
    longitude: float = Query(..., description="经度"),
    latitude: float = Query(..., description="纬度"),
    keywords: str = Query(..., description="搜索关键词"),
    radius: int = Query(1000, description="搜索半径（米）")
):
    """
    周边POI搜索
    """
    try:
        client = await get_amap_tile_client()
        result = await client.search_nearby(longitude, latitude, keywords, radius)

        return result
    except Exception as e:
        logger.error(f"周边搜索失败: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
