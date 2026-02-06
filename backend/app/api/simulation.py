"""
空间模拟和分析 API
包括：圆形模拟、影响分析、报告生成等
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import json

from app.database import get_db
from app.models import (
    Building, SimulationRecord, AnalysisReport,
    User, AIConversation
)
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/v1", tags=["模拟与分析"])


@router.post("/simulation/circle")
async def circle_simulation(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    圆形范围模拟

    计算圆形范围内的受影响建筑，并生成可视化操作指令

    请求体：
    {
        "center_lon": 116.3974,
        "center_lat": 39.9093,
        "radius": 500,
        "hazard_type": "fire"
    }

    响应：
    {
        "simulation_id": "uuid",
        "affected_count": 25,
        "affected_buildings": [...],
        "actions": [...],
        "visualization_data": {...}
    }
    """
    center_lon = request.get("center_lon")
    center_lat = request.get("center_lat")
    radius = request.get("radius")
    hazard_type = request.get("hazard_type", "general")

    # 1. 查询范围内的建筑
    buildings = db.query(Building).all()
    affected_buildings = []

    for b in buildings:
        distance = calculate_distance(
            float(b.latitude),
            float(b.longitude),
            center_lat,
            center_lon
        )

        if distance <= radius:
            affected_buildings.append({
                "id": b.id,
                "name": b.name,
                "distance": distance,
                "height": float(b.height) if b.height else 0,
                "category": b.category,
                "risk_level": b.risk_level,
            })

    # 2. 生成可视化操作指令
    actions = generate_visualization_actions(
        affected_buildings,
        hazard_type,
        center_lon,
        center_lat,
        radius
    )

    # 3. 保存模拟记录
    simulation = SimulationRecord(
        user_id=current_user.id,
        simulation_type="circle",
        center_lon=Decimal(str(center_lon)),
        center_lat=Decimal(str(center_lat)),
        radius=Decimal(str(radius)),
        affected_building_ids=json.dumps([b["id"] for b in affected_buildings]),
        impact_summary={
            "total": len(affected_buildings),
            "by_category": count_by_category(affected_buildings),
            "by_risk_level": count_by_risk_level(affected_buildings),
            "hazard_type": hazard_type
        },
        status="completed",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(simulation)
    db.commit()

    return {
        "simulation_id": simulation.id,
        "affected_count": len(affected_buildings),
        "affected_buildings": affected_buildings[:50],  # 限制返回数量
        "actions": actions,
        "visualization_data": {
            "center": {"lon": center_lon, "lat": center_lat},
            "radius": radius,
            "hazard_type": hazard_type
        }
    }


@router.post("/ai/analyze")
async def ai_analyze(
    request: dict,
    geek_mode: bool = Query(False, description="极客模式"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI 分析接口

    支持的分析类型：
    - risk_assessment: 风险评估
    - asset_optimization: 资产优化
    - trend_prediction: 趋势预测

    请求体：
    {
        "analysis_type": "risk_assessment",
        "location": {"city": "北京", "district": "朝阳区"},
        "filters": {"min_height": 100},
        "geek_mode": true
    }
    """
    analysis_type = request.get("analysis_type")
    location = request.get("location", {})
    filters = request.get("filters", {})

    # 构建提示词
    prompt = build_analysis_prompt(analysis_type, location, filters)

    # 调用 AI 服务（这里需要实际的 AI 服务调用）
    # response = await ai_service.call(prompt)

    # 模拟 AI 响应
    if geek_mode:
        # 极客模式：返回完整分析过程
        response = {
            "raw_response": json.dumps({"thought_process": [...]}),
            "parse_steps": [
                {
                    "step": 1,
                    "description": "解析用户需求",
                    "data": {"analysis_type": analysis_type, "location": location}
                },
                {
                    "step": 2,
                    "description": "查询数据库",
                    "data": {"buildings_found": 150}
                },
                {
                    "step": 3,
                    "description": "生成分析结果",
                    "data": {"risk_level": "medium", "recommendations": [...]}
                }
            ],
            "final_actions": [
                {
                    "type": "fly_to",
                    "params": {"location_name": location.get("district", location.get("city", "北京"))}
                },
                {
                    "type": "search_buildings",
                    "params": filters
                }
            ]
        }
    else:
        # 普通模式：只返回最终结果
        response = {
            "summary": {
                "risk_level": "medium",
                "total_buildings": 150,
                "recommendations": ["建议加强消防检查", "更新应急预案"]
            },
            "actions": [
                {
                    "type": "fly_to",
                    "params": {"location_name": location.get("district", "北京")}
                }
            ]
        }

    # 保存分析报告
    report = AnalysisReport(
        user_id=current_user.id,
        report_type=analysis_type,
        title=f"{analysis_type}_{location.get('city', '未知区域')}",
        content=format_report_as_markdown(response),
        summary=response.get("summary", {}),
        visualization_config={"actions": response.get("actions", [])},
        ai_model="zhipu-glm-4",
        generated_at=datetime.now(),
        created_at=datetime.now()
    )
    db.add(report)
    db.commit()

    return response


@router.get("/analysis/reports")
async def get_analysis_reports(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分析报告列表"""
    reports = db.query(AnalysisReport).filter(
        AnalysisReport.user_id == current_user.id
    ).order_by(
        AnalysisReport.generated_at.desc()
    ).offset(offset).limit(limit).all()

    total = db.query(AnalysisReport).filter(
        AnalysisReport.user_id == current_user.id
    ).count()

    return {
        "total": total,
        "data": [
            {
                "id": r.id,
                "report_type": r.report_type,
                "title": r.title,
                "created_at": r.generated_at.isoformat(),
                "ai_model": r.ai_model
            }
            for r in reports
        ]
    }


@router.get("/analysis/reports/{report_id}")
async def get_analysis_report_detail(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取报告详情"""
    report = db.query(AnalysisReport).filter(
        AnalysisReport.id == report_id,
        AnalysisReport.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    return {
        "id": report.id,
        "report_type": report.report_type,
        "title": report.title,
        "content": report.content,
        "summary": report.summary,
        "visualization_config": report.visualization_config,
        "created_at": report.generated_at.isoformat()
    }


# 辅助函数

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两点间距离（米）"""
    import math
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return 6371000 * c


def generate_visualization_actions(
    buildings: list,
    hazard_type: str,
    center_lon: float,
    center_lat: float,
    radius: float
) -> list:
    """生成可视化操作指令"""
    actions = []

    # 根据风险等级设置颜色
    color_map = {
        0: "#00ff00",  # 绿色 - 无风险
        1: "#ffff00",  # 黄色 - 低风险
        2: "#ffa500",  # 橙色 - 中风险
        3: "#ff0000",  # 红色 - 高风险
        4: "#8b0000",  # 深红 - 极高风险
    }

    # 生成更新颜色的操作
    building_colors = {}
    for b in buildings:
        building_colors[b["id"]] = color_map.get(b["risk_level"], "#ffffff")

    actions.append({
        "type": "update_buildings_color",
        "params": {
            "building_ids": list(building_colors.keys()),
            "colors": building_colors
        }
    })

    # 添加圆心标记
    actions.append({
        "type": "add_marker",
        "params": {
            "longitude": center_lon,
            "latitude": center_lat,
            "label": f"{hazard_type}影响范围",
            "color": "#ff0000"
        }
    })

    # 飞到中心位置
    actions.append({
        "type": "fly_to",
        "params": {
            "longitude": center_lon,
            "latitude": center_lat,
            "height": 1000,
            "duration": 2
        }
    })

    return actions


def count_by_category(buildings: list) -> dict:
    """按类别统计"""
    from collections import Counter
    categories = [b["category"] for b in buildings if b.get("category")]
    return dict(Counter(categories))


def count_by_risk_level(buildings: list) -> dict:
    """按风险等级统计"""
    from collections import Counter
    risks = [b["risk_level"] for b in buildings if "risk_level" in b]
    return dict(Counter(risks))


def build_analysis_prompt(analysis_type: str, location: dict, filters: dict) -> str:
    """构建 AI 分析提示词"""
    return f"""
    请对 {location.get('city', '未知')} {location.get('district', '')} 进行 {analysis_type} 分析。

筛选条件：{json.dumps(filters, ensure_ascii=False)}

请提供：
1. 分析结果摘要
2. 具体的数据统计
3. 可视化建议
4. 可执行的地图操作指令（JSON格式）

返回格式：
{{
  "summary": {{...}},
  "actions": [{{"type": "...", "params": {{...}}}}]
}}
"""


def format_report_as_markdown(response: dict) -> str:
    """格式化报告为 Markdown"""
    md = f"""# {response.get('title', '分析报告')}

## 分析摘要

{json.dumps(response.get('summary', {}), indent=2, ensure_ascii=False)}

## 详细数据

{json.dumps(response.get('detailed_data', {}), indent=2, ensure_ascii=False)}

## 可视化操作

```json
{json.dumps(response.get('actions', []), indent=2, ensure_ascii=False)}
```

## 建议

{chr(10).join(f"- {rec}" for rec in response.get('recommendations', []))}
"""
    return md
