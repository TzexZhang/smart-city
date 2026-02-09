/**
 * 建筑可视化配置
 * 根据不同底图类型应用不同的渲染样式
 */
import * as Cesium from 'cesium'

export interface BuildingStyleConfig {
  color: Cesium.Color
  outlineColor: Cesium.Color
  fillAlpha: number
  outlineWidth: number
  extrudedHeightPropertyName?: string
}

export type MapLayerType = 'amap' | 'satellite' | 'terrain' | 'building' | 'realistic' | 'artistic'

/**
 * 建筑类型颜色映射
 */
const BUILDING_TYPE_COLORS: Record<string, Cesium.Color> = {
  commercial: Cesium.Color.fromCssColorString('#FF6B6B'),   // 红色
  office: Cesium.Color.fromCssColorString('#4D96FF'),     // 蓝色
  residential: Cesium.Color.fromCssColorString('#FFD93D'), // 黄色
  industrial: Cesium.Color.fromCssColorString('#A0A0A0'), // 灰色
  public: Cesium.Color.fromCssColorString('#9B59B6'),     // 紫色
  retail: Cesium.Color.fromCssColorString('#F39C12'),     // 橙色
  hotel: Cesium.Color.fromCssColorString('#1ABC9C'),      // 青色
}

/**
 * 根据底图类型获取建筑样式配置
 */
export function getBuildingStyleForMapLayer(mapLayerType: MapLayerType): BuildingStyleConfig {
  const styles: Record<MapLayerType, BuildingStyleConfig> = {
    // 矢量地图：使用鲜艳颜色，高对比度
    amap: {
      color: Cesium.Color.WHITE.withAlpha(0.3),
      outlineColor: Cesium.Color.BLUE,
      fillAlpha: 0.3,
      outlineWidth: 2,
    },

    // 卫星影像：使用半透明白色，突出轮廓
    satellite: {
      color: Cesium.Color.WHITE.withAlpha(0.2),
      outlineColor: Cesium.Color.YELLOW,
      fillAlpha: 0.2,
      outlineWidth: 1.5,
    },

    // 地形图：根据高度使用渐变色
    terrain: {
      color: Cesium.Color.fromCssColorString('#4CAF50').withAlpha(0.4),
      outlineColor: Cesium.Color.WHITE,
      fillAlpha: 0.4,
      outlineWidth: 1,
    },

    // 建筑白模：使用简洁的灰色调
    building: {
      color: Cesium.Color.WHITE.withAlpha(0.5),
      outlineColor: Cesium.Color.BLACK,
      fillAlpha: 0.5,
      outlineWidth: 1,
    },

    // 三维实景：高透明度，不遮挡真实影像
    realistic: {
      color: Cesium.Color.CYAN.withAlpha(0.1),
      outlineColor: Cesium.Color.BLUE.withAlpha(0.3),
      fillAlpha: 0.1,
      outlineWidth: 1,
    },

    // 艺术风格：使用黑色线条，白色填充
    artistic: {
      color: Cesium.Color.WHITE.withAlpha(0.7),
      outlineColor: Cesium.Color.BLACK,
      fillAlpha: 0.7,
      outlineWidth: 2,
    },
  }

  return styles[mapLayerType] || styles.amap
}

/**
 * 根据建筑类型获取颜色
 */
export function getColorByBuildingType(category: string): Cesium.Color {
  return BUILDING_TYPE_COLORS[category] || Cesium.Color.GRAY
}

/**
 * 根据风险等级获取颜色
 */
export function getColorByRiskLevel(riskLevel: number): Cesium.Color {
  const riskColors: Record<number, Cesium.Color> = {
    0: Cesium.Color.GREEN,   // 低风险
    1: Cesium.Color.YELLOW,  // 中低风险
    2: Cesium.Color.ORANGE,  // 中风险
    3: Cesium.Color.RED,     // 高风险
    4: Cesium.Color.PURPLE,  // 极高风险
  }
  return riskColors[riskLevel] || Cesium.Color.GREEN
}

/**
 * 根据建筑高度获取颜色（用于地形图）
 */
export function getColorByHeight(height: number): Cesium.Color {
  if (height < 50) {
    return Cesium.Color.fromCssColorString('#81C784') // 浅绿色 - 低层
  } else if (height < 100) {
    return Cesium.Color.fromCssColorString('#4CAF50') // 绿色 - 中层
  } else if (height < 200) {
    return Cesium.Color.fromCssColorString('#FF9800') // 橙色 - 高层
  } else {
    return Cesium.Color.fromCssColorString('#F44336') // 红色 - 超高层
  }
}

/**
 * 创建建筑 Entity 样式
 */
export function createBuildingStyle(
  building: any,
  mapLayerType: MapLayerType
): Cesium.Entity.ConstructorOptions {
  const baseStyle = getBuildingStyleForMapLayer(mapLayerType)

  // 根据不同策略选择颜色
  let material: Cesium.Color

  switch (mapLayerType) {
    case 'satellite':
    case 'realistic':
      // 卫星和实景：使用基础颜色
      material = baseStyle.color
      break

    case 'terrain':
      // 地形图：根据高度显示颜色
      material = getColorByHeight(building.height || 0)
      break

    case 'artistic':
      // 艺术风格：根据类型显示颜色
      material = getColorByBuildingType(building.category || 'office')
      break

    default:
      // 其他：使用风险等级颜色
      material = getColorByRiskLevel(building.risk_level || 0)
      break
  }

  return {
    name: building.name,
    position: Cesium.Cartesian3.fromDegrees(
      building.longitude,
      building.latitude,
      0
    ),
    // 使用 Box 或 Polygon
    box: {
      dimensions: new Cesium.Cartesian3(
        100, // 宽度
        100, // 深度
        building.height || 50 // 高度
      ),
      material: material,
      outline: true,
      outlineColor: baseStyle.outlineColor,
      outlineWidth: baseStyle.outlineWidth,
    },
  }
}

/**
 * 获取建筑类型的显示名称
 */
export function getBuildingTypeName(category: string): string {
  const names: Record<string, string> = {
    commercial: '商业',
    office: '办公',
    residential: '住宅',
    industrial: '工业',
    public: '公共',
    retail: '零售',
    hotel: '酒店',
  }
  return names[category] || '其他'
}

/**
 * 获取风险等级的显示名称
 */
export function getRiskLevelName(level: number): string {
  const names: Record<number, string> = {
    0: '低风险',
    1: '中低风险',
    2: '中风险',
    3: '高风险',
    4: '极高风险',
  }
  return names[level] || '未知'
}

/**
 * 可视化配置导出
 */
export const VisualizationConfig = {
  // 颜色方案
  colors: BUILDING_TYPE_COLORS,

  // 样式获取函数
  getStyleForMapLayer: getBuildingStyleForMapLayer,
  getColorByType: getColorByBuildingType,
  getColorByRisk: getColorByRiskLevel,
  getColorByHeight: getColorByHeight,

  // Entity 创建
  createBuildingStyle,

  // 显示名称
  getTypeName: getBuildingTypeName,
  getRiskLevelName: getRiskLevelName,
}

export default VisualizationConfig
