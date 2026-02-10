"""
天气MCP客户端
获取实时天气数据，用于驱动Cesium场景的天气效果
"""

from typing import Dict, Any, Optional
import logging
import httpx
from datetime import datetime
from .base_client import MCPClientBase
from .config import MCPServerConfig

logger = logging.getLogger(__name__)


class OpenWeatherMapClient(MCPClientBase):
    """OpenWeatherMap天气客户端"""

    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.endpoint or "https://api.openweathermap.org/data/2.5"
        self.client = httpx.AsyncClient(timeout=10)

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用天气工具"""
        try:
            if tool_name == "get_current_weather":
                return await self.get_current_weather(
                    parameters.get("city"),
                    parameters.get("latitude"),
                    parameters.get("longitude")
                )
            elif tool_name == "get_weather_by_coordinates":
                return await self.get_weather_by_coordinates(
                    parameters.get("latitude"),
                    parameters.get("longitude")
                )
            elif tool_name == "get_weather_forecast":
                return await self.get_weather_forecast(
                    parameters.get("city"),
                    parameters.get("latitude"),
                    parameters.get("longitude"),
                    parameters.get("days", 1)
                )
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"天气API调用失败: {e}")
            return {"error": str(e)}

    async def list_tools(self) -> list:
        """列出可用的天气工具"""
        return [
            {
                "name": "get_current_weather",
                "description": "获取指定城市的当前天气",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称（如：Beijing, Shanghai, London）"
                        },
                        "latitude": {"type": "number", "description": "纬度（与city二选一）"},
                        "longitude": {"type": "number", "description": "经度（与city二选一）"}
                    }
                }
            },
            {
                "name": "get_weather_by_coordinates",
                "description": "根据坐标获取天气",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"}
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "get_weather_forecast",
                "description": "获取天气预报",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "days": {"type": "number", "default": 1}
                    }
                }
            }
        ]

    async def get_current_weather(
        self,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        获取当前天气

        Args:
            city: 城市名称
            latitude: 纬度
            longitude: 经度

        Returns:
            天气数据
        """
        try:
            # 如果没有提供API key，返回模拟数据
            if not self.api_key:
                return self._get_mock_weather(city, latitude, longitude)

            # 构建请求参数
            params = {
                "appid": self.api_key,
                "units": "metric"
            }

            if city:
                params["q"] = city
            elif latitude and longitude:
                params["lat"] = latitude
                params["lon"] = longitude
            else:
                return {"error": "请提供城市名称或坐标"}

            # 发送请求
            url = f"{self.base_url}/weather"
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # 解析并转换为我们需要的格式
            weather_data = self._parse_weather_data(data)

            logger.info(f"✅ 获取天气数据成功: {weather_data.get('city')}")
            return weather_data

        except httpx.HTTPError as e:
            logger.warning(f"⚠️ 天气API请求失败: {e}，使用模拟数据")
            return self._get_mock_weather(city, latitude, longitude)
        except Exception as e:
            logger.error(f"❌ 获取天气失败: {e}")
            return {
                "error": str(e),
                "fallback": self._get_mock_weather(city, latitude, longitude)
            }

    async def get_weather_by_coordinates(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """根据坐标获取天气"""
        return await self.get_current_weather(None, latitude, longitude)

    async def get_weather_forecast(
        self,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        days: int = 1
    ) -> Dict[str, Any]:
        """获取天气预报"""
        try:
            if not self.api_key:
                return self._get_mock_forecast(city, latitude, longitude, days)

            params = {
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 每天8次预报（3小时间隔）
            }

            if city:
                params["q"] = city
            elif latitude and longitude:
                params["lat"] = latitude
                params["lon"] = longitude
            else:
                return {"error": "请提供城市名称或坐标"}

            url = f"{self.base_url}/forecast"
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # 解析预报数据
            forecast_data = []
            for item in data.get("list", []):
                forecast_data.append({
                    "datetime": datetime.fromtimestamp(item.get("dt", 0)).isoformat(),
                    "temp": item["main"].get("temp"),
                    "feels_like": item["main"].get("feels_like"),
                    "condition": item["weather"][0].get("main") if item.get("weather") else "Clear",
                    "description": item["weather"][0].get("description") if item.get("weather") else "",
                    "humidity": item["main"].get("humidity"),
                    "wind_speed": item.get("wind", {}).get("speed"),
                })

            return {
                "status": "success",
                "city": data.get("city", {}).get("name"),
                "country": data.get("city", {}).get("country"),
                "forecast": forecast_data
            }

        except Exception as e:
            logger.error(f"获取天气预报失败: {e}")
            return self._get_mock_forecast(city, latitude, longitude, days)

    def _parse_weather_data(self, data: dict) -> Dict[str, Any]:
        """解析天气API返回的数据"""
        weather_info = data.get("weather", [{}])[0]
        main_data = data.get("main", {})
        wind_data = data.get("wind", {})
        sys_data = data.get("sys", {})

        # 映射天气状况到我们的标准类型
        condition = weather_info.get("main", "Clear")
        cesium_condition = self._map_to_cesium_condition(condition)

        return {
            "status": "success",
            "city": data.get("name"),
            "country": sys_data.get("country"),
            "latitude": data.get("coord", {}).get("lat"),
            "longitude": data.get("coord", {}).get("lon"),
            "temperature": main_data.get("temp"),
            "feels_like": main_data.get("feels_like"),
            "humidity": main_data.get("humidity"),
            "pressure": main_data.get("pressure"),
            "condition": condition,
            "description": weather_info.get("description"),
            "cesium_condition": cesium_condition,
            "wind_speed": wind_data.get("speed"),
            "wind_direction": wind_data.get("deg"),
            "visibility": data.get("visibility", 10000),
            "clouds": data.get("clouds", {}).get("all"),
            "is_day": self._is_daytime(
                data.get("coord", {}).get("lat"),
                data.get("coord", {}).get("lon"),
                sys_data.get("sunrise"),
                sys_data.get("sunset")
            ),
            "timestamp": datetime.now().isoformat()
        }

    def _map_to_cesium_condition(self, condition: str) -> str:
        """将天气API的condition映射到Cesium支持的条件"""
        condition_map = {
            "Clear": "clear",
            "Clouds": "cloudy",
            "Rain": "rain",
            "Drizzle": "rain",
            "Thunderstorm": "rain",
            "Snow": "snow",
            "Mist": "fog",
            "Fog": "fog",
            "Haze": "fog",
            "Smoke": "fog",
            "Dust": "fog",
            "Sand": "fog",
            "Ash": "fog",
            "Squall": "rain",
            "Tornado": "rain"
        }
        return condition_map.get(condition, "clear")

    def _is_daytime(
        self,
        lat: Optional[float],
        lon: Optional[float],
        sunrise: Optional[int],
        sunset: Optional[int]
    ) -> bool:
        """判断是否是白天"""
        if not lat or not lon:
            # 简单判断：当前时间是否在6-18点
            current_hour = datetime.now().hour
            return 6 <= current_hour < 18

        if sunrise and sunset:
            current_time = datetime.now().timestamp()
            return sunrise <= current_time < sunset

        return True

    def _get_mock_weather(
        self,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """生成模拟天气数据（用于演示或API不可用时）"""
        import random

        current_hour = datetime.now().hour
        is_day = 6 <= current_hour < 18

        # 根据时间生成天气
        conditions = ["Clear", "Clouds", "Rain", "Snow", "Fog"]
        weights = [0.3, 0.3, 0.2, 0.1, 0.1]

        condition = random.choices(conditions, weights=weights)[0]

        return {
            "status": "success",
            "city": city or "Unknown",
            "country": "CN",
            "latitude": latitude or 39.9042,
            "longitude": longitude or 116.4074,
            "temperature": random.uniform(15, 30),
            "feels_like": random.uniform(15, 30),
            "humidity": random.uniform(40, 90),
            "pressure": 1013,
            "condition": condition,
            "description": f"Simulated {condition.lower()} weather",
            "cesium_condition": self._map_to_cesium_condition(condition),
            "wind_speed": random.uniform(0, 10),
            "wind_direction": random.uniform(0, 360),
            "visibility": random.uniform(5000, 10000),
            "clouds": random.uniform(0, 100),
            "is_day": is_day,
            "timestamp": datetime.now().isoformat(),
            "note": "这是模拟数据，请配置OpenWeatherMap API Key获取真实天气"
        }

    def _get_mock_forecast(
        self,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        days: int = 1
    ) -> Dict[str, Any]:
        """生成模拟预报数据"""
        forecast = []
        for i in range(days * 8):
            import random
            from datetime import timedelta

            future_time = datetime.now() + timedelta(hours=i * 3)
            condition = random.choice(["Clear", "Clouds", "Rain", "Snow"])

            forecast.append({
                "datetime": future_time.isoformat(),
                "temp": random.uniform(15, 30),
                "feels_like": random.uniform(15, 30),
                "condition": condition,
                "description": condition.lower(),
                "humidity": random.uniform(40, 90),
                "wind_speed": random.uniform(0, 10),
            })

        return {
            "status": "success",
            "city": city or "Unknown",
            "forecast": forecast,
            "note": "这是模拟预报数据"
        }

    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()
