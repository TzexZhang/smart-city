/**
 * AI指令执行器 - 简化版
 * 避免复杂的类型问题，专注于功能实现
 */
import * as Cesium from 'cesium'
import WeatherEffectsManager, { WeatherCondition } from './weather-effects'

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
  private weatherManager: WeatherEffectsManager

  constructor(viewer: Cesium.Viewer) {
    this.viewer = viewer
    this.weatherManager = new WeatherEffectsManager(viewer)
  }

  /**
   * 执行AI返回的actions
   * 支持顺序执行、等待完成、延迟等高级功能
   */
  async executeActions(actions: Array<any>): Promise<ActionResult> {
    console.log('📋 收到AI指令:', actions)
    console.log('   指令数量:', actions.length)

    let successCount = 0
    let failedCount = 0
    const results: string[] = []
    let weatherData: any = null // 存储天气数据

    for (const actionConfig of actions) {
      try {
        const actionType = actionConfig.type
        const params = actionConfig.parameters || {}
        const waitForCompletion = actionConfig.wait_for_completion || false
        const delay = actionConfig.delay || 0
        const description = actionConfig.description || actionType

        console.log(`🎯 执行指令: ${description}`)
        console.log('   类型:', actionType)
        console.log('   参数:', params)
        console.log('   等待完成:', waitForCompletion)
        console.log('   延迟:', delay, 'ms')

        // 如果有延迟，先等待
        if (delay > 0) {
          console.log(`⏱️ 延迟 ${delay}ms 后执行...`)
          await this.sleep(delay)
        }

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

          case 'spatial_buffer':
            result = await this.executeBufferAnalysis(params)
            break

          case 'spatial_viewshed':
            result = await this.executeViewshedAnalysis(params)
            break

          case 'spatial_accessibility':
            result = await this.executeAccessibilityAnalysis(params)
            break

          case 'set_weather':
            result = await this.executeSetWeather(params)
            break

          case 'get_weather':
            result = await this.executeGetWeather(params)
            // 保存天气数据供UI显示使用
            if (result.success && result.data) {
              weatherData = result.data
            }
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
      data: { results, successCount, failedCount, weatherData }
    }
  }

  /**
   * 飞行到指定位置
   */
  private async executeFlyTo(params: any): Promise<ActionResult> {
    return new Promise(async (resolve) => {
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
        '西安': [108.9398, 34.3416],
        '成都': [104.0668, 30.5728],
        '杭州': [120.1551, 30.2741],
        '武汉': [114.3055, 30.5928],
        '南京': [118.7969, 32.0603],
        'Beijing': [116.4074, 39.9042],
        'Shanghai': [121.4737, 31.2304],
        'Guangzhou': [113.2644, 23.1291],
        'Shenzhen': [114.0579, 22.5431],
        'Hong Kong': [114.1694, 22.3193],
        "Xi'an": [108.9398, 34.3416],
        'Chengdu': [104.0668, 30.5728],
        'Hangzhou': [120.1551, 30.2741],
        'Wuhan': [114.3055, 30.5928],
        'Nanjing': [118.7969, 32.0603]
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
        const duration = params.duration || 3.0

        viewer.camera.flyTo({
          destination: Cesium.Cartesian3.fromDegrees(
            longitude as number,
            latitude as number,
            height as number
          ),
          duration: duration,
          orientation: {
            heading: Cesium.Math.toRadians(params.heading || 0),
            pitch: Cesium.Math.toRadians(params.pitch || -45),
            roll: 0.0
          },
          // 添加完成回调
          complete: () => {
            console.log('✅ 飞行完成')
          }
        })

        // 等待飞行完成（duration + 0.5秒缓冲）
        await this.sleep((duration * 1000) + 500)

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

  /**
   * 缓冲区分析 - 分析指定半径范围内的建筑
   */
  private async executeBufferAnalysis(params: any): Promise<ActionResult> {
    console.log('🔵 执行缓冲区分析:', params)

    try {
      const { longitude, latitude, radius = 1000 } = params

      if (!longitude || !latitude) {
        return {
          success: false,
          message: '请提供中心点坐标 (longitude, latitude)'
        }
      }

      // 调用后端缓冲区分析API
      const queryParams = new URLSearchParams({
        center_lon: longitude.toString(),
        center_lat: latitude.toString(),
        radius: radius.toString(),
      })

      const response = await fetch(`/api/v1/spatial/buffer?${queryParams}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('✅ 缓冲区分析结果:', data)

      // 在Cesium上绘制缓冲区圆圈
      this.drawBufferCircle(longitude, latitude, radius)

      return {
        success: true,
        message: `缓冲区分析完成: 找到 ${data.total || 0} 个建筑`,
        data: data
      }
    } catch (error: any) {
      console.error('❌ 缓冲区分析失败:', error)
      return {
        success: false,
        message: `缓冲区分析失败: ${error.message}`
      }
    }
  }

  /**
   * 视域分析 - 分析从某点可见的区域
   */
  private async executeViewshedAnalysis(params: any): Promise<ActionResult> {
    console.log('👁️ 执行视域分析:', params)

    try {
      const { longitude, latitude, observerHeight = 50, radius = 1000 } = params

      if (!longitude || !latitude) {
        return {
          success: false,
          message: '请提供观察点坐标 (longitude, latitude)'
        }
      }

      // 调用后端视域分析API
      const queryParams = new URLSearchParams({
        longitude: longitude.toString(),
        latitude: latitude.toString(),
        observer_height: observerHeight.toString(),
        radius: radius.toString(),
      })

      const response = await fetch(`/api/v1/spatial/viewshed?${queryParams}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('✅ 视域分析结果:', data)

      // 在Cesium上可视化视域热力图
      this.drawViewshedHeatmap(data.visible_areas || [])

      return {
        success: true,
        message: `视域分析完成: 可见区域覆盖率 ${data.coverage_percent || 0}%`,
        data: data
      }
    } catch (error: any) {
      console.error('❌ 视域分析失败:', error)
      return {
        success: false,
        message: `视域分析失败: ${error.message}`
      }
    }
  }

  /**
   * 可达性分析 - 分析服务覆盖范围
   */
  private async executeAccessibilityAnalysis(params: any): Promise<ActionResult> {
    console.log('🚗 执行可达性分析:', params)

    try {
      const { longitude, latitude, mode = 'driving', timeLimit = 15 } = params

      if (!longitude || !latitude) {
        return {
          success: false,
          message: '请提供起点坐标 (longitude, latitude)'
        }
      }

      // 调用后端可达性分析API
      const queryParams = new URLSearchParams({
        origin_lon: longitude.toString(),
        origin_lat: latitude.toString(),
        mode: mode,
        time_limit: timeLimit.toString(),
      })

      const response = await fetch(`/api/v1/spatial/accessibility?${queryParams}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('✅ 可达性分析结果:', data)

      // 在Cesium上绘制等时圈
      this.drawIsochrones(data.isochrones || [])

      return {
        success: true,
        message: `可达性分析完成: ${timeLimit}分钟${mode === 'driving' ? '驾车' : mode === 'walking' ? '步行' : '公交'}覆盖区域`,
        data: data
      }
    } catch (error: any) {
      console.error('❌ 可达性分析失败:', error)
      return {
        success: false,
        message: `可达性分析失败: ${error.message}`
      }
    }
  }

  /**
   * 在Cesium上绘制缓冲区圆圈
   */
  private drawBufferCircle(longitude: number, latitude: number, radius: number): void {
    try {
      const viewer = this.viewer as any

      // 添加圆形实体
      viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(longitude, latitude),
        name: 'Buffer Analysis',
        ellipse: {
          semiMinorAxis: radius,
          semiMajorAxis: radius,
          height: 0,
          material: Cesium.Color.RED.withAlpha(0.2),
          outline: true,
          outlineColor: Cesium.Color.RED,
          outlineWidth: 2,
        },
      })

      console.log('✅ 缓冲区圆圈已绘制')
    } catch (error) {
      console.error('❌ 绘制缓冲区圆圈失败:', error)
    }
  }

  /**
   * 在Cesium上绘制视域热力图
   */
  private drawViewshedHeatmap(visibleAreas: any[]): void {
    try {
      const viewer = this.viewer as any

      visibleAreas.forEach((area: any, index: number) => {
        viewer.entities.add({
          position: Cesium.Cartesian3.fromDegrees(area.longitude, area.latitude),
          name: `Visible Area ${index}`,
          point: {
            pixelSize: 10,
            color: area.visible ? Cesium.Color.GREEN.withAlpha(0.6) : Cesium.Color.RED.withAlpha(0.3),
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 1,
          },
        })
      })

      console.log('✅ 视域热力图已绘制')
    } catch (error) {
      console.error('❌ 绘制视域热力图失败:', error)
    }
  }

  /**
   * 在Cesium上绘制等时圈
   */
  private drawIsochrones(isochrones: any[]): void {
    try {
      const viewer = this.viewer as any

      const colors = [
        Cesium.Color.BLUE.withAlpha(0.3),
        Cesium.Color.GREEN.withAlpha(0.3),
        Cesium.Color.YELLOW.withAlpha(0.3),
        Cesium.Color.ORANGE.withAlpha(0.3),
      ]

      isochrones.forEach((isochrone: any, index: number) => {
        viewer.entities.add({
          name: `Isochrone ${isochrone.time} min`,
          polygon: {
            hierarchy: Cesium.Cartesian3.fromDegreesArray(isochrone.coordinates),
            height: 0,
            material: colors[index % colors.length],
            outline: true,
            outlineColor: colors[index % colors.length],
            outlineWidth: 2,
          },
        })
      })

      console.log('✅ 等时圈已绘制')
    } catch (error) {
      console.error('❌ 绘制等时圈失败:', error)
    }
  }

  /**
   * 设置天气效果（支持地点参数，自动飞行到指定地点）
   */
  private async executeSetWeather(params: any): Promise<ActionResult> {
    console.log('🌤️ 设置天气效果:', params)

    try {
      const {
        city,
        latitude,
        longitude,
        condition,
        intensity = 0.5,
        is_day = true,
        temperature,
        humidity,
        wind_speed,
        height = 500 // 飞行高度
      } = params

      // 如果提供了地点信息，先飞行到该地点
      if (city || (latitude && longitude)) {
        console.log('✈️ 准备飞行到指定地点...')

        // 构建飞行参数
        const flyParams: any = {}
        if (city) {
          flyParams.city = city
        }
        if (latitude && longitude) {
          flyParams.longitude = longitude
          flyParams.latitude = latitude
        }
        flyParams.height = height

        // 执行飞行
        const flyResult = await this.executeFlyTo(flyParams)

        if (!flyResult.success) {
          return {
            success: false,
            message: `无法飞行到指定地点: ${flyResult.message}`
          }
        }

        // 等待飞行完成
        await this.sleep((height / 500 * 1000) + 1000) // 粗略估算飞行时间 + 1秒缓冲
        console.log('✅ 已到达目标地点，开始设置天气...')
      }

      // 验证天气条件
      const validConditions = ['clear', 'cloudy', 'rain', 'snow', 'fog']
      const weatherCondition = validConditions.includes(condition) ? condition : 'clear'

      // 构建天气条件对象
      const weather: WeatherCondition = {
        condition: weatherCondition,
        intensity: Math.max(0, Math.min(1, intensity)),
        isDay: Boolean(is_day),
        temperature,
        humidity,
        windSpeed: wind_speed
      }

      // 应用天气效果
      this.weatherManager.setWeather(weather)

      // 获取中文名称
      const conditionNames: Record<string, string> = {
        'clear': is_day ? '晴天' : '晴朗夜晚',
        'cloudy': is_day ? '多云' : '多云夜晚',
        'rain': is_day ? '雨天' : '雨夜',
        'snow': is_day ? '雪天' : '雪夜',
        'fog': is_day ? '雾天' : '雾夜'
      }

      const conditionName = conditionNames[weatherCondition] || weatherCondition

      let message = `已切换到${conditionName}天气效果`
      if (city || (latitude && longitude)) {
        const locationName = city || `(${latitude?.toFixed(4)}, ${longitude?.toFixed(4)})`
        message = `已飞行到${locationName}，切换到${conditionName}天气效果`
      }

      return {
        success: true,
        message: message,
        data: {
          condition: weatherCondition,
          conditionName,
          intensity,
          isDay: is_day,
          location: city || { latitude, longitude }
        }
      }
    } catch (error: any) {
      console.error('❌ 设置天气效果失败:', error)
      return {
        success: false,
        message: `设置天气失败: ${error.message}`
      }
    }
  }

  /**
   * 获取并应用实时天气
   */
  private async executeGetWeather(params: any): Promise<ActionResult> {
    console.log('🌡️ 获取实时天气:', params)

    try {
      const { city, latitude, longitude } = params

      // 调用后端天气API
      const queryParams = new URLSearchParams()
      if (city) queryParams.append('city', city)
      if (latitude) queryParams.append('latitude', latitude.toString())
      if (longitude) queryParams.append('longitude', longitude.toString())

      const response = await fetch(`/api/v1/weather/current?${queryParams}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const weatherData = await response.json()
      console.log('✅ 获取天气数据成功:', weatherData)

      // 应用天气效果
      if (weatherData.status === 'success') {
        const weather: WeatherCondition = {
          condition: weatherData.cesium_condition || 'clear',
          intensity: this.calculateWeatherIntensity(weatherData),
          isDay: weatherData.is_day !== undefined ? weatherData.is_day : true,
          temperature: weatherData.temperature,
          humidity: weatherData.humidity,
          windSpeed: weatherData.wind_speed
        }

        this.weatherManager.setWeather(weather)

        const conditionName = this.getConditionDisplayName(weatherData.condition, weatherData.is_day)

        return {
          success: true,
          message: `${weatherData.city}当前天气：${conditionName}，温度 ${weatherData.temperature}°C`,
          data: weatherData
        }
      } else {
        throw new Error(weatherData.error || '获取天气失败')
      }
    } catch (error: any) {
      console.error('❌ 获取天气失败:', error)
      return {
        success: false,
        message: `获取天气失败: ${error.message}`
      }
    }
  }

  /**
   * 根据天气数据计算强度
   */
  private calculateWeatherIntensity(weatherData: any): number {
    const condition = weatherData.cesium_condition || 'clear'
    const humidity = weatherData.humidity || 50
    const windSpeed = weatherData.wind_speed || 0

    switch (condition) {
      case 'rain':
        // 根据湿度和风速计算雨的强度
        return Math.min(1, (humidity - 50) / 50 + windSpeed / 20)
      case 'snow':
        // 根据温度计算雪的强度
        const temp = weatherData.temperature || 0
        return Math.min(1, Math.abs(temp) / 10)
      case 'fog':
        // 根据湿度计算雾的强度
        return Math.min(1, (humidity - 60) / 40)
      default:
        return 0.5
    }
  }

  /**
   * 获取天气条件的显示名称
   */
  private getConditionDisplayName(condition: string, isDay: boolean): string {
    const conditionMap: Record<string, { day: string; night: string }> = {
      'Clear': { day: '晴天', night: '晴朗夜晚' },
      'Clouds': { day: '多云', night: '多云夜晚' },
      'Rain': { day: '雨天', night: '雨夜' },
      'Drizzle': { day: '小雨', night: '小雨' },
      'Thunderstorm': { day: '雷阵雨', night: '雷雨夜' },
      'Snow': { day: '雪天', night: '雪夜' },
      'Mist': { day: '薄雾', night: '薄雾' },
      'Fog': { day: '大雾', night: '大雾' },
      'Haze': { day: '霾', night: '霾' }
    }

    const mapped = conditionMap[condition]
    return mapped ? (isDay ? mapped.day : mapped.night) : condition
  }

  /**
   * 延迟辅助方法
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

export default SimpleAIActionExecutor
