"""
中国主要省会城市3D模型数据配置
基于开源数据源：CMAB、GABLE、Open3Dhk等
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# ============ 中国省会城市3D数据源配置 ============

CHINA_3D_DATA_SOURCES = {
    # 香港特别行政区 - 高质量开源数据
    "Hong Kong": {
        "name_en": "Hong Kong",
        "name_zh": "香港",
        "source": "Open3Dhk",
        "url": "https://3d.map.gov.hk/",
        "api": "https://portal.csdi.gov.hk/csdi-webpage/apidoc/3d-spatial-data-api",
        "coverage": "全境覆盖",
        "resolution": "LoD1, LoD3",
        "formats": ["3D Tiles", "CityGML", "IFC"],
        "download": "https://data.gov.hk/en-data/dataset/hk-landsd-openmap-development-hkms-digital-3d-bit00",
        "cesium_asset_id": None,  # 需要自己托管
        "center": [114.1694, 22.3193],
        "description": "香港特区政府提供的完整3D空间数据，可下载使用"
    },

    # 北京 - 使用CMAB数据集
    "Beijing": {
        "name_en": "Beijing",
        "name_zh": "北京",
        "source": "CMAB + GABLE",
        "dataset": "China Multi-Attribute Building Dataset",
        "url": "https://figshare.com/articles/dataset/CMAB-The_World_s_First_National-Scale_Multi-Attribute_Building_Dataset/27992417",
        "paper": "https://www.nature.com/articles/s41597-025-04730-5",
        "coverage": "全市覆盖",
        "building_count": "数百万栋",
        "attributes": ["height", "type", "year", "orientation", "rooftop"],
        "center": [116.4074, 39.9042],
        "description": "首个国家级多属性建筑数据集，包含31万栋建筑的详细属性"
    },

    # 上海
    "Shanghai": {
        "name_en": "Shanghai",
        "name_zh": "上海",
        "source": "CMAB + GABLE",
        "dataset": "China Multi-Attribute Building Dataset",
        "url": "https://github.com/AICyberTeam/GABLE",
        "coverage": "全市覆盖",
        "resolution": "0.5-0.8m",
        "center": [121.4737, 31.2304],
        "description": "基于北京-3号卫星影像生成的精细3D建筑模型"
    },

    # 广州
    "Guangzhou": {
        "name_en": "Guangzhou",
        "name_zh": "广州",
        "source": "CMAB",
        "dataset": "China Multi-Attribute Building Dataset",
        "coverage": "全市覆盖",
        "center": [113.2644, 23.1291],
        "description": "华南地区中心城市，完整建筑数据"
    },

    # 深圳
    "Shenzhen": {
        "name_en": "Shenzhen",
        "name_zh": "深圳",
        "source": "CMAB + GABLE",
        "dataset": "Fine-grained 3D Building Model",
        "coverage": "全市覆盖",
        "resolution": "0.5-0.8m",
        "center": [114.0579, 22.5431],
        "description": "科技创新中心，高精度3D模型"
    },

    # 其他省会城市配置
    "Chengdu": {
        "name_en": "Chengdu",
        "name_zh": "成都",
        "source": "CMAB",
        "center": [104.0665, 30.5723],
        "description": "西南地区中心城市"
    },

    "Hangzhou": {
        "name_en": "Hangzhou",
        "name_zh": "杭州",
        "source": "CMAB",
        "center": [120.1551, 30.2741],
        "description": "长江三角洲中心城市"
    },

    "Wuhan": {
        "name_en": "Wuhan",
        "name_zh": "武汉",
        "source": "CMAB",
        "center": [114.3055, 30.5928],
        "description": "华中地区中心城市"
    },

    "Xi'an": {
        "name_en": "Xi'an",
        "name_zh": "西安",
        "source": "CMAB",
        "center": [108.9398, 34.3416],
        "description": "西北地区中心城市，古都"
    },

    "Nanjing": {
        "name_en": "Nanjing",
        "name_zh": "南京",
        "source": "CMAB",
        "center": [118.7969, 32.0603],
        "description": "江苏省会，长三角重要城市"
    },
}

# ============ Cesium OSM Buildings 覆盖列表 ============

CESIUM_OSM_COVERAGE = {
    "China": {
        "coverage_level": "Limited",
        "notes": "OSM data quality in China is notably inadequate compared to other regions",
        "asset_id": 96188,  # Cesium ion asset ID for OSM Buildings
        "recommended": False,
        "alternative": "Use CMAB or domestic map providers"
    }
}

# ============ 国内地图服务API（可作为替代） ============

DOMESTIC_MAP_APIS = {
    "Baidu Maps": {
        "name": "百度地图",
        "url": "https://developer.baidu.com/map/",
        "features": ["3D建筑", "室内导航", "多楼层支持"],
        "coverage": "600+城市",
        "api_type": "REST API",
        "cesium_compatible": True,
        "description": "百度提供详细的3D建筑模型"
    },
    "Amap/Gaode": {
        "name": "高德地图",
        "url": "https://lbs.amap.com/",
        "features": ["3D建筑", "AR导航", "360+城市"],
        "api_type": "JavaScript API",
        "cesium_compatible": True,
        "description": "高德地图3D建筑API"
    },
    "Tencent Maps": {
        "name": "腾讯地图",
        "url": "https://lbs.qq.com/",
        "features": ["2D/3D切换", "3D建筑"],
        "api_type": "JavaScript SDK",
        "cesium_compatible": True,
        "description": "腾讯地图3D SDK"
    }
}

# ============ 数据下载和转换指南 ============

DATA_CONVERSION_GUIDE = {
    "from_CMAB": {
        "step1": "下载数据",
        "url": "https://figshare.com/articles/dataset/27992417",
        "format": "Shapefile / GeoPackage",
        "step2": "使用Py3DTiles转换为3D Tiles",
        "tool": "https://github.com/Oslandia/py3dtilers",
        "command": "py3dtiles convert input.shp output.3dtiles --lod 1",
        "step3": "加载到Cesium",
        "code": "viewer.scene.primitives.add(Cesium.Cesium3DTileset.fromUrl('output.3dtiles'))"
    },
    "from_GABLE": {
        "step1": "克隆仓库",
        "url": "https://github.com/AICyberTeam/GABLE",
        "step2": "使用内置查看器预览",
        "step3": "导出为OBJ或CityGML格式",
        "step4": "使用Py3DTiles或GDAL转换为3D Tiles"
    },
    "from_Open3Dhk": {
        "step1": "访问数据门户",
        "url": "https://3d.map.gov.hk/",
        "step2": "注册并下载数据",
        "formats": ["3D Tiles", "CityGML", "IFC"],
        "step3": "直接加载到Cesium",
        "code": "viewer.scene.primitives.add(await Cesium.Cesium3DTileset.fromUrl('data.3dtiles'))"
    }
}

# ============ 推荐的数据获取优先级 ============

DATA_PRIORITY = [
    "1. Open3Dhk (香港) - 开放API，高质量",
    "2. CMAB数据集 (全国) - 最全面，学术开源",
    "3. GABLE (精细) - GitHub可用，高分辨率",
    "4. Cesium OSM Buildings - 全球覆盖但中国质量有限",
    "5. 国内地图API - 百度/高德/腾讯（需申请key）"
]

# ============ 使用示例 ============

def get_city_data_config(city_name: str):
    """获取城市数据配置"""
    city_key = city_name.replace("市", "").replace("省", "")
    return CHINA_3D_DATA_SOURCES.get(city_key, {
        "name_en": city_name,
        "name_zh": city_name,
        "source": "CMAB",
        "center": [0, 0],
        "description": "请配置该城市的数据源"
    })

def print_all_sources():
    """打印所有可用的数据源"""
    print("="*70)
    print("中国城市3D模型数据源列表")
    print("="*70)
    print()

    for city_key, config in CHINA_3D_DATA_SOURCES.items():
        print(f"🏙️  {config['name_zh']} ({config['name_en']})")
        print(f"   数据源: {config['source']}")
        print(f"   中心坐标: {config['center']}")
        print(f"   说明: {config['description']}")
        if 'url' in config:
            print(f"   数据地址: {config['url']}")
        print()

    print("="*70)
    print("数据转换工具推荐")
    print("="*70)
    print()
    print("🔧 Py3DTiles - https://github.com/Oslandia/py3dtilers")
    print("   支持格式: OBJ, GeoJSON, IFC, CityGML → 3D Tiles")
    print("   命令: pip install py3dtiles")
    print()
    print("🔧 Cesium 3D Tiles Tools - https://github.com/CesiumGS/3d-tiles-tools")
    print("   官方工具集，用于3D Tiles处理")
    print()

if __name__ == "__main__":
    print_all_sources()
