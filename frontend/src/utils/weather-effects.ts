/**
 * Cesium天气效果系统
 * 支持雨、雪、雾和昼夜光照效果
 */

import * as Cesium from 'cesium'

export interface WeatherCondition {
  condition: 'clear' | 'cloudy' | 'rain' | 'snow' | 'fog'
  intensity: number // 0-1，强度
  isDay: boolean
  temperature?: number
  humidity?: number
  windSpeed?: number
}

export class WeatherEffectsManager {
  private viewer: Cesium.Viewer
  private currentParticleSystem: Cesium.ParticleSystem | null = null
  private currentCondition: string = 'clear'

  constructor(viewer: Cesium.Viewer) {
    this.viewer = viewer
    this.initializeAtmosphere()
  }

  /**
   * 安全地获取 scene
   */
  private getScene(): Cesium.Scene | null {
    return this.viewer?.scene || null
  }

  /**
   * 初始化大气效果
   */
  private initializeAtmosphere(): void {
    const scene = this.getScene()
    if (!scene) return

    scene.fog.enabled = true
    scene.fog.density = 0.0002
    scene.fog.minimumBrightness = 0.03
  }

  /**
   * 设置天气效果
   */
  public setWeather(condition: WeatherCondition): void {
    console.log('🌤️ 切换天气效果:', condition)

    // 清除现有效果
    this.clearWeatherEffects()

    // 设置天气条件
    this.currentCondition = condition.condition

    // 根据条件应用效果
    switch (condition.condition) {
      case 'rain':
        this.createRainEffect(condition.intensity)
        this.setAtmosphereForRain(condition.isDay)
        break
      case 'snow':
        this.createSnowEffect(condition.intensity)
        this.setAtmosphereForSnow(condition.isDay)
        break
      case 'fog':
        this.createFogEffect(condition.intensity)
        this.setAtmosphereForFog(condition.isDay)
        break
      case 'cloudy':
        this.setAtmosphereForCloudy(condition.isDay)
        break
      case 'clear':
      default:
        this.setAtmosphereForClear(condition.isDay)
        break
    }

    // 设置日夜光照
    this.setDayNightLighting(condition.isDay)
  }

  /**
   * 创建雨效果（禁用粒子系统，使用雾和天空效果）
   */
  private createRainEffect(intensity: number = 0.5): void {
    const scene = this.getScene()
    if (!scene) return

    // 使用雾效果模拟雨天
    scene.fog.enabled = true
    scene.fog.density = 0.0002 + intensity * 0.002
    scene.fog.minimumBrightness = 0.01

    // 调暗天空
    if (scene.skyAtmosphere) {
      scene.skyAtmosphere.brightnessShift = -0.3 * intensity
    }

    console.log('✅ 雨效果已应用（雾效果）')
  }

  /**
   * 创建雪效果（禁用粒子系统，使用雾和天空效果）
   */
  private createSnowEffect(intensity: number = 0.5): void {
    const scene = this.getScene()
    if (!scene) return

    // 使用雾效果模拟雪天
    scene.fog.enabled = true
    scene.fog.density = 0.0002 + intensity * 0.0015
    scene.fog.minimumBrightness = 0.02

    // 调整天空
    if (scene.skyAtmosphere) {
      scene.skyAtmosphere.brightnessShift = -0.2 * intensity
      scene.skyAtmosphere.saturationShift = -0.1 * intensity
    }

    console.log('✅ 雪效果已应用（雾效果）')
  }

  /**
   * 创建雾效果
   */
  private createFogEffect(intensity: number = 0.5): void {
    const scene = this.getScene()
    if (!scene) return

    scene.fog.enabled = true
    scene.fog.density = 0.0002 + intensity * 0.001
    scene.fog.minimumBrightness = 0.03

    console.log('✅ 雾效果已应用')
  }

  /**
   * 清除天气效果
   */
  private clearWeatherEffects(): void {
    // 清除粒子系统
    if (this.currentParticleSystem) {
      this.currentParticleSystem.destroy()
      this.currentParticleSystem = null
    }

    // 安全地重置雾效果
    if (this.viewer && this.viewer.scene) {
      this.viewer.scene.fog.density = 0.0002
    }
  }

  /**
   * 设置晴天大气
   */
  private setAtmosphereForClear(isDay: boolean): void {
    const scene = this.getScene()
    if (!scene) return

    // 不修改SkyBox，使用默认的天空盒
    // scene.skyBox = new Cesium.SkyBox({...}) // 需要有效的图片URL

    // 安全地设置大气效果
    if (scene.skyAtmosphere) {
      scene.skyAtmosphere.hueShift = 0.0
      scene.skyAtmosphere.saturationShift = 0.0
      scene.skyAtmosphere.brightnessShift = 0.0
    }

    console.log(`☀️ 晴天 (${isDay ? '白天' : '夜晚'})`)
  }

  /**
   * 设置雨天大气
   */
  private setAtmosphereForRain(isDay: boolean): void {
    const scene = this.getScene()
    if (!scene) return

    if (scene.skyAtmosphere) {
      scene.skyAtmosphere.saturationShift = -0.3
      scene.skyAtmosphere.brightnessShift = -0.2

      if (!isDay) {
        scene.skyAtmosphere.hueShift = 0.1
      }
    }

    console.log(`🌧️ 雨天 (${isDay ? '白天' : '夜晚'})`)
  }

  /**
   * 设置雪天大气
   */
  private setAtmosphereForSnow(isDay: boolean): void {
    const scene = this.getScene()
    if (!scene) return

    if (scene.skyAtmosphere) {
      scene.skyAtmosphere.saturationShift = -0.1
      scene.skyAtmosphere.brightnessShift = 0.1
    }

    console.log(`❄️ 雪天 (${isDay ? '白天' : '夜晚'})`)
  }

  /**
   * 设置雾天大气
   */
  private setAtmosphereForFog(isDay: boolean): void {
    const scene = this.getScene()
    if (!scene) return

    if (scene.skyAtmosphere) {
      scene.skyAtmosphere.saturationShift = -0.4
      scene.skyAtmosphere.brightnessShift = -0.3
    }

    console.log(`🌫️ 雾天 (${isDay ? '白天' : '夜晚'})`)
  }

  /**
   * 设置多云大气
   */
  private setAtmosphereForCloudy(isDay: boolean): void {
    const scene = this.getScene()
    if (!scene) return

    if (scene.skyAtmosphere) {
      scene.skyAtmosphere.saturationShift = -0.2
      scene.skyAtmosphere.brightnessShift = -0.1
    }

    console.log(`☁️ 多云 (${isDay ? '白天' : '夜晚'})`)
  }

  /**
   * 设置日夜光照
   */
  private setDayNightLighting(isDay: boolean): void {
    const scene = this.getScene()
    if (!scene) return

    if (isDay) {
      // 白天光照
      scene.light = new Cesium.DirectionalLight({
        direction: Cesium.Cartesian3.fromDegrees(0, 45, 100000000),
        intensity: 1.5
      })

      // 启用太阳光照
      if (scene.globe) {
        scene.globe.enableLighting = true
      }

      console.log('☀️ 白天光照已启用')
    } else {
      // 夜晚光照（月光）
      scene.light = new Cesium.DirectionalLight({
        direction: Cesium.Cartesian3.fromDegrees(0, -45, 100000000),
        intensity: 0.3
      })

      // 降低环境光
      if (scene.globe) {
        scene.globe.enableLighting = true
      }

      console.log('🌙 夜晚光照已启用')
    }
  }

  /**
   * 获取当前天气条件
   */
  public getCurrentCondition(): string {
    return this.currentCondition
  }

  /**
   * 销毁天气效果系统
   */
  public destroy(): void {
    this.clearWeatherEffects()
  }
}

export default WeatherEffectsManager
