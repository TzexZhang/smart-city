"""
生成1000+条智慧城市demo数据
包括建筑资产、城市事件、分析报告等
注意：当前使用基础Building模型，如需使用扩展字段请先运行数据库迁移
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import uuid
from decimal import Decimal

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.database import SessionLocal, sync_engine
from app.models import (
    Building, CityEvent, AnalysisReport, User,
    SimulationRecord, ExecutionConfig
)
from app.core.security import hash_password as get_password_hash


def generate_uuid():
    """生成UUID字符串"""
    return str(uuid.uuid4())


def generate_chinese_cities():
    """生成中国主要城市数据"""
    cities = [
        # 直辖市
        {"name": "北京", "districts": ["朝阳区", "海淀区", "东城区", "西城区", "丰台区"], "center": (116.4074, 39.9042)},
        {"name": "上海", "districts": ["黄浦区", "浦东新区", "静安区", "徐汇区", "长宁区"], "center": (121.4737, 31.2304)},
        {"name": "天津", "districts": ["和平区", "河西区", "南开区", "河东区", "河北区"], "center": (117.1901, 39.1209)},
        {"name": "重庆", "districts": ["渝中区", "江北区", "南岸区", "九龙坡区", "沙坪坝区"], "center": (106.5047, 29.5332)},

        # 省会城市
        {"name": "广州", "districts": ["天河区", "越秀区", "海珠区", "荔湾区", "白云区"], "center": (113.2644, 23.1291)},
        {"name": "深圳", "districts": ["福田区", "罗湖区", "南山区", "宝安区", "龙岗区"], "center": (114.0579, 22.5431)},
        {"name": "杭州", "districts": ["西湖区", "上城区", "下城区", "拱墅区", "江干区"], "center": (120.1551, 30.2741)},
        {"name": "南京", "districts": ["玄武区", "秦淮区", "建邺区", "鼓楼区", "浦口区"], "center": (118.7969, 32.0603)},
        {"name": "武汉", "districts": ["江岸区", "江汉区", "硚口区", "汉阳区", "武昌区"], "center": (114.3055, 30.5928)},
        {"name": "成都", "districts": ["锦江区", "青羊区", "金牛区", "武侯区", "成华区"], "center": (104.0665, 30.5723)},
        {"name": "西安", "districts": ["新城区", "碑林区", "莲湖区", "雁塔区", "未央区"], "center": (108.9398, 34.3416)},
        {"name": "苏州", "districts": ["姑苏区", "虎丘区", "吴中区", "相城区", "吴江区"], "center": (120.5853, 31.2989)},
    ]
    return cities


def generate_building_categories():
    """生成建筑类型"""
    return [
        "commercial",  # 商业
        "office",  # 办公
        "residential",  # 住宅
        "industrial",  # 工业
        "public",  # 公共
        "cultural",  # 文化
        "sports",  # 体育
        "educational",  # 教育
        "medical",  # 医疗
        "transportation",  # 交通
        "retail",  # 零售
        "hotel",  # 酒店
    ]


def generate_building_name(city, district, category, index):
    """生成建筑名称"""
    prefixes = {
        "commercial": ["购物中心", "商业广场", "商务中心", "贸易大厦"],
        "office": ["大厦", "写字楼", "商务楼", "办公楼"],
        "residential": ["花园", "家园", "公寓", "小区", "家园"],
        "industrial": ["产业园", "科技园", "工业园", "制造基地"],
        "public": ["市民中心", "政务大厅", "公共服务中心", "图书馆"],
        "cultural": ["博物馆", "艺术中心", "文化宫", "展览馆"],
        "sports": ["体育馆", "运动中心", "体育公园", "健身中心"],
        "educational": ["学校", "大学", "学院", "培训中心"],
        "medical": ["医院", "诊所", "医疗中心", "康复中心"],
        "transportation": ["车站", "地铁站", "机场", "公交枢纽"],
        "retail": ["商场", "超市", "购物中心", "百货"],
        "hotel": ["酒店", "宾馆", "度假村", "公寓"],
    }

    prefix_list = prefixes.get(category, ["建筑"])
    prefix = random.choice(prefix_list)

    # 生成更有特色的名称
    if category in ["commercial", "office"]:
        famous_names = ["中心", "国际", "环球", "金融", "科技", "创新", "未来", "时代", "财富", "金茂"]
        name = f"{city}{district}{random.choice(famous_names)}{prefix}"
    elif category == "residential":
        adjectives = ["阳光", "绿洲", "和谐", "幸福", "美好", "温馨", "美丽", "新时代"]
        name = f"{city}{district}{random.choice(adjectives)}{prefix}"
    else:
        name = f"{city}{district}{prefix}{index if index > 0 else ''}"

    return name


def generate_buildings(session: Session, count: int = 1200):
    """生成大量建筑数据"""
    print(f"开始生成 {count} 条建筑数据...")

    cities = generate_chinese_cities()
    categories = generate_building_categories()

    batch_size = 100
    total_created = 0

    for batch_start in range(0, count, batch_size):
        batch_end = min(batch_start + batch_size, count)
        batch_buildings = []

        for i in range(batch_start, batch_end):
            # 随机选择城市和区域
            city_info = random.choice(cities)
            city = city_info["name"]
            district = random.choice(city_info["districts"])
            category = random.choice(categories)

            # 生成位置（在城市中心附近随机偏移）
            center_lon, center_lat = city_info["center"]
            offset_lon = random.uniform(-0.1, 0.1)
            offset_lat = random.uniform(-0.1, 0.1)
            longitude = round(center_lon + offset_lon, 8)
            latitude = round(center_lat + offset_lat, 8)

            # 生成建筑属性
            height = round(random.uniform(10, 500), 2)  # 10-500米
            floors = int(height / 3) if height > 50 else random.randint(1, 20)
            build_year = random.randint(1990, 2024)
            area = round(random.uniform(500, 500000), 2)
            risk_level = random.choices([0, 1, 2, 3, 4], weights=[70, 15, 10, 4, 1])[0]

            building = Building(
                id=generate_uuid(),
                name=generate_building_name(city, district, category, i),
                category=category,
                height=Decimal(str(height)),
                longitude=Decimal(str(longitude)),
                latitude=Decimal(str(latitude)),
                address=f"{city}{district}某街道{random.randint(1, 999)}号",
                district=district,
                city=city,
                status=random.choice(["normal", "normal", "normal", "normal", "abnormal", "high_risk"]),
                risk_level=risk_level,
                floors=floors,
                build_year=build_year,
                area=Decimal(str(area)),
                description=f"位于{city}{district}的{category}建筑，建于{build_year}年，高度{height}米，{floors}层",
                is_deleted=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            batch_buildings.append(building)

        # 批量插入
        try:
            session.add_all(batch_buildings)
            session.commit()
            total_created += len(batch_buildings)
            print(f"✅ 已创建 {total_created}/{count} 条建筑数据")
        except Exception as e:
            session.rollback()
            print(f"❌ 批量插入失败: {e}")
            continue

    print(f"✅ 建筑数据生成完成！共创建 {total_created} 条")


def generate_city_events(session: Session, count: int = 100):
    """生成城市事件数据"""
    print(f"开始生成 {count} 条城市事件数据...")

    event_types = ["fire", "flood", "traffic", "construction", "weather", "emergency"]
    cities = generate_chinese_cities()

    events_created = 0

    for i in range(count):
        city_info = random.choice(cities)
        event_type = random.choice(event_types)

        # 事件名称
        event_names = {
            "fire": ["建筑火灾", "仓库火情", "森林火灾预警"],
            "flood": ["暴雨积水", "河流洪水", "城市内涝"],
            "traffic": ["重大交通事故", "道路拥堵", "桥梁检修"],
            "construction": ["地铁施工", "道路改造", "管道维护"],
            "weather": ["极端高温", "寒潮预警", "台风来袭"],
            "emergency": ["突发事故", "公共安全事件", "紧急疏散"],
        }

        event_name = random.choice(event_names[event_type])

        # 生成事件时间（过去30天内的随机时间）
        event_date = datetime.now() - timedelta(days=random.randint(0, 30))

        # 生成位置
        center_lon, center_lat = city_info["center"]
        longitude = round(center_lon + random.uniform(-0.05, 0.05), 8)
        latitude = round(center_lat + random.uniform(-0.05, 0.05), 8)

        city_event = CityEvent(
            id=generate_uuid(),
            event_name=f"{city_info['name']}{event_name}",
            event_type=event_type,
            event_date=event_date,
            longitude=Decimal(str(longitude)),
            latitude=Decimal(str(latitude)),
            radius=Decimal(str(random.randint(100, 5000))),
            severity=random.randint(1, 5),
            status=random.choice(["active", "resolved", "monitoring"]),
            description=f"{event_name}，影响半径{random.randint(100, 5000)}米",
            affected_areas={"city": city_info["name"], "districts": [random.choice(city_info["districts"])]},
            response_actions={
                "evacuation": random.choice([True, False]),
                "emergency_services": random.choice([True, False]),
                "traffic_control": random.choice([True, False])
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        try:
            session.add(city_event)
            session.commit()
            events_created += 1

            if events_created % 10 == 0:
                print(f"✅ 已创建 {events_created}/{count} 条事件数据")
        except Exception as e:
            session.rollback()
            print(f"❌ 创建事件失败: {e}")
            continue

    print(f"✅ 城市事件数据生成完成！共创建 {events_created} 条")


def generate_simulation_records(session: Session, count: int = 200):
    """生成空间模拟记录"""
    print(f"开始生成 {count} 条空间模拟记录...")

    # 获取所有用户ID
    users = session.query(User).all()
    if not users:
        print("⚠️  没有用户，跳过模拟记录生成")
        return

    simulation_types = ["circle", "polygon", "buffer", "viewshed"]
    hazard_types = ["fire", "flood", "earthquake", "typhoon", "traffic"]
    cities = generate_chinese_cities()

    records_created = 0

    for i in range(count):
        user = random.choice(users)
        city_info = random.choice(cities)
        sim_type = random.choice(simulation_types)

        center_lon, center_lat = city_info["center"]
        center_lon += random.uniform(-0.05, 0.05)
        center_lat += random.uniform(-0.05, 0.05)

        # 模拟受影响的建筑
        affected_count = random.randint(0, 100)
        affected_ids = [generate_uuid() for _ in range(min(affected_count, 20))]

        simulation = SimulationRecord(
            id=generate_uuid(),
            user_id=user.id,
            simulation_type=sim_type,
            center_lon=Decimal(str(round(center_lon, 8))),
            center_lat=Decimal(str(round(center_lat, 8))),
            radius=Decimal(str(random.randint(100, 5000))),
            affected_building_ids=affected_ids,
            impact_summary={
                "total": affected_count,
                "by_category": {
                    "commercial": random.randint(0, 30),
                    "residential": random.randint(0, 40),
                    "office": random.randint(0, 20),
                },
                "by_risk_level": {
                    "0": random.randint(50, 80),
                    "1": random.randint(10, 30),
                    "2": random.randint(5, 15),
                },
                "hazard_type": random.choice(hazard_types)
            },
            status=random.choice(["completed", "pending", "failed"]),
            created_at=datetime.now() - timedelta(days=random.randint(0, 60)),
            updated_at=datetime.now()
        )

        try:
            session.add(simulation)
            session.commit()
            records_created += 1

            if records_created % 20 == 0:
                print(f"✅ 已创建 {records_created}/{count} 条模拟记录")
        except Exception as e:
            session.rollback()
            print(f"❌ 创建模拟记录失败: {e}")
            continue

    print(f"✅ 空间模拟记录生成完成！共创建 {records_created} 条")


def generate_analysis_reports(session: Session, count: int = 150):
    """生成分析报告"""
    print(f"开始生成 {count} 条分析报告...")

    # 获取所有用户ID
    users = session.query(User).all()
    if not users:
        print("⚠️  没有用户，跳过报告生成")
        return

    report_types = [
        "risk_assessment",
        "asset_optimization",
        "trend_prediction",
        "emergency_response",
        "urban_planning"
    ]

    cities = generate_chinese_cities()
    ai_models = ["glm-4-flash", "glm-4-plus", "glm-4-air", "qwen-turbo", "deepseek-chat"]

    reports_created = 0

    for i in range(count):
        user = random.choice(users)
        city_info = random.choice(cities)
        report_type = random.choice(report_types)

        # 生成报告标题
        titles = {
            "risk_assessment": f"{city_info['name']}风险评估报告",
            "asset_optimization": f"{city_info['name']}资产优化分析",
            "trend_prediction": f"{city_info['name']}趋势预测",
            "emergency_response": f"{city_info['name']}应急响应预案",
            "urban_planning": f"{city_info['name']}城市规划建议",
        }

        # 生成Markdown内容
        content = f"""# {titles[report_type]}

## 分析时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 分析范围
城市: {city_info['name']}
区域: {random.choice(city_info['districts'])}

## 主要发现
1. 整体风险等级: {random.choice(['低', '中', '高'])}
2. 建筑总数: {random.randint(100, 1000)}
3. 需要关注: {random.randint(5, 50)}

## 详细分析
（此处为自动生成的分析内容）

## 建议
1. 建议加强日常巡查
2. 定期更新应急预案
3. 提升应急响应能力

---
*本报告由AI自动生成*
"""

        report = AnalysisReport(
            id=generate_uuid(),
            user_id=user.id,
            report_type=report_type,
            title=titles[report_type],
            content=content,
            summary={
                "risk_level": random.choice(["low", "medium", "high"]),
                "total_buildings": random.randint(100, 1000),
                "recommendations_count": random.randint(3, 10),
                "priority": random.randint(1, 5)
            },
            visualization_config={
                "actions": [
                    {"type": "fly_to", "params": {"location": city_info["name"]}},
                    {"type": "add_marker", "params": {"count": random.randint(1, 10)}}
                ]
            },
            ai_model=random.choice(ai_models),
            generated_at=datetime.now() - timedelta(days=random.randint(0, 30)),
            created_at=datetime.now()
        )

        try:
            session.add(report)
            session.commit()
            reports_created += 1

            if reports_created % 15 == 0:
                print(f"✅ 已创建 {reports_created}/{count} 条报告")
        except Exception as e:
            session.rollback()
            print(f"❌ 创建报告失败: {e}")
            continue

    print(f"✅ 分析报告生成完成！共创建 {reports_created} 条")


def main():
    """主函数：生成所有demo数据"""
    session = SessionLocal()

    try:
        print("="*60)
        print("智慧城市系统 - Demo数据生成器")
        print("="*60)
        print()

        # 检查是否已有用户，如果没有则创建默认用户
        users_count = session.query(User).count()
        if users_count == 0:
            print("创建默认用户...")
            admin_user = User(
                username="admin",
                email="admin@smartcity.com",
                password_hash=get_password_hash("admin123"),
                full_name="系统管理员",
                phone="13800138000",
                status=1,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(admin_user)
            session.commit()
            print("✅ 默认用户创建成功 (用户名: admin, 密码: admin123)")
        else:
            print(f"✅ 已有 {users_count} 个用户")

        print()
        print("-"*60)

        # 生成建筑数据
        generate_buildings(session, count=1200)
        print()

        # 生成城市事件
        generate_city_events(session, count=100)
        print()

        # 生成模拟记录
        generate_simulation_records(session, count=200)
        print()

        # 生成分析报告
        generate_analysis_reports(session, count=150)
        print()

        print("="*60)
        print("✅ 所有Demo数据生成完成！")
        print("="*60)
        print()
        print("数据统计:")
        print(f"  - 建筑资产: {session.query(Building).count()} 条")
        print(f"  - 城市事件: {session.query(CityEvent).count()} 条")
        print(f"  - 模拟记录: {session.query(SimulationRecord).count()} 条")
        print(f"  - 分析报告: {session.query(AnalysisReport).count()} 条")
        print(f"  - 用户: {session.query(User).count()} 个")
        print()

    except Exception as e:
        print(f"❌ 生成数据失败: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
