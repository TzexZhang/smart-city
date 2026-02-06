"""
建筑资产相关 API
包括：搜索、筛选、空间查询等
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from decimal import Decimal
import math

from app.database import get_db
from app.models import Building, User
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/v1/buildings", tags=["建筑资产"])


@router.get("/search")
async def search_buildings(
    min_height: Optional[float] = Query(None, description="最小高度(米)"),
    max_height: Optional[float] = Query(None, description="最大高度(米)"),
    category: Optional[str] = Query(None, description="建筑类型"),
    risk_level: Optional[int] = Query(None, ge=0, le=4, description="风险等级"),
    city: Optional[str] = Query(None, description="城市"),
    district: Optional[str] = Query(None, description="区县"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    搜索建筑资产

    支持多维度筛选：
    - 高度范围
    - 建筑类型
    - 风险等级
    - 城市/区域
    - 关键词搜索
    """
    # 构建查询条件
    conditions = []

    if min_height is not None:
        conditions.append(Building.height >= min_height)
    if max_height is not None:
        conditions.append(Building.height <= max_height)
    if category:
        conditions.append(Building.category == category)
    if risk_level is not None:
        conditions.append(Building.risk_level >= risk_level)
    if city:
        conditions.append(Building.city == city)
    if district:
        conditions.append(Building.district == district)
    if keyword:
        conditions.append(
            or_(
                Building.name.contains(keyword),
                Building.address.contains(keyword),
                Building.description.contains(keyword)
            )
        )

    # 执行查询
    query = db.query(Building).filter(and_(*conditions))

    # 分页
    total = query.count()
    buildings = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": [
            {
                "id": b.id,
                "name": b.name,
                "category": b.category,
                "height": float(b.height) if b.height else None,
                "longitude": float(b.longitude),
                "latitude": float(b.latitude),
                "address": b.address,
                "district": b.district,
                "city": b.city,
                "risk_level": b.risk_level,
                "floors": b.floors,
                "area": float(b.area) if b.area else None,
            }
            for b in buildings
        ]
    }


@router.get("/search/spatial/circle")
async def search_in_circle(
    center_lon: float = Query(..., description="圆心经度"),
    center_lat: float = Query(..., description="圆心纬度"),
    radius: float = Query(..., gt=0, description="半径(米)"),
    min_height: Optional[float] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    圆形范围搜索

    计算两点间距离（Haversine公式），返回圆形范围内的建筑
    """
    # 地球半径（米）
    EARTH_RADIUS = 6371000

    # 查询所有建筑，然后计算距离
    buildings = db.query(Building).all()

    result = []
    for b in buildings:
        # 计算距离
        distance = calculate_distance(
            float(b.latitude),
            float(b.longitude),
            center_lat,
            center_lon
        )

        if distance <= radius:
            # 应用筛选条件
            if min_height and b.height and float(b.height) < min_height:
                continue
            if category and b.category != category:
                continue

            result.append({
                "id": b.id,
                "name": b.name,
                "category": b.category,
                "height": float(b.height) if b.height else None,
                "longitude": float(b.longitude),
                "latitude": float(b.latitude),
                "distance": distance,
                "address": b.address,
            })

    # 按距离排序
    result.sort(key=lambda x: x["distance"])

    return {
        "center": {"longitude": center_lon, "latitude": center_lat},
        "radius": radius,
        "total": len(result),
        "data": result
    }


@router.get("/categories")
async def get_building_categories(db: Session = Depends(get_db)):
    """获取建筑类型列表"""
    categories = db.query(Building.category).distinct().all()
    return {
        "categories": [c[0] for c in categories if c[0]]
    }


@router.get("/statistics/overview")
async def get_building_statistics(
    city: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    建筑统计概览

    返回：
    - 总数量
    - 各类型数量分布
    - 高度分布
    - 风险等级分布
    """
    # 基础查询
    query = db.query(Building)
    if city:
        query = query.filter(Building.city == city)

    total = query.count()

    # 按类型统计
    category_stats = db.query(
        Building.category,
        db.func.count(Building.id)
    ).group_by(Building.category).all()

    # 按高度统计
    height_stats = {
        "0-50m": query.filter(Building.height < 50).count(),
        "50-100m": query.filter(and_(Building.height >= 50, Building.height < 100)).count(),
        "100-200m": query.filter(and_(Building.height >= 100, Building.height < 200)).count(),
        "200m+": query.filter(Building.height >= 200).count(),
    }

    # 按风险等级统计
    risk_stats = db.query(
        Building.risk_level,
        db.func.count(Building.id)
    ).group_by(Building.risk_level).all()

    return {
        "total": total,
        "by_category": {cat: count for cat, count in category_stats},
        "by_height": height_stats,
        "by_risk_level": {risk: count for risk, count in risk_stats}
    }


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    计算两点间的球面距离（Haversine公式）

    Args:
        lat1, lon1: 点1的纬度、经度
        lat2, lon2: 点2的纬度、经度

    Returns:
        距离（米）
    """
    # 将角度转换为弧度
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine 公式
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    # 地球半径（米）
    R = 6371000
    return R * c
