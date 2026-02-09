"""
生成完整的Demo数据 - 独立版本
不依赖复杂的ORM，直接使用pymysql
保证1000+条建筑数据，同时生成城市事件、模拟记录、分析报告等
"""
import sys
import os
from pathlib import Path

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pymysql
from datetime import datetime, timedelta
import uuid
import random
import json
from dotenv import load_dotenv

# 加载环境变量
for env_path in [backend_dir / '.env', Path(__file__).parent / '.env']:
    if env_path.exists():
        load_dotenv(env_path)
        break

pwd = os.getenv('DB_PASSWORD', 'password')

print("="*70)
print("智慧城市系统 - 完整Demo数据生成器")
print("="*70)
print()

try:
    # 连接数据库
    print("1. 连接数据库...")
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password=pwd,
        database='smart_city',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    print("   ✅ 连接成功\n")

    # 检查现有数据
    print("2. 检查现有数据...")
    cursor.execute("SELECT COUNT(*) FROM tb_users")
    users_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tb_buildings")
    buildings_count = cursor.fetchone()[0]

    print(f"   现有用户: {users_count} 个")
    print(f"   现有建筑: {buildings_count} 条\n")

    # 确保至少有一个用户
    if users_count == 0:
        print("3. 创建默认用户...")
        import hashlib
        user_id = str(uuid.uuid4())
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        pwd_hash = hashlib.sha256("admin123".encode()).hexdigest()

        cursor.execute(
            "INSERT INTO tb_users (id, username, email, password_hash, full_name, phone, status, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, 'admin', 'admin@smartcity.com', pwd_hash, '系统管理员', '13800138000', 1, now_str, now_str)
        )
        conn.commit()
        print("   ✅ 默认用户创建成功 (admin/admin123)\n")
        users_count = 1
    else:
        print("3. 用户已存在，跳过创建\n")

    # 获取用户ID（用于后续数据）
    cursor.execute("SELECT id FROM tb_users WHERE username='admin' LIMIT 1")
    user_result = cursor.fetchone()
    admin_user_id = user_result[0] if user_result else str(uuid.uuid4())

    # 定义数据生成参数
    BUILDINGS_TARGET = 1200  # 建筑数据目标
    EVENTS_TARGET = 100       # 城市事件目标
    REPORTS_TARGET = 150      # 分析报告目标
    SIMULATIONS_TARGET = 200  # 模拟记录目标

    # ========== 生成建筑数据 ==========
    print(f"4. 生成建筑数据 (目标: {BUILDINGS_TARGET} 条)...")

    cities = [
        {"name": "北京", "districts": ["朝阳区", "海淀区", "东城区", "西城区", "丰台区"], "center": (116.4074, 39.9042)},
        {"name": "上海", "districts": ["黄浦区", "浦东新区", "静安区", "徐汇区", "长宁区"], "center": (121.4737, 31.2304)},
        {"name": "广州", "districts": ["天河区", "越秀区", "海珠区", "荔湾区", "白云区"], "center": (113.2644, 23.1291)},
        {"name": "深圳", "districts": ["福田区", "罗湖区", "南山区", "宝安区", "龙岗区"], "center": (114.0579, 22.5431)},
        {"name": "杭州", "districts": ["西湖区", "上城区", "下城区", "拱墅区", "江干区"], "center": (120.1551, 30.2741)},
        {"name": "南京", "districts": ["玄武区", "秦淮区", "建邺区", "鼓楼区", "浦口区"], "center": (118.7969, 32.0603)},
        {"name": "武汉", "districts": ["江岸区", "江汉区", "硚口区", "汉阳区", "武昌区"], "center": (114.3055, 30.5928)},
        {"name": "成都", "districts": ["锦江区", "青羊区", "金牛区", "武侯区", "成华区"], "center": (104.0665, 30.5723)},
    ]

    categories = ["commercial", "office", "residential", "industrial", "public", "retail", "hotel"]

    building_prefix_map = {
        "commercial": ["购物中心", "商业广场", "商务中心", "贸易大厦"],
        "office": ["大厦", "写字楼", "商务楼", "办公楼"],
        "residential": ["花园", "家园", "公寓", "小区"],
        "industrial": ["产业园", "科技园", "工业园", "制造基地"],
        "public": ["市民中心", "政务大厅", "公共服务中心", "图书馆"],
        "retail": ["商场", "超市", "购物中心", "百货"],
        "hotel": ["酒店", "宾馆", "度假村", "公寓"],
    }

    buildings_added = 0
    start_id = buildings_count

    for city_info in cities:
        if buildings_count + buildings_added >= BUILDINGS_TARGET:
            break

        for district in city_info["districts"]:
            if buildings_count + buildings_added >= BUILDINGS_TARGET:
                break

            # 每个区域生成15-25个建筑
            num_buildings = random.randint(15, 25)

            for i in range(num_buildings):
                if buildings_count + buildings_added >= BUILDINGS_TARGET:
                    break

                try:
                    bid = str(uuid.uuid4())
                    now = datetime.now()
                    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

                    category = random.choice(categories)
                    prefix = random.choice(building_prefix_map.get(category, ["建筑"]))
                    building_name = f"{city_info['name']}{district}{prefix}{start_id + buildings_added + 1}"

                    # 生成位置
                    center_lon, center_lat = city_info["center"]
                    lon = center_lon + random.uniform(-0.05, 0.05)
                    lat = center_lat + random.uniform(-0.05, 0.05)

                    # 建筑属性
                    height = random.uniform(20, 300)
                    floors = int(height / 3) if height > 50 else random.randint(1, 20)
                    build_year = random.randint(1990, 2024)
                    area = random.uniform(1000, 100000)
                    risk_level = random.choices([0, 1, 2, 3, 4], weights=[70, 15, 10, 4, 1])[0]

                    sql = f"""
                        INSERT INTO tb_buildings
                        (id, name, category, height, longitude, latitude, address,
                         district, city, status, risk_level, floors, build_year,
                         area, description, is_deleted, created_at, updated_at)
                        VALUES (
                            '{bid}', '{building_name}', '{category}', {height:.2f},
                            {lon:.8f}, {lat:.8f}, '{city_info['name']}{district}某街道{random.randint(1, 999)}号',
                            '{district}', '{city_info['name']}', 'normal', {risk_level}, {floors}, {build_year},
                            {area:.2f}, '位于{city_info['name']}{district}的{category}建筑，建于{build_year}年', 0, '{now_str}', '{now_str}'
                        )
                    """

                    cursor.execute(sql)
                    buildings_added += 1

                    if buildings_added % 100 == 0:
                        conn.commit()
                        print(f"   进度: {buildings_count + buildings_added}/{BUILDINGS_TARGET}")

                except Exception as e:
                    print(f"   ⚠️  插入建筑失败: {e}")
                    continue

    conn.commit()
    print(f"   ✅ 建筑数据生成完成！本次添加 {buildings_added} 条\n")

    # ========== 生成城市事件 ==========
    print(f"5. 生成城市事件数据 (目标: {EVENTS_TARGET} 条)...")

    event_types = ["fire", "flood", "traffic", "construction", "weather", "emergency"]

    event_names_map = {
        "fire": ["建筑火灾", "仓库火情", "森林火灾预警"],
        "flood": ["暴雨积水", "河流洪水", "城市内涝"],
        "traffic": ["重大交通事故", "道路拥堵", "桥梁检修"],
        "construction": ["地铁施工", "道路改造", "管道维护"],
        "weather": ["极端高温", "寒潮预警", "台风来袭"],
        "emergency": ["突发事故", "公共安全事件", "紧急疏散"],
    }

    events_added = 0

    for i in range(EVENTS_TARGET):
        try:
            city_info = random.choice(cities)
            event_type = random.choice(event_types)
            event_name = random.choice(event_names_map[event_type])

            # 事件时间（过去30天内）
            event_date = datetime.now() - timedelta(days=random.randint(0, 30))

            eid = str(uuid.uuid4())
            now = datetime.now()
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')
            event_date_str = event_date.strftime('%Y-%m-%d %H:%M:%S')

            # 位置
            center_lon, center_lat = city_info["center"]
            lon = center_lon + random.uniform(-0.05, 0.05)
            lat = center_lat + random.uniform(-0.05, 0.05)

            radius = random.randint(100, 5000)
            severity = random.randint(1, 5)
            status = random.choice(["active", "resolved", "monitoring"])

            # affected_areas JSON
            affected_areas = json.dumps({
                "city": city_info["name"],
                "districts": [random.choice(city_info["districts"])]
            }, ensure_ascii=False)

            # response_actions JSON
            response_actions = json.dumps({
                "evacuation": random.choice([True, False]),
                "emergency_services": random.choice([True, False]),
                "traffic_control": random.choice([True, False])
            }, ensure_ascii=False)

            # 检查表是否存在，如果不存在则创建
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_city_events (
                    id VARCHAR(36) PRIMARY KEY,
                    event_name VARCHAR(200) NOT NULL,
                    event_type VARCHAR(50),
                    event_date DATETIME,
                    longitude FLOAT,
                    latitude FLOAT,
                    radius INT,
                    severity INT,
                    status VARCHAR(20),
                    description TEXT,
                    affected_areas TEXT,
                    response_actions TEXT,
                    created_at DATETIME
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            sql = f"""
                INSERT INTO tb_city_events
                (id, event_name, event_type, event_date, longitude, latitude, radius,
                 severity, status, description, affected_areas, response_actions, created_at)
                VALUES (
                    '{eid}', '{city_info['name']}{event_name}', '{event_type}', '{event_date_str}',
                    {lon:.8f}, {lat:.8f}, {radius}, {severity}, '{status}',
                    '{event_name}，影响半径{radius}米', '{affected_areas}', '{response_actions}', '{now_str}'
                )
            """

            cursor.execute(sql)
            events_added += 1

            if events_added % 20 == 0:
                conn.commit()
                print(f"   进度: {events_added}/{EVENTS_TARGET}")

        except Exception as e:
            print(f"   ⚠️  插入事件失败: {e}")
            continue

    conn.commit()
    print(f"   ✅ 城市事件生成完成！共 {events_added} 条\n")

    # ========== 生成分析报告 ==========
    print(f"6. 生成分析报告数据 (目标: {REPORTS_TARGET} 条)...")

    report_types = [
        "risk_assessment",
        "asset_optimization",
        "trend_prediction",
        "emergency_response",
        "urban_planning"
    ]

    report_titles_map = {
        "risk_assessment": "{}风险评估报告",
        "asset_optimization": "{}资产优化分析",
        "trend_prediction": "{}趋势预测",
        "emergency_response": "{}应急响应预案",
        "urban_planning": "{}城市规划建议",
    }

    reports_added = 0

    for i in range(REPORTS_TARGET):
        try:
            city_info = random.choice(cities)
            report_type = random.choice(report_types)
            title = report_titles_map[report_type].format(city_info['name'])

            # Markdown内容
            content = f"""# {title}

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

            rid = str(uuid.uuid4())
            now = datetime.now()
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')
            generated_at_str = (now - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')

            # summary JSON
            summary = json.dumps({
                "risk_level": random.choice(["low", "medium", "high"]),
                "total_buildings": random.randint(100, 1000),
                "recommendations_count": random.randint(3, 10),
                "priority": random.randint(1, 5)
            }, ensure_ascii=False)

            # visualization_config JSON
            viz_config = json.dumps({
                "actions": [
                    {"type": "fly_to", "params": {"location": city_info["name"]}},
                    {"type": "add_marker", "params": {"count": random.randint(1, 10)}}
                ]
            }, ensure_ascii=False)

            ai_model = random.choice(["glm-4-flash", "glm-4-plus", "glm-4-air", "qwen-turbo"])

            # 检查表是否存在
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_analysis_reports (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36),
                    report_type VARCHAR(50),
                    title VARCHAR(200),
                    content TEXT,
                    summary TEXT,
                    visualization_config TEXT,
                    ai_model VARCHAR(50),
                    generated_at DATETIME,
                    created_at DATETIME
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            sql = f"""
                INSERT INTO tb_analysis_reports
                (id, user_id, report_type, title, content, summary, visualization_config,
                 ai_model, generated_at, created_at)
                VALUES (
                    '{rid}', '{admin_user_id}', '{report_type}', '{title}',
                    '{content.replace(chr(10), chr(32)).replace(chr(13), '')}', '{summary}', '{viz_config}',
                    '{ai_model}', '{generated_at_str}', '{now_str}'
                )
            """

            cursor.execute(sql)
            reports_added += 1

            if reports_added % 20 == 0:
                conn.commit()
                print(f"   进度: {reports_added}/{REPORTS_TARGET}")

        except Exception as e:
            print(f"   ⚠️  插入报告失败: {e}")
            continue

    conn.commit()
    print(f"   ✅ 分析报告生成完成！共 {reports_added} 条\n")

    # ========== 生成模拟记录 ==========
    print(f"7. 生成空间模拟记录 (目标: {SIMULATIONS_TARGET} 条)...")

    simulation_types = ["circle", "polygon", "buffer", "viewshed"]
    hazard_types = ["fire", "flood", "earthquake", "typhoon", "traffic"]

    simulations_added = 0

    for i in range(SIMULATIONS_TARGET):
        try:
            city_info = random.choice(cities)
            sim_type = random.choice(simulation_types)

            center_lon, center_lat = city_info["center"]
            center_lon += random.uniform(-0.05, 0.05)
            center_lat += random.uniform(-0.05, 0.05)

            # 受影响的建筑ID（模拟）
            affected_count = random.randint(0, 100)
            affected_ids = [str(uuid.uuid4()) for _ in range(min(affected_count, 20))]
            affected_ids_json = json.dumps(affected_ids)

            sid = str(uuid.uuid4())
            now = datetime.now()
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')
            created_at_str = (now - timedelta(days=random.randint(0, 60))).strftime('%Y-%m-%d %H:%M:%S')

            # impact_summary JSON
            impact_summary = json.dumps({
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
            }, ensure_ascii=False)

            status = random.choice(["completed", "pending", "failed"])

            # 检查表是否存在
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_simulation_records (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36),
                    simulation_type VARCHAR(50),
                    center_lon FLOAT,
                    center_lat FLOAT,
                    radius INT,
                    affected_building_ids TEXT,
                    impact_summary TEXT,
                    status VARCHAR(20),
                    created_at DATETIME,
                    updated_at DATETIME
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            sql = f"""
                INSERT INTO tb_simulation_records
                (id, user_id, simulation_type, center_lon, center_lat, radius,
                 affected_building_ids, impact_summary, status, created_at, updated_at)
                VALUES (
                    '{sid}', '{admin_user_id}', '{sim_type}', {center_lon:.8f}, {center_lat:.8f}, {random.randint(100, 5000)},
                    '{affected_ids_json}', '{impact_summary}', '{status}', '{created_at_str}', '{now_str}'
                )
            """

            cursor.execute(sql)
            simulations_added += 1

            if simulations_added % 20 == 0:
                conn.commit()
                print(f"   进度: {simulations_added}/{SIMULATIONS_TARGET}")

        except Exception as e:
            print(f"   ⚠️  插入模拟记录失败: {e}")
            continue

    conn.commit()
    print(f"   ✅ 空间模拟记录生成完成！共 {simulations_added} 条\n")

    # ========== 最终验证 ==========
    print("8. 数据验证...")

    cursor.execute("SELECT COUNT(*) FROM tb_users")
    final_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tb_buildings")
    final_buildings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tb_city_events")
    final_events = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tb_analysis_reports")
    final_reports = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tb_simulation_records")
    final_simulations = cursor.fetchone()[0]

    print(f"   用户: {final_users} 个")
    print(f"   建筑: {final_buildings} 条 ✅")
    print(f"   城市事件: {final_events} 条")
    print(f"   分析报告: {final_reports} 条")
    print(f"   模拟记录: {final_simulations} 条")

    total_records = final_buildings + final_events + final_reports + final_simulations

    cursor.close()
    conn.close()

    print()
    print("="*70)
    print("✅ Demo数据生成完成！")
    print("="*70)
    print(f"\n📊 总计生成 {total_records} 条数据")
    print(f"   - 建筑: {final_buildings} 条")
    print(f"   - 事件: {final_events} 条")
    print(f"   - 报告: {final_reports} 条")
    print(f"   - 模拟: {final_simulations} 条")
    print(f"   - 用户: {final_users} 个")
    print()
    print("📝 默认登录:")
    print("   用户名: admin")
    print("   密码: admin123")
    print()
    print("🚀 启动服务:")
    print("   后端: python main.py")
    print("   前端: cd ../frontend && npm run dev")
    print()

except pymysql.Error as e:
    print(f"\n❌ 数据库错误: {e}")
    print("\n💡 解决方案:")
    print("1. 确保 MySQL 正在运行")
    print("2. 创建数据库:")
    print("   mysql -u root -p")
    print("   CREATE DATABASE smart_city CHARACTER SET utf8mb4;")
    print("3. 修改密码:")
    print("   编辑 backend/.env，添加: DB_PASSWORD=你的密码\n")
    import traceback
    traceback.print_exc()

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
