# -*- coding: utf-8 -*-
"""数据库模型"""

from sqlalchemy import Column, String, Boolean, Integer, Text, DECIMAL, DateTime, Index, ForeignKey, JSON, Date, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BOOLEAN
import uuid
import json

from app.database import Base


def generate_uuid():
    """生成UUID字符串"""
    return str(uuid.uuid4())


class User(Base):
    """用户表"""
    __tablename__ = "tb_users"

    id = Column(String(36), primary_key=True, default=generate_uuid, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    full_name = Column(String(100), comment="真实姓名")
    phone = Column(String(20), comment="手机号")
    avatar_url = Column(String(500), comment="头像URL")
    status = Column(Integer, default=1, comment="状态: 0-禁用, 1-正常")
    is_deleted = Column(BOOLEAN, default=False, comment="是否删除")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")

    # 关系
    config = relationship("UserConfig", back_populates="user", uselist=False)
    ai_providers = relationship("AIProvider", back_populates="user")


class UserConfig(Base):
    """用户配置表"""
    __tablename__ = "tb_user_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid, comment="配置ID")
    user_id = Column(String(36), ForeignKey("tb_users.id", ondelete="CASCADE"), unique=True, nullable=False, comment="用户ID")
    provider = Column(String(50), default="zhipu", comment="AI提供商")
    model_name = Column(String(50), default="glm-4-flash", comment="AI模型名称")
    persona = Column(String(20), default="admin", comment="角色: admin-管理员, planner-规划师, geek-极客")
    temperature = Column(DECIMAL(3, 2), default=0.7, comment="温度参数")
    top_p = Column(DECIMAL(3, 2), default=0.9, comment="Top-P参数")
    auto_execute = Column(BOOLEAN, default=False, comment="是否自动执行指令")
    default_city = Column(String(50), default="北京", comment="默认城市")
    language = Column(String(10), default="zh-CN", comment="语言")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="config")


class AIProvider(Base):
    """AI Provider配置表"""
    __tablename__ = "tb_ai_providers"

    id = Column(String(36), primary_key=True, default=generate_uuid, comment="配置ID")
    user_id = Column(String(36), ForeignKey("tb_users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    provider_code = Column(String(50), nullable=False, comment="提供商代码")
    provider_name = Column(String(100), nullable=False, comment="提供商名称")
    api_key_encrypted = Column(Text, comment="加密的API Key")
    api_secret_encrypted = Column(Text, comment="加密的API Secret")
    base_url = Column(String(500), comment="自定义API地址")
    is_enabled = Column(BOOLEAN, default=True, comment="是否启用")
    is_default = Column(BOOLEAN, default=False, comment="是否为默认提供商")
    priority = Column(Integer, default=0, comment="优先级")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="ai_providers")

    # 索引
    __table_args__ = (
        Index('uk_user_provider', 'user_id', 'provider_code', unique=True),
    )


class AIModel(Base):
    """AI模型元数据表"""
    __tablename__ = "tb_ai_models"

    id = Column(String(36), primary_key=True, default=generate_uuid, comment="模型ID")
    provider_code = Column(String(50), nullable=False, comment="提供商代码")
    model_code = Column(String(100), nullable=False, comment="模型代码")
    model_name = Column(String(200), nullable=False, comment="模型显示名称")
    description = Column(Text, comment="模型描述")
    context_length = Column(Integer, comment="上下文长度")
    is_free = Column(BOOLEAN, default=False, comment="是否免费")
    input_price = Column(DECIMAL(10, 4), comment="输入价格")
    output_price = Column(DECIMAL(10, 4), comment="输出价格")
    supports_function_calling = Column(BOOLEAN, default=False, comment="是否支持Function Calling")
    supports_vision = Column(BOOLEAN, default=False, comment="是否支持视觉")
    max_tokens = Column(Integer, comment="最大输出tokens")
    is_active = Column(BOOLEAN, default=True, comment="是否激活")
    display_order = Column(Integer, default=0, comment="显示顺序")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")

    # 索引
    __table_args__ = (
        Index('uk_provider_model', 'provider_code', 'model_code', unique=True),
    )


class Building(Base):
    """建筑资产表"""
    __tablename__ = "tb_buildings"

    id = Column(String(36), primary_key=True, default=generate_uuid, comment="建筑ID")
    name = Column(String(200), nullable=False, comment="建筑名称")
    category = Column(String(50), comment="类型")
    height = Column(DECIMAL(10, 2), comment="建筑高度(米)")
    longitude = Column(DECIMAL(11, 8), nullable=False, comment="经度")
    latitude = Column(DECIMAL(11, 8), nullable=False, comment="纬度")
    address = Column(String(500), comment="详细地址")
    district = Column(String(100), comment="所属区县")
    city = Column(String(50), comment="所属城市")
    status = Column(String(20), default="normal", comment="状态")
    risk_level = Column(Integer, default=0, comment="风险等级")
    floors = Column(Integer, comment="楼层数")
    build_year = Column(Integer, comment="建成年份")
    area = Column(DECIMAL(15, 2), comment="建筑面积")
    description = Column(Text, comment="描述信息")
    is_deleted = Column(BOOLEAN, default=False, comment="是否删除")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")


class AIConversation(Base):
    """AI对话记录表"""
    __tablename__ = "tb_ai_conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid, comment="对话ID")
    user_id = Column(String(36), ForeignKey("tb_users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    session_id = Column(String(36), nullable=False, comment="会话ID")
    role = Column(String(20), nullable=False, comment="角色")
    content = Column(Text, nullable=False, comment="对话内容")
    model_name = Column(String(50), comment="使用的模型")
    tokens_used = Column(Integer, comment="Token消耗量")
    created_at = Column(DateTime, nullable=False, comment="创建时间")


class OperationLog(Base):
    """操作日志表"""
    __tablename__ = "tb_operation_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid, comment="日志ID")
    user_id = Column(String(36), ForeignKey("tb_users.id", ondelete="SET NULL"), comment="用户ID")
    operation_type = Column(String(50), nullable=False, comment="操作类型")
    operation_data = Column(Text, comment="操作数据(JSON格式)")
    ip_address = Column(String(50), comment="IP地址")
    user_agent = Column(Text, comment="用户代理")
    status = Column(String(20), default="success", comment="状态")
    error_message = Column(Text, comment="错误信息")
    created_at = Column(DateTime, nullable=False, comment="创建时间")


class AIUsageStats(Base):
    """用户使用统计表"""
    __tablename__ = "tb_ai_usage_stats"

    id = Column(String(36), primary_key=True, default=generate_uuid, comment="统计ID")
    user_id = Column(String(36), ForeignKey("tb_users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    provider_code = Column(String(50), nullable=False, comment="提供商代码")
    model_code = Column(String(100), nullable=False, comment="模型代码")
    date = Column(DateTime, nullable=False, comment="统计日期")
    request_count = Column(Integer, default=0, comment="请求次数")
    input_tokens = Column(Integer, default=0, comment="输入tokens")
    output_tokens = Column(Integer, default=0, comment="输出tokens")
    total_tokens = Column(Integer, default=0, comment="总tokens")
    estimated_cost = Column(DECIMAL(10, 4), default=0, comment="估算成本")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")


class SimulationRecord(Base):
    """空间模拟记录表"""
    __tablename__ = "tb_simulation_records"

    id = Column(String(36), primary_key=True, default=generate_uuid, comment="模拟ID")
    user_id = Column(String(36), ForeignKey("tb_users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    simulation_type = Column(String(50), nullable=False, comment="模拟类型")
    center_lon = Column(DECIMAL(11, 8), nullable=False, comment="中心经度")
    center_lat = Column(DECIMAL(11, 8), nullable=False, comment="中心纬度")
    radius = Column(DECIMAL(10, 2), comment="半径(米)")
    affected_building_ids = Column(JSON, comment="受影响建筑ID列表")
    impact_summary = Column(JSON, comment="影响摘要")
    status = Column(String(20), default="pending", comment="状态")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")


class CityEvent(Base):
    """城市事件表"""
    __tablename__ = "tb_city_events"

    id = Column(String(36), primary_key=True, default=generate_uuid, comment="事件ID")
    event_name = Column(String(200), nullable=False, comment="事件名称")
    event_type = Column(String(50), nullable=False, comment="事件类型")
    event_date = Column(DateTime, comment="事件时间")
    longitude = Column(DECIMAL(11, 8), comment="经度")
    latitude = Column(DECIMAL(11, 8), comment="纬度")
    radius = Column(DECIMAL(10, 2), comment="影响半径")
    severity = Column(Integer, comment="严重程度 1-5")
    status = Column(String(20), default="active", comment="状态")
    description = Column(Text, comment="描述")
    affected_areas = Column(JSON, comment="受影响区域")
    response_actions = Column(JSON, comment="响应措施")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")


class AnalysisReport(Base):
    """分析报告表"""
    __tablename__ = "tb_analysis_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid, comment="报告ID")
    user_id = Column(String(36), ForeignKey("tb_users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    report_type = Column(String(50), nullable=False, comment="报告类型")
    title = Column(String(200), nullable=False, comment="报告标题")
    content = Column(Text, nullable=False, comment="报告内容(Markdown)")
    summary = Column(JSON, comment="摘要数据")
    visualization_config = Column(JSON, comment="可视化配置")
    ai_model = Column(String(50), comment="使用的AI模型")
    generated_at = Column(DateTime, nullable=False, comment="生成时间")
    created_at = Column(DateTime, nullable=False, comment="创建时间")


class ExecutionConfig(Base):
    """执行配置表"""
    __tablename__ = "tb_execution_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid, comment="配置ID")
    user_id = Column(String(36), ForeignKey("tb_users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    execution_mode = Column(String(20), default="auto", comment="执行模式")
    confirm_required_actions = Column(JSON, comment="需要确认的动作")
    auto_approve_actions = Column(JSON, comment="自动批准的动作")
    log_all_actions = Column(BOOLEAN, default=True, comment="记录所有动作")
    show_geek_mode = Column(BOOLEAN, default=False, comment="显示极客模式")
    max_undo_count = Column(Integer, default=10, comment="最大撤销次数")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")

