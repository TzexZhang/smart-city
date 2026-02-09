/**
 * AI Actions 执行器
 * 解析并执行 AI 返回的地图控制指令
 */

import * as Cesium from 'cesium'

export interface AIAction {
  type: 'fly_to' | 'add_marker' | 'show_layer' | 'hide_layer' | 'set_time' | 'zoom_in' | 'zoom_out'
  params: any
}

export class AIActionExecutor {
  private viewer: Cesium.Viewer
  private entities: Map<string, Cesium.Entity> = new Map()

  constructor(viewer: Cesium.Viewer) {
    this.viewer = viewer
  }

  /**
   * 执行单个 action
   */
  async executeAction(action: AIAction): Promise<boolean> {
    try {
      switch (action.type) {
        case 'fly_to':
          return await this.flyTo(action.params)

        case 'add_marker':
          return this.addMarker(action.params)

        case 'show_layer':
          return this.showLayer(action.params)

        case 'hide_layer':
          return this.hideLayer(action.params)

        case 'set_time':
          return this.setTime(action.params)

        case 'zoom_in':
          return this.zoomIn(action.params)

        case 'zoom_out':
          return this.zoomOut(action.params)

        default:
          console.warn('未知的 action 类型:', action.type)
          return false
      }
    } catch (error) {
      console.error('执行 action 失败:', error)
      return false
    }
  }

  /**
   * 批量执行 actions
   */
  async executeActions(actions: AIAction[]): Promise<{ success: number; failed: number }> {
    let success = 0
    let failed = 0

    for (const action of actions) {
      const result = await this.executeAction(action)
      if (result) {
        success++
      } else {
        failed++
      }
    }

    return { success, failed }
  }

  /**
   * 飞到指定位置
   */
  private async flyTo(params: {
    longitude?: number
    latitude?: number
    height?: number
    duration?: number
    locationName?: string
  }): Promise<boolean> {
    try {
      let destination: Cesium.Cartesian3

      // 如果有经纬度，直接使用
      if (params.longitude !== undefined && params.latitude !== undefined) {
        const height = params.height || 1000
        destination = Cesium.Cartesian3.fromDegrees(
          params.longitude,
          params.latitude,
          height
        )

        this.viewer.camera.flyTo({
          destination: destination,
          duration: params.duration || 2,
          orientation: {
            heading: Cesium.Math.toRadians(0),
            pitch: Cesium.Math.toRadians(-45),
            roll: 0.0
          }
        })
        return new Promise((resolve) => {
          setTimeout(() => resolve(true), (params.duration || 2) * 1000)
        })
      }

      // 如果有地名，尝试查找（这里需要扩展地名到坐标的映射）
      if (params.locationName) {
        return this.flyToLocationByName(params.locationName, params.duration)
      }

      return false
    } catch (error) {
      console.error('flyTo 失败:', error)
      return false
    }
  }

  /**
   * 根据地名飞到指定位置
   */
  private async flyToLocationByName(locationName: string, duration: number = 2): Promise<boolean> {
    // 主要城市坐标映射
    const cityCoordinates: Record<string, { lon: number; lat: number; height: number }> = {
      '北京': { lon: 116.3974, lat: 39.9093, height: 50000 },
      '上海': { lon: 121.4737, lat: 31.2304, height: 50000 },
      '纽约': { lon: -74.0060, lat: 40.7128, height: 50000 },
      '伦敦': { lon: -0.1276, lat: 51.5074, height: 50000 },
      '东京': { lon: 139.6917, lat: 35.6895, height: 50000 },
      '巴黎': { lon: 2.3522, lat: 48.8566, height: 50000 },
      '中国': { lon: 116.3974, lat: 39.9093, height: 2000 },
    }

    // 模糊匹配
    for (const [name, coords] of Object.entries(cityCoordinates)) {
      if (locationName.includes(name) || name.includes(locationName)) {
        this.viewer.camera.flyTo({
          destination: Cesium.Cartesian3.fromDegrees(coords.lon, coords.lat, coords.height),
          duration: duration,
          orientation: {
            heading: Cesium.Math.toRadians(0),
            pitch: Cesium.Math.toRadians(-45),
            roll: 0.0
          }
        })
        return new Promise((resolve) => {
          setTimeout(() => resolve(true), duration * 1000)
        })
      }
    }

    console.warn('未找到位置:', locationName)
    return false
  }

  /**
   * 添加标记
   */
  private addMarker(params: {
    longitude: number
    latitude: number
    label?: string
    color?: string
  }): boolean {
    try {
      const id = `marker_${Date.now()}`
      const entity = this.viewer.entities.add({
        name: params.label || 'Marker',
        position: Cesium.Cartesian3.fromDegrees(params.longitude, params.latitude, 0),
        point: {
          pixelSize: 12,
          color: Cesium.Color.fromCssColorString(params.color || '#ff0000'),
          outlineColor: Cesium.Color.WHITE,
          outlineWidth: 2,
        },
        label: params.label ? {
          text: params.label,
          font: '14px sans-serif',
          fillColor: Cesium.Color.WHITE,
          backgroundColor: Cesium.Color.BLACK.withAlpha(0.7),
          backgroundPadding: new Cesium.Cartesian2(8, 6),
          showBackground: true,
          pixelOffset: new Cesium.Cartesian2(15, -15),
        } : undefined,
      })

      this.entities.set(id, entity)
      return true
    } catch (error) {
      console.error('addMarker 失败:', error)
      return false
    }
  }

  /**
   * 显示图层
   */
  private showLayer(params: { layerName: string }): boolean {
    // 根据图层名称显示对应的图层
    // 这里需要扩展以支持具体的图层控制
    console.log('显示图层:', params.layerName)
    return true
  }

  /**
   * 隐藏图层
   */
  private hideLayer(params: { layerName: string }): boolean {
    console.log('隐藏图层:', params.layerName)
    return true
  }

  /**
   * 设置时间
   */
  private setTime(params: { time: string }): boolean {
    // 设置场景时间，影响光照效果
    console.log('设置时间:', params.time)
    return true
  }

  /**
   * 放大
   */
  private zoomIn(params: { amount?: number } = {}): boolean {
    const zoomAmount = params.amount || 0.5
    const camera = this.viewer.camera
    camera.zoomIn(camera.positionCartographic.height * zoomAmount)
    return true
  }

  /**
   * 缩小
   */
  private zoomOut(params: { amount?: number } = {}): boolean {
    const zoomAmount = params.amount || 0.5
    const camera = this.viewer.camera
    camera.zoomOut(camera.positionCartographic.height * zoomAmount)
    return true
  }

  /**
   * 清除所有标记
   */
  clearAllMarkers(): void {
    this.entities.forEach((entity) => {
      this.viewer.entities.remove(entity)
    })
    this.entities.clear()
  }
}
