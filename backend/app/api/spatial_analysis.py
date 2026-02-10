"""
空间分析 API
包括：缓冲区分析、视域分析、可达性分析
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal
import math
from shapely.geometry import Point, shape
from shapely.ops import unary_union
import logging

from app.database import get_db
from app.models import Building

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/spatial", tags=["空间分析"])


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    计算两点间的球面距离（Haversine公式）

    Args:
        lat1, lon1: 点1的纬度、经度
        lat2, lon2: 点2的纬度、经度

    Returns:
        距离（米）
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    R = 6371000  # 地球半径（米）
    return R * c


@router.get("/buffer")
async def buffer_analysis(
    center_lon: float = Query(..., description="圆心经度"),
    center_lat: float = Query(..., description="圆心纬度"),
    radius: float = Query(..., gt=0, description="半径(米)"),
    min_height: Optional[float] = Query(None, description="最小高度过滤"),
    category: Optional[str] = Query(None, description="建筑类型过滤"),
    risk_level: Optional[int] = Query(None, ge=0, le=4, description="最小风险等级"),
    db: Session = Depends(get_db)
):
    """
    缓冲区分析

    分析指定半径范围内的建筑，并返回统计信息

    参数:
        center_lon: 圆心经度
        center_lat: 圆心纬度
        radius: 半径（米）
        min_height: 可选，最小高度过滤
        category: 可选，建筑类型过滤
        risk_level: 可选，最小风险等级

    返回:
        - total: 总建筑数量
        - data: 建筑列表
        - statistics: 统计信息（按类型、高度、风险等级）
    """
    logger.info(f"🔵 缓冲区分析请求: center=({center_lon}, {center_lat}), radius={radius}m")

    try:
        # 创建中心点
        center_point = Point(center_lon, center_lat)

        # 获取所有建筑
        buildings = db.query(Building).all()

        # 筛选范围内的建筑
        buildings_in_buffer = []
        for b in buildings:
            try:
                building_point = Point(float(b.longitude), float(b.latitude))
                # 计算距离
                distance = calculate_distance(
                    float(b.latitude), float(b.longitude),
                    center_lat, center_lon
                )

                if distance <= radius:
                    # 应用额外过滤条件
                    if min_height and b.height and float(b.height) < min_height:
                        continue
                    if category and b.category != category:
                        continue
                    if risk_level is not None and b.risk_level < risk_level:
                        continue

                    buildings_in_buffer.append({
                        "id": b.id,
                        "name": b.name,
                        "category": b.category,
                        "height": float(b.height) if b.height else None,
                        "longitude": float(b.longitude),
                        "latitude": float(b.latitude),
                        "distance": distance,
                        "address": b.address,
                        "risk_level": b.risk_level,
                    })
            except Exception as e:
                logger.warning(f"处理建筑 {b.id} 时出错: {e}")
                continue

        # 按距离排序
        buildings_in_buffer.sort(key=lambda x: x["distance"])

        # 生成统计信息
        statistics = {
            "by_category": {},
            "by_height": {
                "0-50m": 0,
                "50-100m": 0,
                "100-200m": 0,
                "200m+": 0
            },
            "by_risk_level": {},
            "average_distance": sum(b["distance"] for b in buildings_in_buffer) / len(buildings_in_buffer) if buildings_in_buffer else 0
        }

        for b in buildings_in_buffer:
            # 按类型统计
            cat = b["category"] or "未分类"
            statistics["by_category"][cat] = statistics["by_category"].get(cat, 0) + 1

            # 按高度统计
            h = b["height"] or 0
            if h < 50:
                statistics["by_height"]["0-50m"] += 1
            elif h < 100:
                statistics["by_height"]["50-100m"] += 1
            elif h < 200:
                statistics["by_height"]["100-200m"] += 1
            else:
                statistics["by_height"]["200m+"] += 1

            # 按风险等级统计
            risk = b["risk_level"] or 0
            statistics["by_risk_level"][risk] = statistics["by_risk_level"].get(risk, 0) + 1

        logger.info(f"✅ 缓冲区分析完成: 找到 {len(buildings_in_buffer)} 个建筑")

        return {
            "center": {"longitude": center_lon, "latitude": center_lat},
            "radius": radius,
            "total": len(buildings_in_buffer),
            "data": buildings_in_buffer,
            "statistics": statistics
        }

    except Exception as e:
        logger.error(f"❌ 缓冲区分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"缓冲区分析失败: {str(e)}")


@router.get("/viewshed")
async def viewshed_analysis(
    longitude: float = Query(..., description="观察点经度"),
    latitude: float = Query(..., description="观察点纬度"),
    observer_height: float = Query(50, ge=0, description="观察者高度(米)"),
    radius: float = Query(1000, gt=0, description="分析半径(米)"),
    db: Session = Depends(get_db)
):
    """
    视域分析

    分析从观察点可见的区域（简化版，基于高度差判断）

    参数:
        longitude: 观察点经度
        latitude: 观察点纬度
        observer_height: 观察者高度（米）
        radius: 分析半径（米）

    返回:
        - visible_areas: 可见区域列表
        - coverage_percent: 覆盖率百分比
        - statistics: 统计信息
    """
    logger.info(f"👁️ 视域分析请求: observer=({longitude}, {latitude}), height={observer_height}m")

    try:
        # 获取范围内的建筑
        buildings = db.query(Building).all()

        visible_areas = []
        visible_count = 0
        total_count = 0

        for b in buildings:
            try:
                # 计算距离
                distance = calculate_distance(
                    float(b.latitude), float(b.longitude),
                    latitude, longitude
                )

                if distance <= radius:
                    total_count += 1

                    # 简化的可见性判断：基于高度差
                    building_height = float(b.height) if b.height else 0
                    observer_elevation = observer_height

                    # 如果建筑高度高于观察者高度，可能遮挡
                    # 这里使用简化模型，实际应该使用3D可见性分析
                    is_visible = building_height < observer_elevation or distance > 500

                    visible_areas.append({
                        "id": b.id,
                        "name": b.name,
                        "longitude": float(b.longitude),
                        "latitude": float(b.latitude),
                        "height": building_height,
                        "distance": distance,
                        "visible": is_visible
                    })

                    if is_visible:
                        visible_count += 1

            except Exception as e:
                logger.warning(f"处理建筑 {b.id} 时出错: {e}")
                continue

        coverage_percent = (visible_count / total_count * 100) if total_count > 0 else 0

        logger.info(f"✅ 视域分析完成: 可见率 {coverage_percent:.1f}%")

        return {
            "observer": {"longitude": longitude, "latitude": latitude, "height": observer_height},
            "radius": radius,
            "total_analyzed": total_count,
            "visible_count": visible_count,
            "coverage_percent": round(coverage_percent, 2),
            "visible_areas": visible_areas,
            "statistics": {
                "average_visibility_distance": sum(
                    a["distance"] for a in visible_areas if a["visible"]
                ) / visible_count if visible_count > 0 else 0
            }
        }

    except Exception as e:
        logger.error(f"❌ 视域分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"视域分析失败: {str(e)}")


@router.get("/accessibility")
async def accessibility_analysis(
    origin_lon: float = Query(..., description="起点经度"),
    origin_lat: float = Query(..., description="起点纬度"),
    mode: str = Query("driving", description="交通方式: driving, walking, transit"),
    time_limit: int = Query(15, ge=1, le=120, description="时间限制(分钟)"),
    db: Session = Depends(get_db)
):
    """
    可达性分析

    分析指定时间内的可达范围（简化版，基于距离估算）

    参数:
        origin_lon: 起点经度
        origin_lat: 起点纬度
        mode: 交通方式 (driving, walking, transit)
        time_limit: 时间限制（分钟）

    返回:
        - isochrones: 等时圈列表
        - reachable_pois: 可达的POI数量
        - coverage_area: 覆盖面积（平方公里）
    """
    logger.info(f"🚗 可达性分析请求: origin=({origin_lon}, {origin_lat}), mode={mode}, time={time_limit}min")

    try:
        # 速度估算（米/分钟）
        speeds = {
            "driving": 833.3,    # ~50 km/h
            "walking": 83.3,     # ~5 km/h
            "transit": 416.7     # ~25 km/h (包含换乘时间)
        }

        speed = speeds.get(mode, speeds["driving"])
        max_distance = speed * time_limit

        # 生成等时圈（每5分钟一个圈）
        isochrones = []
        num_intervals = min(4, time_limit // 5 + 1)

        for i in range(1, num_intervals + 1):
            interval_time = i * 5
            if interval_time > time_limit:
                break

            interval_distance = speed * interval_time

            # 生成简化的等时圈坐标（圆形，实际应该使用路网分析）
            num_points = 32
            coordinates = []
            for j in range(num_points):
                angle = (2 * math.pi * j) / num_points
                # 简单的圆形等时圈
                lat_offset = (interval_distance * math.cos(angle)) / 111320  # 纬度1度约111km
                lon_offset = (interval_distance * math.sin(angle)) / (111320 * math.cos(math.radians(origin_lat)))

                coordinates.extend([
                    origin_lon + lon_offset,
                    origin_lat + lat_offset
                ])

            isochrones.append({
                "time": interval_time,
                "distance": interval_distance,
                "coordinates": coordinates
            })

        # 统计可达范围内的建筑
        buildings = db.query(Building).all()
        reachable_count = 0

        for b in buildings:
            try:
                distance = calculate_distance(
                    float(b.latitude), float(b.longitude),
                    origin_lat, origin_lon
                )

                if distance <= max_distance:
                    reachable_count += 1
            except Exception:
                continue

        # 计算覆盖面积（简化为圆形）
        coverage_area = math.pi * (max_distance / 1000) ** 2

        logger.info(f"✅ 可达性分析完成: 覆盖 {coverage_area:.2f} km², {reachable_count} 个建筑")

        return {
            "origin": {"longitude": origin_lon, "latitude": origin_lat},
            "mode": mode,
            "time_limit": time_limit,
            "max_distance": max_distance,
            "isochrones": isochrones,
            "reachable_pois": reachable_count,
            "coverage_area": round(coverage_area, 2),
            "statistics": {
                "isochrone_count": len(isochrones),
                "average_speed_kmh": round((speed * 60) / 1000, 1)
            }
        }

    except Exception as e:
        logger.error(f"❌ 可达性分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"可达性分析失败: {str(e)}")
