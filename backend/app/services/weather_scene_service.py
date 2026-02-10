"""
天气场景组合Action
当用户查询城市天气时，自动执行：飞行 → 获取天气 → 应用效果
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


async def execute_weather_scene_action(
    city: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> Dict[str, Any]:
    """
    执行天气场景组合动作

    流程：
    1. 飞到目标城市
    2. 获取实时天气
    3. 应用天气效果

    Args:
        city: 城市名称
        latitude: 纬度（可选）
        longitude: 经度（可选）

    Returns:
        组合动作列表，供前端顺序执行
    """
    logger.info(f"🎬 生成天气场景动作: city={city}")

    # 城市坐标映射
    city_coords = {
        '北京': {'longitude': 116.4074, 'latitude': 39.9042},
        '上海': {'longitude': 121.4737, 'latitude': 31.2304},
        '广州': {'longitude': 113.2644, 'latitude': 23.1291},
        '深圳': {'longitude': 114.0579, 'latitude': 22.5431},
        '香港': {'longitude': 114.1694, 'latitude': 22.3193},
        '西安': {'longitude': 108.9398, 'latitude': 34.3416},
        '成都': {'longitude': 104.0668, 'latitude': 30.5728},
        '杭州': {'longitude': 120.1551, 'latitude': 30.2741},
        '武汉': {'longitude': 114.3055, 'latitude': 30.5928},
        '南京': {'longitude': 118.7969, 'latitude': 32.0603},
        'Beijing': {'longitude': 116.4074, 'latitude': 39.9042},
        'Shanghai': {'longitude': 121.4737, 'latitude': 31.2304},
        'Guangzhou': {'longitude': 113.2644, 'latitude': 23.1291},
        'Shenzhen': {'longitude': 114.0579, 'latitude': 22.5431},
        'Hong Kong': {'longitude': 114.1694, 'latitude': 22.3193},
        "Xi'an": {'longitude': 108.9398, 'latitude': 34.3416},
        'Chengdu': {'longitude': 104.0668, 'latitude': 30.5728},
        'Hangzhou': {'longitude': 120.1551, 'latitude': 30.2741},
    }

    # 获取坐标
    coords = city_coords.get(city)
    if not coords and not (latitude and longitude):
        # 尝试模糊匹配
        for key, value in city_coords.items():
            if city.lower() in key.lower() or key.lower() in city.lower():
                coords = value
                city = key
                break

    if not coords:
        coords = {'longitude': longitude, 'latitude': latitude}

    if not coords.get('longitude') or not coords.get('latitude'):
        return {
            "error": f"无法确定城市坐标: {city}"
        }

    # 生成组合动作序列
    actions = [
        # 步骤1: 飞到目标城市
        {
            "type": "camera_flyTo",
            "description": f"飞往{city}",
            "parameters": {
                "longitude": coords['longitude'],
                "latitude": coords['latitude'],
                "height": 5000,
                "duration": 3.0,
                "pitch": -30
            },
            "wait_for_completion": True  # 等待飞行完成
        },
        # 步骤2: 获取并应用天气
        {
            "type": "get_weather",
            "description": f"获取{city}天气并应用效果",
            "parameters": {
                "city": city,
                "latitude": coords['latitude'],
                "longitude": coords['longitude']
            },
            "delay": 1000  # 飞行完成后等待1秒
        }
    ]

    logger.info(f"✅ 生成 {len(actions)} 个动作")
    return {
        "status": "success",
        "actions": actions,
        "city": city,
        "coords": coords,
        "description": f"将飞往{city}，获取天气数据，并应用对应的天气效果"
    }


# 预定义的天气场景
WEATHER_SCENES = {
    "雨天": {
        "condition": "rain",
        "intensity": 0.7,
        "is_day": False,
        "description": "雨夜场景"
    },
    "雪天": {
        "condition": "snow",
        "intensity": 0.5,
        "is_day": True,
        "description": "雪天场景"
    },
    "雾天": {
        "condition": "fog",
        "intensity": 0.8,
        "is_day": False,
        "description": "雾夜场景"
    },
    "晴天": {
        "condition": "clear",
        "intensity": 0,
        "is_day": True,
        "description": "晴天场景"
    },
    "雷雨": {
        "condition": "rain",
        "intensity": 1.0,
        "is_day": False,
        "description": "雷雨夜场景"
    }
}


def get_weather_scene(scene_name: str) -> Optional[Dict[str, Any]]:
    """获取预定义的天气场景"""
    return WEATHER_SCENES.get(scene_name)
