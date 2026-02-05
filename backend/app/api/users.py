# -*- coding: utf-8 -*-
"""用户管理API"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import os
from datetime import datetime
from pathlib import Path

from app.database import get_db
from app.core.deps import get_current_user
from app.models import User, UserConfig
from app.schemas import UserConfigResponse, UserUpdate, PasswordUpdate
from app.core.security import verify_password, hash_password

router = APIRouter(prefix="/users", tags=["用户管理"])

# 头像上传目录
UPLOAD_DIR = Path("uploads/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/me")
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return {
        "code": 200,
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone": current_user.phone,
            "avatar_url": current_user.avatar_url,
            "status": current_user.status,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        }
    }


@router.put("/me")
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    # 构建更新数据字典（只更新提供的字段）
    update_data = {}
    if user_data.username is not None:
        # 检查用户名是否已被占用
        result = await db.execute(
            select(User).where(
                User.username == user_data.username,
                User.id != current_user.id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被占用"
            )
        update_data["username"] = user_data.username

    if user_data.email is not None:
        # 检查邮箱是否已被占用
        result = await db.execute(
            select(User).where(
                User.email == user_data.email,
                User.id != current_user.id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被占用"
            )
        update_data["email"] = user_data.email

    if user_data.full_name is not None:
        update_data["full_name"] = user_data.full_name

    if user_data.phone is not None:
        update_data["phone"] = user_data.phone

    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(**update_data)
        )
        await db.commit()

    return {
        "code": 200,
        "message": "用户信息更新成功"
    }


@router.put("/me/password")
async def update_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )

    # 更新密码
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(
            password_hash=hash_password(password_data.new_password),
            updated_at=datetime.utcnow()
        )
    )
    await db.commit()

    return {
        "code": 200,
        "message": "密码修改成功"
    }


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """上传头像"""
    # 验证文件类型
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持 JPG、PNG、GIF、WebP 格式的图片"
        )

    # 验证文件大小（最大5MB）
    MAX_SIZE = 5 * 1024 * 1024
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片大小不能超过5MB"
        )

    # 生成文件名
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{current_user.id}_{int(datetime.utcnow().timestamp())}{file_ext}"
    file_path = UPLOAD_DIR / filename

    # 保存文件
    with open(file_path, "wb") as f:
        f.write(content)

    # 生成访问URL
    avatar_url = f"/static/avatars/{filename}"

    # 删除旧头像
    if current_user.avatar_url and current_user.avatar_url.startswith("/static/avatars/"):
        old_filename = current_user.avatar_url.split("/")[-1]
        old_path = UPLOAD_DIR / old_filename
        if old_path.exists():
            os.remove(old_path)

    # 更新数据库
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(avatar_url=avatar_url, updated_at=datetime.utcnow())
    )
    await db.commit()

    return {
        "code": 200,
        "message": "头像上传成功",
        "data": {"avatar_url": avatar_url}
    }


@router.get("/me/config", response_model=dict)
async def get_user_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户配置"""
    result = await db.execute(
        select(UserConfig).where(UserConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    if not config:
        # 创建默认配置
        config = UserConfig(user_id=current_user.id)
        db.add(config)
        await db.commit()
        await db.refresh(config)

    return {
        "code": 200,
        "data": {
            "provider": config.provider,
            "model_name": config.model_name,
            "persona": config.persona,
            "temperature": float(config.temperature) if config.temperature else 0.7,
            "top_p": float(config.top_p) if config.top_p else 0.9,
            "auto_execute": config.auto_execute,
            "default_city": config.default_city
        }
    }


@router.put("/me/config")
async def update_user_config(
    config_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户配置"""
    result = await db.execute(
        select(UserConfig).where(UserConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    if not config:
        config = UserConfig(user_id=current_user.id)
        db.add(config)

    # 更新配置
    if "provider" in config_data:
        config.provider = config_data["provider"]
    if "model_name" in config_data:
        config.model_name = config_data["model_name"]
    if "persona" in config_data:
        config.persona = config_data["persona"]
    if "temperature" in config_data:
        config.temperature = config_data["temperature"]
    if "top_p" in config_data:
        config.top_p = config_data["top_p"]
    if "auto_execute" in config_data:
        config.auto_execute = config_data["auto_execute"]
    if "default_city" in config_data:
        config.default_city = config_data["default_city"]

    await db.commit()

    return {
        "code": 200,
        "message": "配置更新成功"
    }
