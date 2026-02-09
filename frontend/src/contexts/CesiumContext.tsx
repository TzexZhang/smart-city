import { createContext, useContext, ReactNode, useRef, useState, useEffect } from 'react'
import * as Cesium from 'cesium'

// 配置 Cesium Ion Access Token
const VITE_CESIUM_ION_TOKEN = import.meta.env.VITE_CESIUM_ION_TOKEN || ''

if ((Cesium as any).Ion && VITE_CESIUM_ION_TOKEN) {
  (Cesium as any).Ion.defaultAccessToken = VITE_CESIUM_ION_TOKEN
}

interface CesiumContextType {
  viewer: Cesium.Viewer | null
  viewerReady: boolean
}

const CesiumContext = createContext<CesiumContextType>({
  viewer: null,
  viewerReady: false
})

export const useCesiumViewer = () => useContext(CesiumContext)

export const CesiumProvider = ({ children }: { children: ReactNode }) => {
  const [viewer, setViewer] = useState<Cesium.Viewer | null>(null)
  const [viewerReady, setViewerReady] = useState(false)
  const cesiumContainerRef = useRef<HTMLDivElement>(null)
  const [buildingsLoaded, setBuildingsLoaded] = useState(false)

  useEffect(() => {
    if (!cesiumContainerRef.current) return

    /**
     * 添加示例建筑
     */
    const addSampleBuildings = (cesiumViewer: Cesium.Viewer) => {
      try {
        const viewerPosition = Cesium.Cartesian3.fromDegrees(116.3974, 39.9093, 0)

        // 添加中国
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
        positions.push(positions[0])

        cesiumViewer.entities.add({
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

          cesiumViewer.entities.add({
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
        // 创建 Viewer 配置
        const viewerOptions: any = {
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

        // 如果有 token，使用 Cesium World Terrain
        if (VITE_CESIUM_ION_TOKEN) {
          viewerOptions.terrainProvider = await Cesium.CesiumTerrainProvider.fromIonAssetId(1, {
            requestVertexNormals: true,
            requestWaterMask: true,
          })
        } else {
          viewerOptions.terrainProvider = new Cesium.EllipsoidTerrainProvider()
        }

        // 创建Cesium Viewer
        const cesiumViewer = new Cesium.Viewer(cesiumContainerRef.current as HTMLElement, viewerOptions)

        // 添加高德地图作为主底图
        const amapImageryProvider = new Cesium.UrlTemplateImageryProvider({
          url: 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
          minimumLevel: 3,
          maximumLevel: 18,
          credit: '高德地图',
        })
        cesiumViewer.imageryLayers.addImageryProvider(amapImageryProvider)

        // 如果有 token，添加全球卫星影像
        if (VITE_CESIUM_ION_TOKEN) {
          try {
            const ionImagery = await Cesium.IonImageryProvider.fromAssetId(2)
            const ionLayer = cesiumViewer.imageryLayers.addImageryProvider(ionImagery, 1)
            ionLayer.alpha = 0.3
          } catch (error) {
            console.warn('无法加载 Cesium Ion 影像')
          }
        }

        // 设置初始视角到北京
        cesiumViewer.camera.setView({
          destination: Cesium.Cartesian3.fromDegrees(116.3974, 39.9093, 50000),
          orientation: {
            heading: Cesium.Math.toRadians(0),
            pitch: Cesium.Math.toRadians(-45),
            roll: 0.0
          }
        })

        // 启用光照效果
        cesiumViewer.scene.globe.enableLighting = true

        // 如果有 token，添加 OSM Buildings
        if (VITE_CESIUM_ION_TOKEN && !buildingsLoaded) {
          try {
            const buildingsTileset = await Cesium.createOsmBuildingsAsync()
            cesiumViewer.scene.primitives.add(buildingsTileset)
            setBuildingsLoaded(true)
            console.log('✅ Cesium OSM Buildings 加载成功')
          } catch (error) {
            console.warn('加载 OSM Buildings 失败:', error)
          }
        }

        // 添加示例建筑
        addSampleBuildings(cesiumViewer)

        setViewer(cesiumViewer)
        setViewerReady(true)

      } catch (error) {
        console.error('Cesium初始化失败:', error)
      }
    }

    initCesium()

    // 清理函数
    return () => {
      if (viewer) {
        viewer.destroy()
        setViewer(null)
        setViewerReady(false)
      }
    }
  }, [buildingsLoaded])

  return (
    <CesiumContext.Provider value={{ viewer, viewerReady }}>
      <div
        ref={cesiumContainerRef}
        style={{
          width: '100%',
          height: '100%',
          background: '#1a1a1a',
        }}
      />
      {children}
    </CesiumContext.Provider>
  )
}
