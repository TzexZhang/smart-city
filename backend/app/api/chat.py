# -*- coding: utf-8 -*-
"""聊天和对话API"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from app.database import get_db
from app.core.deps import get_current_user
from app.models import AIConversation, User, UserConfig
from app.services.ai_service import AIService
from app.services.ai.providers import Message
from app.services.mcp import get_mcp_manager, DataEnhancementClient
from app.services.weather_scene_service import execute_weather_scene_action

router = APIRouter(prefix="/chat", tags=["聊天"])


@router.post("/completions")
async def chat_completion(
    request_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """聊天补全"""
    session_id = request_data.get("session_id") or str(uuid.uuid4())
    message_content = request_data.get("message")

    # 保存用户消息
    user_message = AIConversation(
        user_id=current_user.id,
        session_id=session_id,
        role="user",
        content=message_content
    )
    db.add(user_message)

    # 获取用户配置
    result = await db.execute(
        select(UserConfig).where(UserConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    # 构建对话历史
    history_result = await db.execute(
        select(AIConversation)
        .where(
            AIConversation.session_id == session_id,
            AIConversation.user_id == current_user.id
        )
        .order_by(AIConversation.created_at)
        .limit(20)
    )
    history = list(history_result.scalars().all())

    # 构建消息列表（排除最后一条，那是刚刚保存的当前用户消息）
    messages = []
    prev_messages = history[:-1]

    # 如果有之前的对话历史，添加system提示
    if prev_messages:
        messages.append(Message(role="system", content="你是智慧城市控制大脑，负责理解用户自然语言指令并控制系统动作。"))

    # 添加之前的对话消息
    for msg in prev_messages:
        messages.append(Message(role=msg.role, content=msg.content))

    # 添加当前用户消息
    messages.append(Message(role="user", content=message_content))

    # 获取Function Calling工具定义
    tools = get_function_tools()

    # 调用AI服务
    ai_service = AIService(db)
    try:
        # 尝试调用AI服务，如果未配置Provider则使用模拟响应
        try:
            response = await ai_service.chat_completion(
                user_id=current_user.id,
                messages=messages,
                model=config.model_name if config else "glm-4-flash",
                temperature=float(config.temperature) if config else 0.7,
                tools=tools
            )
        except ValueError as e:
            if "未配置可用的AI Provider" in str(e):
                # 使用简单的规则匹配作为fallback
                logger.warning("⚠️ 未配置AI Provider，使用简单规则匹配")

                actions = []
                message_lower = message_content.lower()

                # 简单的城市名称匹配
                city_keywords = {
                    '上海': '上海', '北京': '北京', '广州': '广州', '深圳': '深圳',
                    '香港': '香港', 'hangzhou': '杭州', 'shanghai': '上海',
                    'beijing': '北京', 'guangzhou': '广州', 'shenzhen': '深圳',
                    'hong kong': '香港'
                }

                for city_name, city_value in city_keywords.items():
                    if city_name in message_lower or city_value in message_content:
                        actions.append({
                            "type": "camera_flyTo",
                            "parameters": {"city": city_value}
                        })
                        break

                # 模拟AI响应
                from app.services.ai.providers import ChatCompletionResponse
                response = ChatCompletionResponse(
                    content=f"好的，正在为您执行相关操作。",
                    model="rule-based",
                    tokens_used={"total_tokens": 0},
                    finish_reason="stop",
                    tool_calls=None
                )

                if actions:
                    logger.info(f"✅ 规则匹配到 actions: {actions}")
                else:
                    logger.warning(f"⚠️ 未匹配到规则，输入: {message_content}")
            else:
                raise

        # 保存助手回复
        assistant_message = AIConversation(
            user_id=current_user.id,
            session_id=session_id,
            role="assistant",
            content=response.content,
            model_name=config.model_name if config else "glm-4-flash",
            tokens_used=response.tokens_used.get("total_tokens", 0)
        )
        db.add(assistant_message)
        await db.commit()

        # 提取tool_calls并转换为前端期望的格式
        actions = []
        if response.tool_calls:
            for tc in response.tool_calls:
                function = tc.get("function", {})
                function_name = function.get("name", "")
                function_args = function.get("arguments", "{}")

                # 解析函数参数
                try:
                    import json
                    parameters = json.loads(function_args) if isinstance(function_args, str) else function_args
                except:
                    parameters = {}

                # 特殊处理：query_and_apply_weather 需要展开为多个actions
                if function_name == "query_and_apply_weather":
                    logger.info(f"🎬 检测到天气场景请求，生成组合actions")
                    scene_result = await execute_weather_scene_action(
                        city=parameters.get("city"),
                        latitude=parameters.get("latitude"),
                        longitude=parameters.get("longitude")
                    )

                    if scene_result.get("error"):
                        # 如果失败，添加错误提示
                        logger.error(f"❌ 生成天气场景失败: {scene_result['error']}")
                        actions.append({
                            "type": "error",
                            "parameters": {
                                "message": scene_result['error']
                            }
                        })
                    else:
                        # 将组合actions添加到列表
                        scene_actions = scene_result.get("actions", [])
                        actions.extend(scene_actions)
                        logger.info(f"✅ 生成 {len(scene_actions)} 个场景actions")
                else:
                    # 普通action，直接添加
                    actions.append({
                        "type": function_name,
                        "parameters": parameters
                    })

        return {
            "code": 200,
            "data": {
                "session_id": session_id,
                "message": {
                    "role": "assistant",
                    "content": response.content
                },
                "actions": actions,  # 总是返回actions列表，即使为空
                "tokens_used": response.tokens_used
            }
        }

    except Exception as e:
        # 保存错误信息
        error_message = AIConversation(
            user_id=current_user.id,
            session_id=session_id,
            role="assistant",
            content=f"抱歉，发生了错误：{str(e)}"
        )
        db.add(error_message)
        await db.commit()

        raise


async def query_with_database_fallback(
    db: AsyncSession,
    query_params: dict,
    mcp_manager=None
) -> dict:
    """
    数据库优先查询策略

    优先级: 本地数据库 -> Redis缓存 -> MCP增强查询 -> AI生成补充

    Args:
        db: 数据库会话
        query_params: 查询参数
        mcp_manager: MCP管理器（可选）

    Returns:
        查询结果
    """
    from app.models import Building
    from sqlalchemy import and_, or_

    logger.info(f"🔍 数据库优先查询: {query_params}")

    try:
        # 1. 尝试从本地数据库查询
        conditions = []

        city = query_params.get("city")
        if city:
            conditions.append(Building.city == city)

        district = query_params.get("district")
        if district:
            conditions.append(Building.district == district)

        min_height = query_params.get("min_height")
        if min_height is not None:
            conditions.append(Building.height >= min_height)

        max_height = query_params.get("max_height")
        if max_height is not None:
            conditions.append(Building.height <= max_height)

        category = query_params.get("category")
        if category:
            conditions.append(Building.category == category)

        risk_level = query_params.get("risk_level")
        if risk_level is not None:
            conditions.append(Building.risk_level >= risk_level)

        keyword = query_params.get("keyword")
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
        buildings = query.limit(50).all()

        if buildings:
            logger.info(f"✅ 从数据库找到 {len(buildings)} 条记录")

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
                })

            return {
                "source": "database",
                "total": len(results),
                "buildings": results,
                "query_params": query_params
            }

        # 2. 数据库无结果，尝试MCP增强查询
        if mcp_manager:
            logger.info("📡 数据库无结果，尝试MCP增强查询")
            try:
                mcp_result = await mcp_manager.call_tool(
                    "data-enhancement",
                    "search_buildings",
                    query_params
                )

                if mcp_result.get("status") == "success" and mcp_result.get("buildings"):
                    logger.info(f"✅ MCP查询找到 {len(mcp_result['buildings'])} 条记录")
                    return {
                        "source": "mcp",
                        **mcp_result
                    }
            except Exception as e:
                logger.warning(f"⚠️ MCP查询失败: {e}")

        # 3. 无数据源返回结果，返回空结果
        logger.info("ℹ️ 所有数据源均无结果")
        return {
            "source": "none",
            "total": 0,
            "buildings": [],
            "message": "未找到匹配的建筑数据",
            "query_params": query_params
        }

    except Exception as e:
        logger.error(f"❌ 查询失败: {e}")
        return {
            "source": "error",
            "error": str(e),
            "total": 0,
            "buildings": []
        }


def get_function_tools():
    """获取Function Calling工具定义"""
    return [
        {
            "type": "function",
            "function": {
                "name": "camera_flyTo",
                "description": "控制3D相机飞行到指定城市或位置。支持城市名称（如：北京、上海、广州、深圳、香港）或经纬度坐标",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称（支持：北京、上海、广州、深圳、香港、Beijing、Shanghai、Guangzhou、Shenzhen、Hong Kong）",
                            "enum": ["北京", "上海", "广州", "深圳", "香港", "Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Hong Kong"]
                        },
                        "longitude": {
                            "type": "number",
                            "description": "目标经度（如果没有提供城市名称）"
                        },
                        "latitude": {
                            "type": "number",
                            "description": "目标纬度（如果没有提供城市名称）"
                        },
                        "height": {
                            "type": "number",
                            "description": "飞行高度(米)，默认50000"
                        },
                        "duration": {
                            "type": "number",
                            "description": "飞行时长(秒)，默认3.0"
                        },
                        "heading": {
                            "type": "number",
                            "description": "航向角(度)，默认0"
                        },
                        "pitch": {
                            "type": "number",
                            "description": "俯仰角(度)，默认-45"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "highlight_buildings",
                "description": "高亮显示指定的建筑物",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "building_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "建筑ID列表"
                        },
                        "color": {
                            "type": "string",
                            "description": "高亮颜色(HEX)"
                        }
                    },
                    "required": ["building_ids", "color"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_buildings",
                "description": "查询符合条件的建筑物列表（优先从数据库查询）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "district": {"type": "string"},
                        "min_height": {"type": "number"},
                        "max_height": {"type": "number"},
                        "category": {"type": "string"},
                        "risk_level": {"type": "number"},
                        "keyword": {"type": "string"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "spatial_buffer",
                "description": "缓冲区分析 - 分析指定半径范围内的建筑分布",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "longitude": {"type": "number", "description": "圆心经度"},
                        "latitude": {"type": "number", "description": "圆心纬度"},
                        "radius": {"type": "number", "description": "半径(米)，默认1000"},
                        "min_height": {"type": "number", "description": "最小高度过滤"},
                        "category": {"type": "string", "description": "建筑类型过滤"}
                    },
                    "required": ["longitude", "latitude"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "spatial_viewshed",
                "description": "视域分析 - 分析从观察点可见的区域",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "longitude": {"type": "number", "description": "观察点经度"},
                        "latitude": {"type": "number", "description": "观察点纬度"},
                        "observer_height": {"type": "number", "description": "观察者高度(米)，默认50"},
                        "radius": {"type": "number", "description": "分析半径(米)，默认1000"}
                    },
                    "required": ["longitude", "latitude"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "spatial_accessibility",
                "description": "可达性分析 - 分析指定时间内的可达范围",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "longitude": {"type": "number", "description": "起点经度"},
                        "latitude": {"type": "number", "description": "起点纬度"},
                        "mode": {"type": "string", "description": "交通方式: driving, walking, transit", "enum": ["driving", "walking", "transit"]},
                        "time_limit": {"type": "number", "description": "时间限制(分钟)，默认15"}
                    },
                    "required": ["longitude", "latitude"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_weather",
                "description": "设置3D场景的天气效果（雨、雪、雾、晴天等）和日夜光照",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "condition": {
                            "type": "string",
                            "enum": ["clear", "cloudy", "rain", "snow", "fog"],
                            "description": "天气条件"
                        },
                        "intensity": {
                            "type": "number",
                            "description": "天气强度(0-1)，默认0.5"
                        },
                        "is_day": {
                            "type": "boolean",
                            "description": "是否白天，默认true"
                        }
                    }
                },
                "required": ["condition"]
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取指定城市或位置的实时天气数据，并自动应用到3D场景",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称（如：Beijing, Shanghai, London）"
                        },
                        "latitude": {
                            "type": "number",
                            "description": "纬度（与city二选一）"
                        },
                        "longitude": {
                            "type": "number",
                            "description": "经度（与city二选一）"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_and_apply_weather",
                "description": "查询城市天气并自动应用完整场景：飞行到该城市 → 获取实时天气 → 应用天气效果（雨/雪/雾+昼夜光照）。例如：'西安天气'会飞到西安、获取天气、显示对应的天气效果。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称（支持：北京、上海、广州、深圳、香港、西安、成都、杭州等，Beijing、Shanghai等）"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    ]


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话历史"""
    result = await db.execute(
        select(AIConversation)
        .where(
            AIConversation.session_id == session_id,
            AIConversation.user_id == current_user.id
        )
        .order_by(AIConversation.created_at)
        .limit(50)
    )
    conversations = result.scalars().all()

    return {
        "code": 200,
        "data": [
            {
                "role": conv.role,
                "content": conv.content,
                "created_at": conv.created_at.isoformat()
            }
            for conv in conversations
        ]
    }


@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """清空对话历史"""
    from sqlalchemy import delete as sql_delete

    await db.execute(
        sql_delete(AIConversation)
        .where(
            AIConversation.session_id == session_id,
            AIConversation.user_id == current_user.id
        )
    )
    await db.commit()

    return {
        "code": 200,
        "message": "对话历史已清空"
    }
