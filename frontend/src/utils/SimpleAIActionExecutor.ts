/**
 * AI指令执行器 - 简化版
 * 避免复杂的类型问题，专注于功能实现
 */
import * as Cesium from 'cesium'

export interface AIAction {
  type: string
  description: string
  execute: (viewer: Cesium.Viewer) => Promise<ActionResult>
}

export interface ActionResult {
  success: boolean
  message: string
  data?: any
}

export class SimpleAIActionExecutor {
  private viewer: Cesium.Viewer

  constructor(viewer: Cesium.Viewer) {
    this.viewer = viewer
  }

  /**
   * 执行AI返回的actions
   */
  async executeActions(actions: Array<any>): Promise<ActionResult> {
    console.log('📋 收到AI指令:', actions)

    let successCount = 0
    let failedCount = 0
    const results: string[] = []

    for (const actionConfig of actions) {
      try {
        const actionType = actionConfig.type
        const params = actionConfig.parameters || {}

        console.log(`🎯 执行指令: ${actionType}`)
        console.log('   参数:', params)

        let result: ActionResult

        // 根据指令类型执行
        switch (actionType) {
          case 'camera_flyTo':
            result = await this.executeFlyTo(params)
            break

          case 'camera_setView':
            result = await this.executeSetView(params)
            break

          case 'building_query':
            result = await this.executeBuildingQuery(params)
            break

          case 'layer_switch':
            result = await this.executeLayerSwitch(params)
            break

          case 'reset':
            result = await this.executeReset()
            break

          default:
            result = {
              success: false,
              message: `不支持的指令类型: ${actionType}`
            }
        }

        if (result.success) {
          successCount++
          results.push(`✅ ${result.message}`)
        } else {
          failedCount++
          results.push(`❌ ${result.message}`)
        }

      } catch (error: any) {
        console.error(`❌ 指令执行失败:`, error)
        failedCount++
        results.push(`❌ 执行失败: ${error.message || error}`)
      }
    }

    return {
      success: successCount > 0,
      message: `执行完成: ${successCount} 成功, ${failedCount} 失败`,
      data: { results, successCount, failedCount }
    }
  }

  /**
   * 飞行到指定位置
   */
  private async executeFlyTo(params: any): Promise<ActionResult> {
    return new Promise((resolve) => {
      // 城市名称映射
      const cityCoords: Record<string, [number, number]> = {
        '北京': [116.4074, 39.9042],
        '上海': [121.4737, 31.2304],
        '广州': [113.2644, 23.1291],
        '深圳': [114.0579, 22.5431],
        '香港': [114.1694, 22.3193],
        'Beijing': [116.4074, 39.9042],
        'Shanghai': [121.4737, 31.2304],
        'Guangzhou': [113.2644, 23.1291],
        'Shenzhen': [114.0579, 22.5431],
        'Hong Kong': [114.1694, 22.3193]
      }

      let longitude = params.longitude
      let latitude = params.latitude
      let height = params.height || 50000

      // 如果提供了城市名称
      if (params.city && cityCoords[params.city]) {
        [longitude, latitude] = cityCoords[params.city]
      }

      if (!longitude || !latitude) {
        resolve({
          success: false,
          message: '请提供城市名称或坐标'
        })
        return
      }

      // 执行飞行
      this.viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(
          longitude,
          latitude,
          height
        ),
        duration: params.duration || 3.0,
        orientation: {
          heading: Cesium.Math.toRadians(params.heading || 0),
          pitch: Cesium.Math.toRadians(params.pitch || -45),
          roll: 0.0
        }
      })

      resolve({
        success: true,
        message: `已飞行到 ${params.city || `(${longitude}, ${latitude}`}`
      })
    })
  }

  /**
   * 设置视角
   */
  private async executeSetView(params: any): Promise<ActionResult> {
    return new Promise((resolve) => {
      const cityCoords: Record<string, [number, number]> = {
        '北京': [116.4074, 39.9042],
        '上海': [121.4737, 31.2304]
      }

      let longitude = params.longitude
      let latitude = params.latitude

      if (params.city && cityCoords[params.city]) {
        [longitude, latitude] = cityCoords[params.city]
      }

      this.viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(
          longitude || 116.4074,
          latitude || 39.9042,
          params.height || 50000
        )
      })

      resolve({
        success: true,
        message: `视角已设置到 ${params.city || `(${longitude}, ${latitude}`}`
      })
    })
  }

  /**
   * 查询建筑
   */
  private async executeBuildingQuery(params: any): Promise<ActionResult> {
    try {
      // 调用后端API
      const response = await fetch('/api/buildings/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      })

      const data = await response.json()

      return {
        success: true,
        message: `找到 ${data.count} 条建筑记录`,
        data: data
      }
    } catch (error: any) {
      return {
        success: false,
        message: `查询失败: ${error.message}`
      }
    }
  }

  /**
   * 切换底图
   */
  private async executeLayerSwitch(params: any): Promise<ActionResult> {
    try {
      // 触发底图切换事件
      const event = new CustomEvent('switchMapLayer', {
        detail: { layerType: params.layerType }
      })
      window.dispatchEvent(event)

      return {
        success: true,
        message: `已切换到${params.layerType}底图`
      }
    } catch (error: any) {
      return {
        success: false,
        message: `切换失败: ${error.message}`
      }
    }
  }

  /**
   * 重置视图
   */
  private async executeReset(): Promise<ActionResult> {
    return new Promise((resolve) => {
      this.viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(116.4074, 39.9042, 50000),
        duration: 2.0
      })

      resolve({
        success: true,
        message: '视图已重置'
      })
    })
  }
}

export default SimpleAIActionExecutor
