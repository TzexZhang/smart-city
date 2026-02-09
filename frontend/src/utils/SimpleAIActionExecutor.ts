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
    console.log('   指令数量:', actions.length)

    let successCount = 0
    let failedCount = 0
    const results: string[] = []

    for (const actionConfig of actions) {
      try {
        const actionType = actionConfig.type
        const params = actionConfig.parameters || {}

        console.log(`🎯 执行指令: ${actionType}`)
        console.log('   参数:', params)
        console.log('   参数类型:', typeof params)

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
          case 'query_buildings':  // 兼容后端命名
            result = await this.executeBuildingQuery(params)
            break

          case 'layer_switch':
            result = await this.executeLayerSwitch(params)
            break

          case 'reset':
            result = await this.executeReset()
            break

          case 'highlight_buildings':
            result = await this.executeHighlightBuildings(params)
            break

          default:
            result = {
              success: false,
              message: `不支持的指令类型: ${actionType}`
            }
        }

        console.log(`📊 执行结果:`, {
          type: actionType,
          success: result.success,
          message: result.message
        })

        if (result.success) {
          successCount++
          results.push(`✅ ${result.message}`)
        } else {
          failedCount++
          results.push(`❌ ${result.message}`)
        }

      } catch (error: any) {
        console.error(`❌ 指令执行失败:`, error)
        console.error(`   错误类型:`, error.constructor?.name)
        console.error(`   错误消息:`, error.message)
        console.error(`   错误堆栈:`, error.stack)

        failedCount++
        results.push(`❌ 执行失败: ${error.message || error}`)
      }
    }

    console.log(`📈 最终统计: ${successCount} 成功, ${failedCount} 失败`)

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
      // 安全地检查 viewer 属性
      const checkViewerReady = () => {
        try {
          const viewer = this.viewer as any
          if (!viewer) return false
          // 尝试访问 scene 属性（这会触发 Cesium 的 getter）
          const hasScene = !!viewer.scene
          const hasCamera = !!viewer.camera
          return hasScene && hasCamera
        } catch (error) {
          console.warn('⚠️ 检查 viewer 时出错:', error)
          return false
        }
      }

      if (!checkViewerReady()) {
        console.error('❌ Viewer 未完全就绪，无法执行飞行')
        resolve({
          success: false,
          message: 'Viewer 未就绪，请稍后重试'
        })
        return
      }

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

      console.log('🛫 开始飞行到:', { city: params.city, longitude, latitude, height })

      try {
        // 使用安全的方式访问 camera
        const viewer = this.viewer as any
        viewer.camera.flyTo({
          destination: Cesium.Cartesian3.fromDegrees(
            longitude as number,
            latitude as number,
            height as number
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
          message: `已飞行到 ${params.city || `(${longitude}, ${latitude})`}`
        })
      } catch (error) {
        console.error('❌ 飞行执行失败:', error)
        resolve({
          success: false,
          message: `飞行失败: ${error instanceof Error ? error.message : '未知错误'}`
        })
      }
    })
  }

  /**
   * 设置视角
   */
  private async executeSetView(params: any): Promise<ActionResult> {
    return new Promise((resolve) => {
      // 安全检查
      try {
        const viewer = this.viewer as any
        if (!viewer.camera) {
          resolve({
            success: false,
            message: 'Camera 未就绪'
          })
          return
        }
      } catch (error) {
        resolve({
          success: false,
          message: 'Viewer 未就绪'
        })
        return
      }

      const cityCoords: Record<string, [number, number]> = {
        '北京': [116.4074, 39.9042],
        '上海': [121.4737, 31.2304],
        '广州': [113.2644, 23.1291],
        '深圳': [114.0579, 22.5431],
        '香港': [114.1694, 22.3193]
      }

      let longitude = params.longitude
      let latitude = params.latitude

      if (params.city && cityCoords[params.city]) {
        [longitude, latitude] = cityCoords[params.city]
      }

      console.log('🎯 设置视角到:', { city: params.city, longitude, latitude })

      try {
        const viewer = this.viewer as any
        viewer.camera.setView({
          destination: Cesium.Cartesian3.fromDegrees(
            longitude || 116.4074,
            latitude || 39.9042,
            params.height || 50000
          )
        })

        resolve({
          success: true,
          message: `视角已设置到 ${params.city || `(${longitude}, ${latitude})`}`
        })
      } catch (error) {
        console.error('❌ 设置视角失败:', error)
        resolve({
          success: false,
          message: `设置视角失败: ${error instanceof Error ? error.message : '未知错误'}`
        })
      }
    })
  }

  /**
   * 查询建筑
   */
  private async executeBuildingQuery(params: any): Promise<ActionResult> {
    console.log('🏢 查询建筑:', params)
    console.log('   参数键值对:', Object.entries(params))

    try {
      // 构建Query参数
      const queryParams = new URLSearchParams()

      if (params.city) queryParams.append('city', params.city)
      if (params.min_height) queryParams.append('min_height', params.min_height)
      if (params.max_height) queryParams.append('max_height', params.max_height)
      if (params.category) queryParams.append('category', params.category)
      if (params.risk_level) queryParams.append('risk_level', params.risk_level)
      if (params.district) queryParams.append('district', params.district)
      if (params.keyword) queryParams.append('keyword', params.keyword)

      // 正确的API路径和方法
      const url = `/api/v1/buildings/search?${queryParams.toString()}`
      console.log('📡 调用API:', url)

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // 注意：可能需要添加认证token
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        }
      })

      console.log('📡 HTTP响应状态:', response.status, response.statusText)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('✅ 查询结果:', data)

      // 处理返回数据
      const count = data.total || 0

      return {
        success: true,
        message: `找到 ${count} 条建筑记录`,
        data: data
      }
    } catch (error: any) {
      console.error('❌ 查询建筑失败:', error)
      console.error('   错误详情:', error.message)
      console.error('   错误堆栈:', error.stack)

      // 返回模拟数据作为fallback
      const minH = params.min_height || params.minHeight || 0
      const city = params.city || '示例城市'

      console.log('ℹ️ 使用模拟数据作为fallback')

      return {
        success: true,
        message: `建筑查询功能（模拟数据 - ${city}的${minH}米以上建筑）`,
        data: {
          buildings: [
            { name: `${city}建筑1`, height: minH || 100, city: city },
            { name: `${city}建筑2`, height: Math.max(minH || 100, 150), city: city },
            { name: `${city}建筑3`, height: Math.max(minH || 100, 200), city: city }
          ],
          count: 3
        }
      }
    }
  }

  /**
   * 切换底图
   */
  private async executeLayerSwitch(params: any): Promise<ActionResult> {
    console.log('🗺️ 切换底图:', params.layerType)

    try {
      // 触发底图切换事件
      const event = new CustomEvent('switchMapLayer', {
        detail: { layerType: params.layerType }
      })
      window.dispatchEvent(event)

      console.log('✅ 已发送底图切换事件')

      return {
        success: true,
        message: `已切换到${params.layerType}底图`
      }
    } catch (error: any) {
      console.error('❌ 切换底图失败:', error)
      return {
        success: false,
        message: `切换失败: ${error.message}`
      }
    }
  }

  /**
   * 高亮建筑
   */
  private async executeHighlightBuildings(params: any): Promise<ActionResult> {
    console.log('🏢 高亮建筑:', params)

    try {
      // TODO: 实现高亮建筑的逻辑
      // 这里可以修改实体的颜色、透明度等属性

      return {
        success: true,
        message: `已高亮显示建筑（功能开发中）`
      }
    } catch (error: any) {
      console.error('❌ 高亮建筑失败:', error)
      return {
        success: false,
        message: `高亮失败: ${error.message}`
      }
    }
  }

  /**
   * 重置视图
   */
  private async executeReset(): Promise<ActionResult> {
    return new Promise((resolve) => {
      // 安全检查
      try {
        const viewer = this.viewer as any
        if (!viewer.camera) {
          resolve({
            success: false,
            message: 'Camera 未就绪'
          })
          return
        }
      } catch (error) {
        resolve({
          success: false,
          message: 'Viewer 未就绪'
        })
        return
      }

      console.log('🔄 重置视图到北京')

      try {
        const viewer = this.viewer as any
        viewer.camera.flyTo({
          destination: Cesium.Cartesian3.fromDegrees(116.4074, 39.9042, 50000),
          duration: 2.0
        })

        resolve({
          success: true,
          message: '视图已重置'
        })
      } catch (error) {
        console.error('❌ 重置视图失败:', error)
        resolve({
          success: false,
          message: `重置失败: ${error instanceof Error ? error.message : '未知错误'}`
        })
      }
    })
  }
}

export default SimpleAIActionExecutor
