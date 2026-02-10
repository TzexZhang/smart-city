import React, { useState, useEffect, useRef } from 'react'
import { App } from 'antd'
import { chatApi } from '../services'
import CesiumViewer from '../components/CesiumViewer'
import { ChatContainer } from '../components/chat'
import { SimpleAIActionExecutor } from '../utils/SimpleAIActionExecutor'
import { useCesiumViewer } from '../contexts/CesiumContext'
import { getCurrentPosition, formatPosition } from '../utils/geolocation'

// 注意：TextArea和Title/Text已不再使用，使用ChatContainer组件代替

interface Message {
  role: string
  content: string
  created_at: string
  actions?: any[]
  tokens_used?: any
  executionResult?: {
    success: boolean
    message: string
    data?: {
      results: string[]
      successCount: number
      failedCount: number
    }
  }
}

const HomePage = () => {
  const { message } = App.useApp()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | undefined>(undefined)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const actionExecutorRef = useRef<SimpleAIActionExecutor | null>(null)
  const [userLocation, setUserLocation] = useState<{ latitude: number; longitude: number } | null>(null)
  const [hasLocation, setHasLocation] = useState(false)
  const { viewer, viewerReady } = useCesiumViewer()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 当 viewer ready 时初始化 action executor
  useEffect(() => {
    // 安全地检查 viewer 属性
    const checkViewerState = () => {
      try {
        return {
          viewer存在: !!viewer,
          viewerReady,
          camera存在: viewer ? !!(viewer as any).camera : false,
          scene存在: viewer ? !!(viewer as any).scene : false,
        }
      } catch (error) {
        return {
          viewer存在: !!viewer,
          viewerReady,
          camera存在: false,
          scene存在: false,
          检查错误: true
        }
      }
    }

    const state = checkViewerState()
    console.log('🔍 [Executor初始化检查] 状态:', {
      ...state,
      executor已存在: !!actionExecutorRef.current,
      时间: new Date().toLocaleTimeString()
    })

    // 尝试初始化 executor
    const tryInitExecutor = () => {
      if (!viewer || !viewerReady) return false

      try {
        // 检查 camera 是否可访问
        const hasCamera = !!(viewer as any).camera
        const hasScene = !!(viewer as any).scene

        if (hasCamera && hasScene && !actionExecutorRef.current) {
          actionExecutorRef.current = new SimpleAIActionExecutor(viewer)
          console.log('✅ SimpleAIActionExecutor 已初始化！', new Date().toLocaleTimeString())
          return true
        }
        return false
      } catch (error) {
        console.warn('⚠️ 无法初始化 Executor:', error)
        return false
      }
    }

    // 立即尝试初始化
    if (tryInitExecutor()) {
      return
    }

    // 如果初始化失败，延迟后重试
    if (viewer && viewerReady && !actionExecutorRef.current) {
      console.warn('⚠️ Viewer 就绪但无法立即初始化，延迟重试...')
      setTimeout(() => {
        tryInitExecutor()
      }, 100)

      // 设置轮询检查
      const checkInterval = setInterval(() => {
        if (tryInitExecutor() || actionExecutorRef.current) {
          clearInterval(checkInterval)
        }
      }, 200)

      // 5秒后停止检查
      setTimeout(() => clearInterval(checkInterval), 5000)
    }
  }, [viewer, viewerReady])

  // 额外的监控：确保 executor 在 viewerReady 后被创建
  useEffect(() => {
    if (viewerReady && viewer && !actionExecutorRef.current) {
      const tryInit = () => {
        try {
          const hasCamera = !!(viewer as any).camera
          if (hasCamera && !actionExecutorRef.current) {
            actionExecutorRef.current = new SimpleAIActionExecutor(viewer)
            console.log('✅ Executor 通过备用方法初始化')
            return true
          }
          return false
        } catch {
          return false
        }
      }

      if (!tryInit()) {
        // 延迟后再次尝试
        setTimeout(tryInit, 200)
      }
    }
  }, [viewerReady])

  // Get user's current location
  const handleGetLocation = async () => {
    try {
      message.loading({ content: '正在获取位置...', key: 'location' })

      const result = await getCurrentPosition({
        enableHighAccuracy: true,
        timeout: 10000,
      })

      if (result.success) {
        const { latitude, longitude } = result.position
        setUserLocation({ latitude, longitude })
        setHasLocation(true)
        message.success({
          content: `位置已获取: ${formatPosition(result.position)}`,
          key: 'location',
          duration: 3,
        })

        // Optional: Fly to user's location
        if (actionExecutorRef.current) {
          await actionExecutorRef.current.executeActions([{
            type: 'camera_flyTo',
            parameters: {
              longitude,
              latitude,
              height: 1000,
              duration: 2,
            }
          }])
        }
      } else {
        message.error({
          content: result.error.message,
          key: 'location',
          duration: 5,
        })
      }
    } catch (error: any) {
      message.error({
        content: `获取位置失败: ${error.message}`,
        key: 'location',
      })
    }
  }

  const handleSend = async () => {
    if (!inputValue.trim() || loading) return

    console.log('🚀 [handleSend] 开始发送消息')
    console.log('   当前状态:', {
      viewer: !!viewer,
      viewerReady,
      executor存在: !!actionExecutorRef.current,
      时间: new Date().toLocaleTimeString()
    })

    const userMessage = inputValue.trim()
    setInputValue('')

    // If user location is available and message doesn't contain explicit location, append it
    let finalMessage = userMessage
    if (userLocation && !containsLocationKeywords(userMessage)) {
      finalMessage = `${userMessage}\n\n[我的当前位置: ${userLocation.latitude.toFixed(6)}, ${userLocation.longitude.toFixed(6)}]`
    }

    // 添加用户消息
    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        content: userMessage,
        created_at: new Date().toISOString(),
      },
    ])

    setLoading(true)

    try {
      const res: any = await chatApi.sendMessage({
        session_id: sessionId,
        message: finalMessage,
      })

      console.log('📨 后端响应:', res.data)

      if (res.data.session_id) {
        setSessionId(res.data.session_id)
      }

      // 执行 AI 返回的 actions
      let executionResult: any = undefined
      console.log('🔍 [执行前检查] 状态:', {
        hasActions: !!res.data.actions,
        actionsLength: res.data.actions?.length || 0,
        hasExecutor: !!actionExecutorRef.current
      })

      // 如果 executor 不存在但 viewer 存在，立即初始化
      if (!actionExecutorRef.current && viewer) {
        console.warn('⚠️ Executor 未初始化但 Viewer 存在，立即初始化...')
        actionExecutorRef.current = new SimpleAIActionExecutor(viewer)
        console.log('✅ Executor 已手动初始化')
      }

      if (res.data.actions && res.data.actions.length > 0 && actionExecutorRef.current) {
        console.log('🎯 开始执行 actions:', res.data.actions)
        executionResult = await actionExecutorRef.current.executeActions(res.data.actions)
        console.log('✅ 执行结果:', executionResult)
        message.info(`已执行 ${executionResult.data?.successCount || 0} 个动作`)
      } else {
        if (!res.data.actions || res.data.actions.length === 0) {
          console.warn('⚠️ 后端未返回 actions')
        }
        if (!actionExecutorRef.current) {
          console.error('❌ actionExecutor 未初始化！ viewer:', !!viewer, 'viewerReady:', viewerReady)
        }
      }

      // 添加AI回复
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.data.message.content,
          created_at: new Date().toISOString(),
          actions: res.data.actions,
          tokens_used: res.data.tokens_used,
          executionResult,
        },
      ])
    } catch (error: any) {
      message.error('发送失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  // Helper function to check if message contains location keywords
  const containsLocationKeywords = (text: string): boolean => {
    const locationKeywords = [
      '北京', '上海', '广州', '深圳', '香港', '杭州', '成都',
      'beijing', 'shanghai', 'guangzhou', 'shenzhen', 'hong kong',
      'hangzhou', 'chengdu', '位置', '地点', '坐标', '经纬度',
      'location', 'position', 'coordinate', '这里', 'there'
    ]
    const lowerText = text.toLowerCase()
    return locationKeywords.some(keyword => lowerText.includes(keyword.toLowerCase()))
  }

  return (
    <div style={styles.pageContainer}>
      {/* Cesium 3D地图 */}
      <div style={styles.mapContainer}>
        <CesiumViewer />
      </div>

      {/* AI对话面板 - 使用新的玻璃态UI */}
      <ChatContainer
        messages={messages}
        inputValue={inputValue}
        onInputChange={setInputValue}
        onSend={handleSend}
        loading={loading}
        sessionId={sessionId}
        onGetLocation={handleGetLocation}
        hasLocation={hasLocation}
      />
    </div>
  )
}

// 页面容器样式 - 无滚动条，完美适配视口
const styles = {
  pageContainer: {
    display: 'flex',
    height: '100vh',  // 使用100vh而不是calc，确保适配视口
    width: '100vw',
    overflow: 'hidden',  // 禁止整个页面滚动
    margin: 0,
    padding: 0,
  } as React.CSSProperties,

  mapContainer: {
    flex: 1,  // 占据剩余空间
    minWidth: 0,  // 允许flex子项收缩
    overflow: 'hidden',  // 禁止地图容器滚动
    height: '100%',
  } as React.CSSProperties,
}

export default HomePage
