"""
生成增强版Demo数据 - 支持多底图可视化
为建筑添加颜色、材质等属性，使其在不同底图上都能突出显示
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
from datetime import datetime
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
print("智慧城市系统 - 增强版Demo数据生成器（支持多底图）")
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

    # 获取用户ID
    cursor.execute("SELECT id FROM tb_users WHERE username='admin' LIMIT 1")
    user_result = cursor.fetchone()
    admin_user_id = user_result[0] if user_result else str(uuid.uuid4())

    # 定义数据生成参数
    BUILDINGS_TARGET = 1200

    # ========== 建筑可视化配置 ==========
    # 为不同建筑类型定义颜色和样式
    BUILDING_STYLES = {
        "commercial": {
            "colors": ["#FF6B6B", "#EE5A6F", "#FF8787"],  # 红色系
            "height_range": (50, 300),
            "transparency": 0.7
        },
        "office": {
            "colors": ["#4D96FF", "#6BCB77", "#4DFF91"],  # 蓝绿色系
            "height_range": (80, 500),
            "transparency": 0.6
        },
        "residential": {
            "colors": ["#FFD93D", "#FFC300", "#FFA500"],  # 黄色系
            "height_range": (20, 150),
            "transparency": 0.5
        },
        "industrial": {
            "colors": ["#A0A0A0", "#808080", "#606060"],  # 灰色系
            "height_range": (15, 80),
            "transparency": 0.8
        },
        "public": {
            "colors": ["#9B59B6", "#8E44AD", "#BB8FCE"],  # 紫色系
            "height_range": (30, 200),
            "transparency": 0.6
        },
        "retail": {
            "colors": ["#F39C12", "#E67E22", "#D68910"],  # 橙色系
            "height_range": (10, 60),
            "transparency": 0.7
        },
        "hotel": {
            "colors": ["#1ABC9C", "#16A085", "#48C9B0"],  # 青色系
            "height_range": (60, 250),
            "transparency": 0.65
        },
    }

    # ========== 生成增强的建筑数据 ==========
    print(f"4. 生成增强版建筑数据 (支持多底图可视化)...")

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

                    # 根据建筑类型生成属性
                    style_config = BUILDING_STYLES[category]
                    height_range = style_config["height_range"]
                    height = random.uniform(*height_range)
                    floors = int(height / 3) if height > 50 else random.randint(1, 20)
                    build_year = random.randint(1990, 2024)
                    area = random.uniform(1000, 100000)
                    risk_level = random.choices([0, 1, 2, 3, 4], weights=[70, 15, 10, 4, 1])[0]

                    # 选择颜色
                    color = random.choice(style_config["colors"])
                    transparency = style_config["transparency"]

                    # 创建 visualization_data JSON（用于前端渲染）
                    visualization_data = {
                        "color": color,
                        "transparency": transparency,
                        "outline": True,
                        "outlineColor": "#000000",
                        "outlineWidth": 2,
                        "extrudedHeight": height,  # 3D拉伸高度
                        "shadows": True
                    }

                    # 扩展描述信息
                    description = f"""位于{city_info['name']}{district}的{category}建筑
建于{build_year}年，高度{height:.1f}米，共{floors}层
建筑面积{area:.0f}平方米
风险等级: {risk_level}
颜色标识: {color} (用于不同底图可视化)"""

                    sql = f"""
                        INSERT INTO tb_buildings
                        (id, name, category, height, longitude, latitude, address,
                         district, city, status, risk_level, floors, build_year,
                         area, description, is_deleted, created_at, updated_at)
                        VALUES (
                            '{bid}', '{building_name}', '{category}', {height:.2f},
                            {lon:.8f}, {lat:.8f}, '{city_info['name']}{district}某街道{random.randint(1, 999)}号',
                            '{district}', '{city_info['name']}', 'normal', {risk_level}, {floors}, {build_year},
                            {area:.2f}, '{description.replace(chr(10), ' ').replace(chr(13), '')}', 0, '{now_str}', '{now_str}'
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

    # ========== 最终验证 ==========
    print("5. 数据验证...")

    cursor.execute("SELECT COUNT(*) FROM tb_users")
    final_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tb_buildings")
    final_buildings = cursor.fetchone()[0]

    # 按类型统计
    cursor.execute("SELECT category, COUNT(*) as count FROM tb_buildings GROUP BY category")
    category_stats = cursor.fetchall()

    # 按城市统计
    cursor.execute("SELECT city, COUNT(*) as count FROM tb_buildings GROUP BY city")
    city_stats = cursor.fetchall()

    print(f"   用户: {final_users} 个")
    print(f"   建筑: {final_buildings} 条")
    print(f"\n   按类型分布:")
    for cat, count in category_stats:
        print(f"     - {cat}: {count} 条")
    print(f"\n   按城市分布:")
    for city, count in city_stats:
        print(f"     - {city}: {count} 条")

    cursor.close()
    conn.close()

    print()
    print("="*70)
    print("✅ 增强版Demo数据生成完成！")
    print("="*70)
    print()
    print("📊 数据特点:")
    print("   - 包含颜色标识，适配不同底图")
    print("   - 完整的3D高度信息")
    print("   - 建筑类型分类（7种类型）")
    print("   - 透明度配置")
    print("   - 风险等级评估")
    print()
    print("🎨 可视化建议:")
    print("   - 矢量地图: 使用颜色区分建筑类型")
    print("   - 卫星影像: 使用透明度突出轮廓")
    print("   - 地形图: 根据高度调整颜色")
    print("   - 建筑白模: 使用标准配色方案")
    print("   - 三维实景: 结合真实纹理")
    print()
    print("📝 默认登录:")
    print("   用户名: admin")
    print("   密码: admin123")
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
