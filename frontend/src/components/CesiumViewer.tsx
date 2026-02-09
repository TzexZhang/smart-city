import { useEffect, useRef, useState } from 'react'
import * as Cesium from 'cesium'
import MapLayerControl from './MapLayerControl'

// 配置 Cesium Ion Access Token
// 请在 https://ion.cesium.com/tokens 获取您的免费 token
const VITE_CESIUM_ION_TOKEN = import.meta.env.VITE_CESIUM_ION_TOKEN || ''

if ((Cesium as any).Ion && VITE_CESIUM_ION_TOKEN) {
  (Cesium as any).Ion.defaultAccessToken = VITE_CESIUM_ION_TOKEN
}

const CesiumViewer = () => {
  const cesiumContainer = useRef<HTMLDivElement>(null)
  const viewerRef = useRef<Cesium.Viewer | null>(null)
  const [buildingsLoaded, setBuildingsLoaded] = useState(false)

  useEffect(() => {
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
        if (VITE_CESIUM_ION_TOKEN && !buildingsLoaded) {
          try {
            const buildingsTileset = await Cesium.createOsmBuildingsAsync();
            viewer.scene.primitives.add(buildingsTileset);
            setBuildingsLoaded(true)
            console.log('✅ Cesium OSM Buildings 加载成功')
          } catch (error) {
            console.warn('加载 OSM Buildings 失败:', error)
          }
        }

        // 添加示例建筑
        addSampleBuildings(viewer)

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
      }
    }
  }, [buildingsLoaded])

  return (
    <>
      {viewerRef.current?.scene?.globe && (
        <MapLayerControl viewer={viewerRef.current} currentCity="北京" />
      )}
      <div
        ref={cesiumContainer}
        style={{
          width: '100%',
          height: '100%',
          background: '#1a1a1a',
        }}
      />
    </>
  )
}

export default CesiumViewer
