"""
示例数据种子文件
用于初始化数据库和测试
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime, date
import uuid

from app.models import Building, User, AIModel, AIProvider
from app.database import SessionLocal
from app.core.security import hash_password as get_password_hash


def generate_uuid():
    """生成UUID字符串"""
    return str(uuid.uuid4())


def seed_users(session: Session):
    """创建示例用户"""
    users = [
        {
            "username": "admin",
            "email": "admin@smartcity.com",
            "password": "admin123",
            "full_name": "系统管理员",
            "phone": "13800138000",
            "status": 1
        },
        {
            "username": "planner",
            "email": "planner@smartcity.com",
            "password": "planner123",
            "full_name": "城市规划师",
            "phone": "13800138001",
            "status": 1
        },
        {
            "username": "geek",
            "email": "geek@smartcity.com",
            "password": "geek123",
            "full_name": "技术极客",
            "phone": "13800138002",
            "status": 1
        }
    ]

    for user_data in users:
        # 检查用户是否已存在
        existing = session.query(User).filter(
            User.username == user_data["username"]
        ).first()

        if not existing:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                phone=user_data["phone"],
                status=user_data["status"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(user)

    session.commit()
    print("✅ 用户数据已创建")


def seed_ai_models(session: Session):
    """创建AI模型配置"""
    models = [
        {
            "provider_code": "zhipu",
            "model_code": "glm-4-flash",
            "model_name": "智谱 GLM-4 Flash",
            "description": "免费高性能模型，适合日常使用",
            "context_length": 128000,
            "is_free": True,
            "input_price": 0,
            "output_price": 0,
            "supports_function_calling": True,
            "supports_vision": False,
            "max_tokens": 128000,
            "display_order": 1
        },
        {
            "provider_code": "zhipu",
            "model_code": "glm-4-plus",
            "model_name": "智谱 GLM-4 Plus",
            "description": "增强版模型，更强的理解能力",
            "context_length": 128000,
            "is_free": True,
            "input_price": 0.0001,
            "output_price": 0.0001,
            "supports_function_calling": True,
            "supports_vision": False,
            "max_tokens": 128000,
            "display_order": 2
        },
        {
            "provider_code": "qwen",
            "model_code": "qwen-turbo",
            "model_name": "通义千问 Qwen Turbo",
            "description": "阿里云通义千问，响应快速",
            "context_length": 8000,
            "is_free": True,
            "input_price": 0,
            "output_price": 0,
            "supports_function_calling": True,
            "supports_vision": False,
            "max_tokens": 6000,
            "display_order": 3
        },
        {
            "provider_code": "deepseek",
            "model_code": "deepseek-chat",
            "model_name": "DeepSeek Chat",
            "description": "深度求索，强大的代码生成能力",
            "context_length": 64000,
            "is_free": True,
            "input_price": 0,
            "output_price": 0,
            "supports_function_calling": True,
            "supports_vision": False,
            "max_tokens": 4096,
            "display_order": 4
        }
    ]

    for model_data in models:
        existing = session.query(AIModel).filter(
            AIModel.model_code == model_data["model_code"]
        ).first()

        if not existing:
            model = AIModel(
                id=generate_uuid(),
                **model_data,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(model)

    session.commit()
    print("✅ AI模型配置已创建")


def seed_buildings(session: Session):
    """创建示例建筑数据"""
    # 北京朝阳区示例建筑
    buildings_data = [
        {
            "name": "中国尊",
            "category": "commercial",
            "height": 528,
            "longitude": 116.3974,
            "latitude": 39.9093,
            "address": "北京市朝阳区光华路15号",
            "district": "朝阳区",
            "city": "北京",
            "risk_level": 0,
            "floors": 108,
            "build_year": 2014,
            "area": 437000,
            "description": "北京最高建筑，中信大厦总部",
            "geometry_type": "polygon",
            "roof_type": "flat",
            "material_type": "steel_glass",
            "usage_type": "办公",
            "fire_resistance_level": 1,
            "seismic_fortification_level": 8,
            "has_basement": True,
            "basement_floors": 5,
            "data_source": "manual"
        },
        {
            "name": "朝阳公园",
            "category": "public",
            "height": 15,
            "longitude": 116.4831,
            "latitude": 39.9219,
            "address": "北京市朝阳区朝阳公园南路1号",
            "district": "朝阳区",
            "city": "北京",
            "risk_level": 0,
            "description": "城市公园",
            "geometry_type": "polygon",
            "data_source": "manual"
        },
        {
            "name": "国贸大厦",
            "category": "commercial",
            "height": 330,
            "longitude": 116.4569,
            "latitude": 39.9087,
            "address": "北京市朝阳区建国门外大街1号",
            "district": "朝阳区",
            "city": "北京",
            "risk_level": 1,
            "floors": 38,
            "build_year": 1990,
            "area": 280000,
            "description": "中国国际贸易中心主楼",
            "geometry_type": "polygon",
            "roof_type": "flat",
            "material_type": "concrete",
            "usage_type": "办公",
            "fire_resistance_level": 2,
            "seismic_fortification_level": 7,
            "has_basement": True,
            "basement_floors": 3,
            "data_source": "manual"
        },
        {
            "name": "三里屯太古里",
            "category": "retail",
            "height": 12,
            "longitude": 116.4569,
            "latitude": 39.9389,
            "address": "北京市朝阳区三里屯路19号",
            "district": "朝阳区",
            "city": "北京",
            "risk_level": 0,
            "description": "购物中心",
            "geometry_type": "polygon",
            "data_source": "manual"
        },
        {
            "name": "望京SOHO",
            "category": "office",
            "height": 200,
            "longitude": 116.4814,
            "latitude": 39.9999,
            "address": "北京市朝阳区望京街10号",
            "district": "朝阳区",
            "city": "北京",
            "risk_level": 1,
            "floors": 42,
            "build_year": 2014,
            "area": 150000,
            "description": "办公综合体",
            "geometry_type": "polygon",
            "roof_type": "slant",
            "material_type": "glass",
            "usage_type": "办公",
            "fire_resistance_level": 2,
            "seismic_fortification_level": 8,
            "has_basement": True,
            "basement_floors": 2,
            "data_source": "manual"
        },
        {
            "name": "北京首都机场T3航站楼",
            "category": "transportation",
            "height": 45,
            "longitude": 116.5839,
            "latitude": 40.0799,
            "address": "北京市顺义区首都机场路3号",
            "district": "顺义区",
            "city": "北京",
            "risk_level": 1,
            "floors": 5,
            "build_year": 2008,
            "area": 986000,
            "description": "国际机场航站楼",
            "geometry_type": "polygon",
            "roof_type": "curved",
            "material_type": "steel",
            "usage_type": "交通",
            "fire_resistance_level": 1,
            "seismic_fortification_level": 8,
            "data_source": "manual"
        },
        {
            "name": "鸟巢国家体育场",
            "category": "cultural",
            "height": 69,
            "longitude": 116.3967,
            "latitude": 39.9930,
            "address": "北京市朝阳区国家体育场南路1号",
            "district": "朝阳区",
            "city": "北京",
            "risk_level": 0,
            "floors": 5,
            "build_year": 2008,
            "area": 258000,
            "description": "国家体育场，奥运主场馆",
            "geometry_type": "polygon",
            "data_source": "manual"
        },
        {
            "name": "水立方国家游泳中心",
            "category": "sports",
            "height": 31,
            "longitude": 116.3883,
            "latitude": 39.9931,
            "address": "北京市朝阳区天辰东路11号",
            "district": "朝阳区",
            "city": "北京",
            "risk_level": 0,
            "floors": 3,
            "build_year": 2008,
            "area": 79832,
            "description": "国家游泳中心",
            "geometry_type": "polygon",
            "data_source": "manual"
        }
    ]

    for building_data in buildings_data:
        # 检查是否已存在
        existing = session.query(Building).filter(
            Building.name == building_data["name"]
        ).first()

        if not existing:
            building = Building(
                id=generate_uuid(),
                **building_data,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(building)

    session.commit()
    print(f"✅ 已创建 {len(buildings_data)} 个示例建筑")


def seed_all():
    """运行所有种子数据"""
    session = SessionLocal()

    try:
        print("开始创建示例数据...")
        seed_users(session)
        seed_ai_models(session)
        seed_buildings(session)
        print("✅ 所有示例数据创建完成！")
    except Exception as e:
        print(f"❌ 创建数据失败: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    seed_all()
