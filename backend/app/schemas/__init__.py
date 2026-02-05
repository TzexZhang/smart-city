# -*- coding: utf-8 -*-
"""Pydantic schemas for data validation"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


# 用户相关
class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """用户注册"""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class UserResponse(UserBase):
    """用户响应"""
    id: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    status: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """更新用户信息"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class PasswordUpdate(BaseModel):
    """修改密码"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)


class Token(BaseModel):
    """Token响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# AI Provider相关
class AIProviderCreate(BaseModel):
    """创建AI Provider"""
    provider_code: str
    provider_name: str
    api_key: Optional[str] = None  # 免费模型可以不需要API Key
    api_secret: Optional[str] = None
    base_url: Optional[str] = None


class AIProviderResponse(BaseModel):
    """AI Provider响应"""
    id: str
    provider_code: str
    provider_name: str
    api_key_encrypted: str  # 只返回部分掩码
    is_enabled: bool
    is_default: bool
    priority: int

    class Config:
        from_attributes = True


# AI模型相关
class ModelInfoResponse(BaseModel):
    """模型信息响应"""
    code: str
    name: str
    description: str
    context_length: int
    is_free: bool
    input_price: float
    output_price: float
    supports_function_calling: bool
    supports_vision: bool
    max_tokens: int

    class Config:
        from_attributes = True


# 用户配置相关
class UserConfigUpdate(BaseModel):
    """更新用户配置"""
    model_config = ConfigDict(protected_namespaces=())

    provider: Optional[str] = None
    model_name: Optional[str] = None
    persona: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    auto_execute: Optional[bool] = None
    default_city: Optional[str] = None


class UserConfigResponse(BaseModel):
    """用户配置响应"""
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    provider: str
    model_name: str
    persona: str
    temperature: float
    top_p: float
    auto_execute: bool
    default_city: str


# 建筑相关
class BuildingResponse(BaseModel):
    """建筑响应"""
    id: str
    name: str
    category: Optional[str]
    height: Optional[float]
    longitude: float
    latitude: float
    address: Optional[str]
    district: Optional[str]
    city: Optional[str]
    status: str

    class Config:
        from_attributes = True


# AI对话相关
class ChatMessage(BaseModel):
    """聊天消息"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """聊天请求"""
    session_id: Optional[str] = None
    message: str
    stream: bool = False


class ChatResponse(BaseModel):
    """聊天响应"""
    session_id: str
    message: ChatMessage
    actions: Optional[list] = None
    tokens_used: Optional[dict] = None


# 分页相关
class PaginatedResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    page_size: int
    items: list


# 通用响应
class ApiResponse(BaseModel):
    """API统一响应"""
    code: int
    message: str
    data: Optional[dict] = None
    timestamp: str
