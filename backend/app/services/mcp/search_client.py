"""
数据检索增强MCP客户端
提供本地数据库和外部数据源的统一检索接口
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
import logging
from .base_client import MCPClientBase
from .config import MCPServerConfig

logger = logging.getLogger(__name__)


class DataEnhancementClient(MCPClientBase):
    """数据增强检索客户端"""

    def __init__(self, config: MCPServerConfig, db: AsyncSession = None):
        super().__init__(config)
        self.db = db

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用数据增强工具"""
        try:
            if tool_name == "search_buildings":
                return await self._search_buildings(parameters)
            elif tool_name == "search_poi":
                return await self._search_poi(parameters)
            elif tool_name == "get_statistics":
                return await self._get_statistics(parameters)
            elif tool_name == "semantic_search":
                return await self._semantic_search(parameters)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"数据增强调用失败: {e}")
            return {"error": str(e)}

    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出具可用的数据增强工具"""
        return [
            {
                "name": "search_buildings",
                "description": "智能建筑检索，支持多维度筛选",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "district": {"type": "string"},
                        "min_height": {"type": "number"},
                        "max_height": {"type": "number"},
                        "category": {"type": "string"},
                        "risk_level": {"type": "number"},
                        "keyword": {"type": "string"},
                        "limit": {"type": "number", "default": 20}
                    }
                }
            },
            {
                "name": "search_poi",
                "description": "兴趣点(POI)搜索",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "longitude": {"type": "number"},
                        "latitude": {"type": "number"},
                        "radius": {"type": "number", "default": 1000},
                        "poi_type": {"type": "string"}
                    }
                }
            },
            {
                "name": "get_statistics",
                "description": "获取建筑统计数据",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "group_by": {"type": "string", "enum": ["category", "height", "risk_level"]}
                    }
                }
            },
            {
                "name": "semantic_search",
                "description": "语义搜索（结合AI理解）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "number", "default": 10}
                    }
                }
            }
        ]

    async def _search_buildings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能建筑检索

        Args:
            params: 检索参数

        Returns:
            建筑列表
        """
        if not self.db:
            return {"error": "数据库连接不可用"}

        try:
            from app.models import Building

            # 构建查询条件
            conditions = []

            city = params.get("city")
            if city:
                conditions.append(Building.city == city)

            district = params.get("district")
            if district:
                conditions.append(Building.district == district)

            min_height = params.get("min_height")
            if min_height is not None:
                conditions.append(Building.height >= min_height)

            max_height = params.get("max_height")
            if max_height is not None:
                conditions.append(Building.height <= max_height)

            category = params.get("category")
            if category:
                conditions.append(Building.category == category)

            risk_level = params.get("risk_level")
            if risk_level is not None:
                conditions.append(Building.risk_level >= risk_level)

            keyword = params.get("keyword")
            if keyword:
                conditions.append(
                    or_(
                        Building.name.contains(keyword),
                        Building.address.contains(keyword),
                        Building.description.contains(keyword)
                    )
                )

            # 执行查询
            query = self.db.query(Building).filter(and_(*conditions))
            limit = params.get("limit", 20)
            buildings = query.limit(limit).all()

            # 格式化结果
            results = []
            for b in buildings:
                results.append({
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
                })

            return {
                "status": "success",
                "total": len(results),
                "buildings": results,
                "query_params": params
            }

        except Exception as e:
            logger.error(f"建筑检索失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _search_poi(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        POI搜索（简化实现）

        Args:
            params: 搜索参数

        Returns:
            POI列表
        """
        # 这里可以集成高德地图POI搜索API
        # 暂时返回模拟数据
        return {
            "status": "success",
            "message": "POI搜索功能需要配置高德地图API",
            "params": params
        }

    async def _get_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取统计数据

        Args:
            params: 统计参数

        Returns:
            统计结果
        """
        if not self.db:
            return {"error": "数据库连接不可用"}

        try:
            from app.models import Building
            from sqlalchemy import func

            city = params.get("city")
            group_by = params.get("group_by", "category")

            # 基础查询
            query = self.db.query(Building)
            if city:
                query = query.filter(Building.city == city)

            total = query.count()

            # 分组统计
            if group_by == "category":
                stats = self.db.query(
                    Building.category,
                    func.count(Building.id)
                ).group_by(Building.category).all()

                return {
                    "status": "success",
                    "total": total,
                    "group_by": "category",
                    "statistics": {cat: count for cat, count in stats}
                }
            elif group_by == "height":
                stats = {
                    "0-50m": query.filter(Building.height < 50).count(),
                    "50-100m": query.filter(
                        and_(Building.height >= 50, Building.height < 100)
                    ).count(),
                    "100-200m": query.filter(
                        and_(Building.height >= 100, Building.height < 200)
                    ).count(),
                    "200m+": query.filter(Building.height >= 200).count(),
                }

                return {
                    "status": "success",
                    "total": total,
                    "group_by": "height",
                    "statistics": stats
                }
            elif group_by == "risk_level":
                stats = self.db.query(
                    Building.risk_level,
                    func.count(Building.id)
                ).group_by(Building.risk_level).all()

                return {
                    "status": "success",
                    "total": total,
                    "group_by": "risk_level",
                    "statistics": {risk: count for risk, count in stats}
                }
            else:
                return {"error": f"Unsupported group_by: {group_by}"}

        except Exception as e:
            logger.error(f"统计查询失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _semantic_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        语义搜索（结合AI理解用户意图）

        Args:
            params: 搜索参数

        Returns:
            搜索结果
        """
        # 这里可以集成向量搜索或AI增强检索
        # 暂时返回基础搜索结果
        query = params.get("query", "")
        limit = params.get("limit", 10)

        # 简单的关键词提取
        keywords = query.split()

        # 使用建筑检索
        return await self._search_buildings({
            "keyword": " ".join(keywords[:3]),  # 取前3个关键词
            "limit": limit
        })

    def set_db(self, db: AsyncSession):
        """设置数据库连接"""
        self.db = db
