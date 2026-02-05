import { useEffect, useRef } from 'react'
import * as Cesium from 'cesium'

// 完全禁用Cesium Ion服务（不使用任何在线资源）
(Cesium as any).Ion.defaultAccessToken = ''

const CesiumViewer = () => {
  const cesiumContainer = useRef<HTMLDivElement>(null)
  const viewerRef = useRef<Cesium.Viewer | null>(null)

  useEffect(() => {
    if (!cesiumContainer.current) return

    try {
      // 创建Cesium Viewer，禁用所有在线服务
      const viewer = new Cesium.Viewer(cesiumContainer.current, {
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
        // 禁用地形服务
        terrainProvider: new Cesium.EllipsoidTerrainProvider(),
        // 禁用 imagery 层
        imageryProviderViewModels: [],
      })

      viewerRef.current = viewer

      // 设置初始视角到北京
      viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(116.3974, 39.9093, 50000),
        orientation: {
          heading: Cesium.Math.toRadians(0),
          pitch: Cesium.Math.toRadians(-45),
          roll: 0.0
        }
      })

      // 设置地球为深色模式
      viewer.scene.globe.baseColor = Cesium.Color.BLACK
      viewer.scene.globe.tileCacheSize = 0 // 减少缓存

      // 禁用大气和天空效果
      if (viewer.scene.skyBox) {
        viewer.scene.skyBox.show = false
      }
      if (viewer.scene.skyAtmosphere) {
        viewer.scene.skyAtmosphere.show = false
      }
      if (viewer.scene.fog) {
        viewer.scene.fog.enabled = false
      }
      if (viewer.scene.sun) {
        viewer.scene.sun.show = false
      }
      if (viewer.scene.moon) {
        viewer.scene.moon.show = false
      }

      // 添加一些示例建筑（使用简单的盒子）
      const viewerPosition = Cesium.Cartesian3.fromDegrees(116.3974, 39.9093, 0)

      // 添加中国尊（模拟）
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
        name: '中国尊',
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

    } catch (error) {
      console.error('Cesium初始化失败:', error)
    }

    // 清理函数
    return () => {
      if (viewerRef.current) {
        viewerRef.current.destroy()
        viewerRef.current = null
      }
    }
  }, [])

  return (
    <div
      ref={cesiumContainer}
      style={{
        width: '100%',
        height: '100%',
        background: '#000',
      }}
    />
  )
}

export default CesiumViewer
