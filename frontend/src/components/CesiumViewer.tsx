import { useEffect, useRef } from 'react'
import * as Cesium from 'cesium'
import { useCesiumViewer } from '../contexts/CesiumContext'

// 配置 Cesium Ion Access Token
// 请在 https://ion.cesium.com/tokens 获取您的免费 token
const VITE_CESIUM_ION_TOKEN = import.meta.env.VITE_CESIUM_ION_TOKEN || ''

if ((Cesium as any).Ion && VITE_CESIUM_ION_TOKEN) {
  (Cesium as any).Ion.defaultAccessToken = VITE_CESIUM_ION_TOKEN
}

const CesiumViewer = () => {
  const cesiumContainer = useRef<HTMLDivElement>(null)
  const viewerRef = useRef<Cesium.Viewer | null>(null)
  const buildingsLoadedRef = useRef(false)  // 使用ref避免触发重新渲染
  const { registerViewer, unregisterViewer } = useCesiumViewer()

  useEffect(() => {
    // 防止重复初始化
    if (viewerRef.current) {
      console.log('⚠️ Viewer 已存在，跳过重复初始化')
      return
    }

    // 确保容器存在并且已经挂载到 DOM
    if (!cesiumContainer.current) {
      console.warn('⏳ Cesium 容器未准备好，等待下次渲染...')
      return
    }

    // 使用 setTimeout 确保 DOM 完全渲染
    const initTimer = setTimeout(() => {
      if (!cesiumContainer.current) {
        console.error('❌ Cesium 容器在延迟后仍然未找到')
        return
      }
      initCesium()
    }, 0)

    /**
     * 添加示例建筑
     */
    const addSampleBuildings = (viewer: Cesium.Viewer) => {
      try {
        const viewerPosition = Cesium.Cartesian3.fromDegrees(116.3974, 39.9093, 0)

        // 添加中国（模拟）
        const positions = []
        const numberOfPoints = 16
        for (let i = 0; i < numberOfPoints; i++) {
          const angle = (i / numberOfPoints) * Cesium.Math.TWO_PI
          const radius = 50
          const x = Math.cos(angle) * radius
          const y = Math.sin(angle) * radius
          positions.push(
            new Cesium.Cartesian3(viewerPosition.x + x, viewerPosition.y + y, 0)
          )
        }
        positions.push(positions[0]) // 闭合多边形

        viewer.entities.add({
          name: '中国',
          polygon: {
            hierarchy: new Cesium.PolygonHierarchy(positions),
            extrudedHeight: 500,
            material: Cesium.Color.BLUE.withAlpha(0.5),
            outline: true,
            outlineColor: Cesium.Color.BLUE,
            outlineWidth: 2
          }
        })

        // 添加其他示例建筑
        for (let i = 0; i < 5; i++) {
          const height = 200 + Math.random() * 300
          const lon = 116.3974 + (Math.random() - 0.5) * 0.01
          const lat = 39.9093 + (Math.random() - 0.5) * 0.01

          viewer.entities.add({
            name: `建筑 ${i + 1}`,
            position: Cesium.Cartesian3.fromDegrees(lon, lat, 0),
            box: {
              dimensions: new Cesium.Cartesian3(100, 100, height),
              material: Cesium.Color.fromRandom({ alpha: 0.6 }),
              outline: true,
              outlineColor: Cesium.Color.WHITE
            }
          })
        }
        console.log('✅ 示例建筑添加成功')
      } catch (error) {
        console.warn('添加示例建筑失败:', error)
      }
    }

    /**
     * 加载OSM道路数据
     */
    const loadOSMRoads = async (viewer: Cesium.Viewer) => {
      try {
        console.log('🛣️ 开始加载OSM道路数据...')

        // 定义重点城市（北京作为示例）
        const cities = [
          { name: '北京', lon: 116.3974, lat: 39.9093 },
        ]

        // 为每个城市创建简化的示例道路网络
        for (const city of cities) {
          try {
            // 创建主要道路网格（简化版本，不依赖外部API）
            const gridSize = 0.02 // 网格大小（度）
            const roadCount = 8 // 道路数量

            // 创建东西向道路
            for (let i = 0; i < roadCount; i++) {
              const lat = city.lat + (i - roadCount / 2) * gridSize
              const lonStart = city.lon - gridSize * 4
              const lonEnd = city.lon + gridSize * 4

              viewer.entities.add({
                name: `${city.name} - 东西向道路${i + 1}`,
                polyline: {
                  positions: Cesium.Cartesian3.fromDegreesArrayHeights([
                    lonStart, lat, 1,
                    lonEnd, lat, 1
                  ]),
                  width: 2,
                  material: Cesium.Color.fromCssColorString('#4D96FF'),
                  clampToGround: false,
                }
              })
            }

            // 创建南北向道路
            for (let i = 0; i < roadCount; i++) {
              const lon = city.lon + (i - roadCount / 2) * gridSize
              const latStart = city.lat - gridSize * 4
              const latEnd = city.lat + gridSize * 4

              viewer.entities.add({
                name: `${city.name} - 南北向道路${i + 1}`,
                polyline: {
                  positions: Cesium.Cartesian3.fromDegreesArrayHeights([
                    lon, latStart, 1,
                    lon, latEnd, 1
                  ]),
                  width: 2,
                  material: Cesium.Color.fromCssColorString('#6BCB77'),
                  clampToGround: false,
                }
              })
            }

            // 添加一条主干道（模拟环路）
            const loopRoadPoints: number[] = []
            const loopRadius = gridSize * 3
            for (let angle = 0; angle <= 360; angle += 10) {
              const lon = city.lon + Math.cos(angle * Math.PI / 180) * loopRadius
              const lat = city.lat + Math.sin(angle * Math.PI / 180) * loopRadius
              loopRoadPoints.push(lon, lat, 1)
            }

            viewer.entities.add({
              name: `${city.name} - 主环路`,
              polyline: {
                positions: Cesium.Cartesian3.fromDegreesArrayHeights(loopRoadPoints),
                width: 4,
                material: Cesium.Color.fromCssColorString('#FFD93D'),
                clampToGround: false,
              }
            })

            console.log(`✅ ${city.name}道路加载成功（示例道路网格）`)
          } catch (error) {
            console.warn(`⚠️ ${city.name}道路加载失败:`, error)
          }
        }

        console.log('✅ OSM道路数据加载完成')
      } catch (error) {
        console.warn('⚠️ 加载OSM道路失败:', error)
      }
    }

    const initCesium = async () => {
      try {
        // 确保容器存在
        if (!cesiumContainer.current) {
          console.error('❌ Cesium 容器未找到')
          return
        }

        // 创建 Viewer 配置
        const viewerOptions: any = {
          // 基础控件设置
          timeline: false,
          animation: false,
          baseLayerPicker: false,
          geocoder: false,
          homeButton: true,
          sceneModePicker: false,
          navigationHelpButton: false,
          fullscreenButton: false,
          infoBox: false,
          selectionIndicator: false,
          // 禁用默认底图（Bing Maps）
          imageryProvider: false,
        }

        // 如果有 token，使用 Cesium World Terrain（真实地形）
        if (VITE_CESIUM_ION_TOKEN) {
          viewerOptions.terrainProvider = await Cesium.CesiumTerrainProvider.fromIonAssetId(1, {
            requestVertexNormals: true,
            requestWaterMask: true,
          })
        } else {
          // 没有 token 时使用椭球体地形（无起伏）
          viewerOptions.terrainProvider = new Cesium.EllipsoidTerrainProvider()
        }

        // 创建Cesium Viewer
        const viewer = new Cesium.Viewer(cesiumContainer.current, viewerOptions)

        viewerRef.current = viewer

        // 添加高德地图作为主底图
        const amapImageryProvider = new Cesium.UrlTemplateImageryProvider({
          url: 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
          minimumLevel: 3,
          maximumLevel: 18,
          credit: '高德地图',
        })
        viewer.imageryLayers.addImageryProvider(amapImageryProvider)

        // 如果有 token，添加全球卫星影像作为第二图层（增强视觉效果）
        if (VITE_CESIUM_ION_TOKEN) {
          try {
            const ionImagery = await Cesium.IonImageryProvider.fromAssetId(2)
            const ionLayer = viewer.imageryLayers.addImageryProvider(ionImagery, 1)
            ionLayer.alpha = 0.3 // 30% 透明度
          } catch (error) {
            console.warn('无法加载 Cesium Ion 影像，可能需要配置正确的 token')
          }
        }

        // 设置初始视角到北京
        viewer.camera.setView({
          destination: Cesium.Cartesian3.fromDegrees(116.3974, 39.9093, 50000),
          orientation: {
            heading: Cesium.Math.toRadians(0),
            pitch: Cesium.Math.toRadians(-45),
            roll: 0.0
          }
        })

        // 启用光照效果（让地图有立体感）
        viewer.scene.globe.enableLighting = true

        // 如果有 token，添加 OSM Buildings（全球3.5亿建筑）
        if (VITE_CESIUM_ION_TOKEN && !buildingsLoadedRef.current) {
          try {
            const buildingsTileset = await Cesium.createOsmBuildingsAsync();
            viewer.scene.primitives.add(buildingsTileset);
            buildingsLoadedRef.current = true
            console.log('✅ Cesium OSM Buildings 加载成功')
          } catch (error) {
            console.warn('加载 OSM Buildings 失败:', error)
          }
        }

        // 添加示例建筑
        addSampleBuildings(viewer)

        // 加载OSM道路数据
        setTimeout(() => {
          loadOSMRoads(viewer)
        }, 1000) // 延迟1秒加载，避免阻塞初始化

        // 延迟注册 viewer 到 context，确保 Cesium 内部完全初始化
        setTimeout(() => {
          // ✅ 检查viewer是否已被销毁
          if (!viewerRef.current || viewerRef.current.isDestroyed()) {
            console.warn('⚠️ Viewer 已被销毁，取消注册')
            return
          }

          // 验证 viewer 的关键属性是否存在
          try {
            const hasScene = !!(viewer as any).scene
            const hasCamera = !!(viewer as any).camera
            const hasEntities = !!(viewer as any).entities

            if (hasScene && hasCamera && hasEntities) {
              registerViewer(viewer)
              console.log('✅ Cesium Viewer 初始化完成并已注册（scene、camera、entities 都就绪）')
            } else {
              console.warn('⚠️ Viewer 创建但部分属性未就绪:', { hasScene, hasCamera, hasEntities })
              // 即使部分属性未就绪，也尝试注册（让上层决定如何处理）
              registerViewer(viewer)
            }
          } catch (error) {
            console.error('❌ 验证 viewer 属性时出错:', error)
            // ❌ 出错时不注册已销毁的viewer
            console.warn('⚠️ Viewer 验证失败，不注册到 Context')
          }
        }, 200) // 延迟 200ms

      } catch (error) {
        console.error('Cesium初始化失败:', error)
      }
    }

    // 清理函数
    return () => {
      // 清除初始化定时器
      clearTimeout(initTimer)

      if (viewerRef.current) {
        viewerRef.current.destroy()
        viewerRef.current = null
        unregisterViewer()
        console.log('🧹 Cesium Viewer 已清理并从 Context 注销')
      }
    }
  }, []) // ✅ 空依赖数组 - 只运行一次，不会重复初始化

  return (
    <div
      ref={cesiumContainer}
      style={{
        width: '100%',
        height: '100%',
        background: '#1a1a1a',
      }}
    />
  )
}

export default CesiumViewer
