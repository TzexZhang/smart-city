import { createContext, useContext, ReactNode, useState } from 'react'
import * as Cesium from 'cesium'

// 配置 Cesium Ion Access Token
const VITE_CESIUM_ION_TOKEN = import.meta.env.VITE_CESIUM_ION_TOKEN || ''

if ((Cesium as any).Ion && VITE_CESIUM_ION_TOKEN) {
  (Cesium as any).Ion.defaultAccessToken = VITE_CESIUM_ION_TOKEN
}

interface CesiumContextType {
  viewer: Cesium.Viewer | null
  viewerReady: boolean
  registerViewer: (viewer: Cesium.Viewer) => void
  unregisterViewer: () => void
}

const CesiumContext = createContext<CesiumContextType>({
  viewer: null,
  viewerReady: false,
  registerViewer: () => {},
  unregisterViewer: () => {}
})

export const useCesiumViewer = () => useContext(CesiumContext)

export const CesiumProvider = ({ children }: { children: ReactNode }) => {
  const [viewer, setViewer] = useState<Cesium.Viewer | null>(null)
  const [viewerReady, setViewerReady] = useState(false)

  // 提供一个方法让 CesiumViewer 组件注册 viewer
  const registerViewer = (cesiumViewer: Cesium.Viewer) => {
    if (!viewer) {
      setViewer(cesiumViewer)
      setViewerReady(true)
      console.log('✅ Viewer 已注册到 Context', new Date().toLocaleTimeString())
    }
  }

  const unregisterViewer = () => {
    if (viewer) {
      viewer.destroy()
      setViewer(null)
      setViewerReady(false)
      console.log('🧹 Viewer 已从 Context 注销')
    }
  }

  return (
    <CesiumContext.Provider value={{ viewer, viewerReady, registerViewer, unregisterViewer }}>
      {children}
    </CesiumContext.Provider>
  )
}
