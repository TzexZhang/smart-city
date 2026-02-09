# -*- coding: utf-8 -*-
"""聊天和对话API"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from app.database import get_db
from app.core.deps import get_current_user
from app.models import AIConversation, User, UserConfig
from app.services.ai_service import AIService
from app.services.ai.providers import Message

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
        response = await ai_service.chat_completion(
            user_id=current_user.id,
            messages=messages,
            model=config.model_name if config else "glm-4-flash",
            temperature=float(config.temperature) if config else 0.7,
            tools=tools
        )

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

                # 转换为前端期望的格式
                actions.append({
                    "type": function_name,  # 直接使用function name作为type
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
                "description": "查询符合条件的建筑物列表",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "district": {"type": "string"},
                        "min_height": {"type": "number"},
                        "category": {"type": "string"}
                    }
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
