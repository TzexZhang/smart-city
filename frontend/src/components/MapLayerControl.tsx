import React, { useState, useEffect } from 'react'
import { Button, Dropdown, Space, Divider } from 'antd'
import {
  PictureOutlined,
  GlobalOutlined,
  BuildOutlined,
  CameraOutlined,
  BgColorsOutlined,
  EnvironmentOutlined,
} from '@ant-design/icons'
import * as Cesium from 'cesium'

export interface MapLayerConfig {
  id: string
  name: string
  icon: React.ReactNode
  provider: () => Cesium.ImageryProvider | Promise<Cesium.ImageryProvider>
  description: string
}

interface MapLayerControlProps {
  viewer: Cesium.Viewer | null
  currentCity?: string
}

export const MapLayerControl: React.FC<MapLayerControlProps> = ({ viewer, currentCity = '北京' }) => {
  const [currentLayer, setCurrentLayer] = useState<string>('amap')
  const [viewerReady, setViewerReady] = useState<boolean>(false)

  // 监听 viewer 状态 - 只检查 viewer 是否存在，不访问深层属性
  useEffect(() => {
    // 完全不访问 scene，只检查 viewer 对象本身
    const hasViewer = viewer != null && typeof viewer === 'object'

    if (hasViewer) {
      console.log('✅ MapLayerControl: Viewer 对象已传入')
      // 延迟设置 ready 状态，确保 scene 已初始化
      const timer = setTimeout(() => {
        setViewerReady(true)
      }, 100)
      return () => clearTimeout(timer)
    } else {
      console.log('⏳ MapLayerControl: 等待 Viewer 对象...')
      setViewerReady(false)
    }
  }, [viewer])

  // 定义所有底图配置
  const mapLayers: MapLayerConfig[] = [
    {
      id: 'amap',
      name: '矢量地图',
      icon: <GlobalOutlined />,
      description: '标准矢量地图，清晰显示道路和建筑',
      provider: () => new Cesium.UrlTemplateImageryProvider({
        url: 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
        minimumLevel: 3,
        maximumLevel: 18,
        credit: '高德地图',
      }),
    },
    {
      id: 'satellite',
      name: '卫星影像',
      icon: <PictureOutlined />,
      description: '真实卫星影像，直观展示地理环境',
      provider: () => new Cesium.UrlTemplateImageryProvider({
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        maximumLevel: 18,
        credit: 'ArcGIS World Imagery',
      }),
    },
    {
      id: 'terrain',
      name: '地形图',
      icon: <EnvironmentOutlined />,
      description: '突出地形起伏，适合分析地势',
      provider: () => new Cesium.UrlTemplateImageryProvider({
        url: 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
        minimumLevel: 3,
        maximumLevel: 18,
        credit: '高德地形图',
      }),
    },
    {
      id: 'building',
      name: '建筑白模',
      icon: <BuildOutlined />,
      description: '简洁建筑轮廓，突出城市结构',
      provider: () => new Cesium.UrlTemplateImageryProvider({
        url: 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=9&x={x}&y={y}&z={z}',
        minimumLevel: 3,
        maximumLevel: 18,
        credit: '高德建筑白模',
      }),
    },
    {
      id: 'realistic',
      name: '三维实景',
      icon: <CameraOutlined />,
      description: '倾斜摄影实景，真实还原城市',
      provider: () => {
        const token = import.meta.env.VITE_CESIUM_ION_TOKEN
        if (!token) {
          console.warn('未配置 Cesium Ion Token，无法加载三维实景')
          throw new Error('三维实景需要 Cesium Ion Token')
        }
        return Cesium.IonImageryProvider.fromAssetId(2)
      },
    },
    {
      id: 'artistic',
      name: '艺术风格',
      icon: <BgColorsOutlined />,
      description: '艺术化渲染，适合展示和演示',
      provider: () => new Cesium.UrlTemplateImageryProvider({
        url: 'https://tiles.stadiamaps.com/stamen_toner/{z}/{x}/{y}.png',
        minimumLevel: 0,
        maximumLevel: 20,
        credit: 'Stamen Toner',
      }),
    },
  ]

  // 切换底图
  const switchLayer = async (layerConfig: MapLayerConfig) => {
    try {
      // 使用可选链安全检查，如果 viewer 未就绪直接返回
      if (!viewer?.imageryLayers) {
        console.error('❌ Viewer 未就绪，无法切换底图')
        console.log('viewer 存在:', !!viewer)
        console.log('imageryLayers 存在:', !!viewer?.imageryLayers)
        return
      }

      console.log(`正在切换到 ${layerConfig.name}...`)

      // 移除所有现有图层
      viewer.imageryLayers.removeAll()

      // 添加新的底图
      const provider = await layerConfig.provider()
      viewer.imageryLayers.addImageryProvider(provider)

      // 如果是三维实景，添加一些额外的视觉效果（使用可选链）
      if (layerConfig.id === 'realistic') {
        try {
          if (viewer?.scene?.globe) {
            viewer.scene.globe.enableLighting = true
          }
        } catch (sceneError) {
          console.warn('⚠️ 无法设置 lighting 效果:', sceneError)
        }
      }

      setCurrentLayer(layerConfig.id)
      console.log(`✅ 已切换到 ${layerConfig.name}`)
    } catch (error) {
      console.error(`❌ 切换底图失败:`, error)
      // 如果切换失败，尝试恢复默认底图
      try {
        if (viewer?.imageryLayers) {
          const defaultProvider = await mapLayers[0].provider()
          viewer.imageryLayers.addImageryProvider(defaultProvider)
          setCurrentLayer('amap')
          console.log('✅ 已恢复默认底图')
        }
      } catch (retryError) {
        console.error('❌ 恢复默认底图也失败:', retryError)
      }
    }
  }

  const items = mapLayers.map((layer) => ({
    key: layer.id,
    label: (
      <div>
        <Space>
          {layer.icon}
          <span>{layer.name}</span>
        </Space>
        <div style={{ fontSize: '12px', color: '#999', marginLeft: '24px' }}>
          {layer.description}
        </div>
      </div>
    ),
    onClick: () => switchLayer(layer),
  }))

  // 获取当前底图名称
  const getCurrentLayerName = () => {
    const layer = mapLayers.find((l) => l.id === currentLayer)
    return layer?.name || '未知底图'
  }

  return (
    <div
      style={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        zIndex: 1000,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        padding: '12px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        minWidth: '200px',
      }}
    >
      <div style={{ marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
        <EnvironmentOutlined style={{ marginRight: '8px' }} />
        当前城市: {currentCity}
      </div>
      <Divider style={{ margin: '8px 0' }} />
      <div style={{ marginBottom: '8px', fontSize: '13px', color: '#666' }}>
        底图: {getCurrentLayerName()}
      </div>
      {!viewerReady && (
        <div style={{ marginBottom: '8px', fontSize: '12px', color: '#faad14' }}>
          ⏳ 地图初始化中...
        </div>
      )}
      <Dropdown
        menu={{ items }}
        trigger={['click']}
        disabled={!viewerReady}
      >
        <Button
          type="primary"
          block
          icon={<BgColorsOutlined />}
          disabled={!viewerReady}
        >
          切换底图
        </Button>
      </Dropdown>
    </div>
  )
}

export default MapLayerControl
