"""
天气API
提供实时天气数据获取接口
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
import logging

from app.database import get_db
from app.services.weather_service import get_weather_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/weather", tags=["天气服务"])


@router.get("/current")
async def get_current_weather(
    city: Optional[str] = Query(None, description="城市名称（如：Beijing, Shanghai）"),
    latitude: Optional[float] = Query(None, description="纬度"),
    longitude: Optional[float] = Query(None, description="经度"),
    db=Depends(get_db)
):
    """
    获取当前天气数据

    参数:
        city: 城市名称（与coordinates二选一）
        latitude: 纬度（与city二选一）
        longitude: 经度（与city二选一）

    返回:
        天气数据，包括温度、天气状况、湿度、风速等
    """
    logger.info(f"🌡️ 请求天气数据: city={city}, lat={latitude}, lon={longitude}")

    try:
        # 获取天气服务
        weather_service = await get_weather_service()

        # 调用天气服务
        result = await weather_service.get_current_weather(
            city=city,
            latitude=latitude,
            longitude=longitude
        )

        if result.get("error"):
            logger.error(f"❌ 获取天气失败: {result['error']}")
            raise HTTPException(status_code=500, detail=result['error'])

        logger.info(f"✅ 获取天气成功: {result.get('city')}, {result.get('condition')}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 天气API异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast")
async def get_weather_forecast(
    city: Optional[str] = Query(None, description="城市名称"),
    latitude: Optional[float] = Query(None, description="纬度"),
    longitude: Optional[float] = Query(None, description="经度"),
    days: int = Query(1, ge=1, le=5, description="预报天数"),
    db=Depends(get_db)
):
    """
    获取天气预报数据

    参数:
        city: 城市名称（与coordinates二选一）
        latitude: 纬度
        longitude: 经度
        days: 预报天数（1-5天）

    返回:
        天气预报数据
    """
    logger.info(f"🌡️ 请求天气预报: city={city}, days={days}")

    try:
        weather_service = await get_weather_service()

        result = await weather_service.get_weather_forecast(
            city=city,
            latitude=latitude,
            longitude=longitude,
            days=days
        )

        return result

    except Exception as e:
        logger.error(f"❌ 获取天气预报失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
