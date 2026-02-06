"""
执行配置和策略管理 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import ExecutionConfig, User
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/v1/execution", tags=["执行配置"])


class ExecutionConfigUpdate(BaseModel):
    """执行配置更新模型"""
    execution_mode: Optional[str] = None  # auto, confirm, manual
    confirm_required_actions: Optional[list] = None
    auto_approve_actions: Optional[list] = None
    show_geek_mode: Optional[bool] = None
    max_undo_count: Optional[int] = None


@router.get("/config", response_model=dict)
async def get_execution_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户执行配置"""
    config = db.query(ExecutionConfig).filter(
        ExecutionConfig.user_id == current_user.id
    ).first()

    if not config:
        # 创建默认配置
        config = ExecutionConfig(
            user_id=current_user.id,
            execution_mode="auto",
            confirm_required_actions=[],
            auto_approve_actions=["fly_to", "add_marker"],
            show_geek_mode=False,
            max_undo_count=10
        )
        db.add(config)
        db.commit()

    return {
        "execution_mode": config.execution_mode,
        "confirm_required_actions": config.confirm_required_actions or [],
        "auto_approve_actions": config.auto_approve_actions or [],
        "show_geek_mode": config.show_geek_mode,
        "max_undo_count": config.max_undo_count
    }


@router.put("/config")
async def update_execution_config(
    updates: ExecutionConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新执行配置"""
    config = db.query(ExecutionConfig).filter(
        ExecutionConfig.user_id == current_user.id
    ).first()

    if not config:
        config = ExecutionConfig(user_id=current_user.id)
        db.add(config)

    # 更新字段
    if updates.execution_mode is not None:
        config.execution_mode = updates.execution_mode
    if updates.confirm_required_actions is not None:
        config.confirm_required_actions = updates.confirm_required_actions
    if updates.auto_approve_actions is not None:
        config.auto_approve_actions = updates.auto_approve_actions
    if updates.show_geek_mode is not None:
        config.show_geek_mode = updates.show_geek_mode
    if updates.max_undo_count is not None:
        config.max_undo_count = updates.max_undo_count

    db.commit()

    return {"message": "配置更新成功", "config": {
        "execution_mode": config.execution_mode,
        "confirm_required_actions": config.confirm_required_actions or [],
        "auto_approve_actions": config.auto_approve_actions or [],
        "show_geek_mode": config.show_geek_mode,
        "max_undo_count": config.max_undo_count
    }}


@router.post("/test-action")
async def test_action_execution(
    action: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    测试动作执行（不实际执行）

    返回该动作是否需要确认
    """
    config = db.query(ExecutionConfig).filter(
        ExecutionConfig.user_id == current_user.id
    ).first()

    if not config:
        config = ExecutionConfig(user_id=current_user.id)

    action_type = action.get("type")
    requires_confirmation = action_type in (config.confirm_required_actions or [])

    return {
        "action": action,
        "requires_confirmation": requires_confirmation,
        "auto_approved": action_type in (config.auto_approve_actions or []),
        "execution_mode": config.execution_mode
    }
