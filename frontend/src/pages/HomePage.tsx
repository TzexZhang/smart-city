import React, { useState, useEffect, useRef } from 'react'
import { Input, Button, List, Typography, Tag, message, Collapse, Card, Space } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined, CheckCircleOutlined, QuestionCircleOutlined } from '@ant-design/icons'
import { chatApi } from '../services'
import CesiumViewer from '../components/CesiumViewer'
import { SimpleAIActionExecutor } from '../utils/SimpleAIActionExecutor'
import { useCesiumViewer } from '../contexts/CesiumContext'

const { TextArea } = Input
const { Title, Text } = Typography

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
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | undefined>(undefined)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const actionExecutorRef = useRef<SimpleAIActionExecutor | null>(null)
  const [showCommandHints, setShowCommandHints] = useState(false)
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
        message: userMessage,
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

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 64px)' }}>
      {/* Cesium 3D地图 */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <CesiumViewer />
      </div>

      {/* AI对话面板 */}
      <div
        style={{
          width: 400,
          display: 'flex',
          flexDirection: 'column',
          background: '#fff',
          borderLeft: '1px solid #d9d9d9',
        }}
      >
        <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
          <Title level={4} style={{ margin: 0 }}>
            AI对话控制
          </Title>
        </div>

        {/* 消息列表 */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '16px',
            background: '#fafafa',
          }}
        >
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', marginTop: 100, color: '#999' }}>
              <RobotOutlined style={{ fontSize: 48, marginBottom: 16 }} />
              <p>你好！我是智慧城市AI助手</p>
              <p>你可以问我：</p>
              <ul style={{ textAlign: 'left', display: 'inline-block' }}>
                <li>飞到中国</li>
                <li>显示朝阳区200米以上的建筑</li>
                <li>当前北京的天气怎么样？</li>
              </ul>
            </div>
          ) : (
            <List
              dataSource={messages}
              renderItem={(msg) => (
                <List.Item style={{ border: 'none', padding: '8px 0' }}>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    }}
                  >
                    <div
                      style={{
                        maxWidth: '80%',
                        padding: '12px',
                        borderRadius: 8,
                        background: msg.role === 'user' ? '#1890ff' : '#f0f0f0',
                        color: msg.role === 'user' ? '#fff' : '#000',
                      }}
                    >
                      <div style={{ fontSize: 12, marginBottom: 4 }}>
                        {msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                        <span style={{ marginLeft: 4 }}>
                          {msg.role === 'user' ? '我' : 'AI'}
                        </span>
                      </div>
                      <div>{msg.content}</div>
                      {msg.tokens_used && (
                        <div
                          style={{
                            fontSize: 10,
                            opacity: 0.7,
                            marginTop: 4,
                          }}
                        >
                          Tokens: {msg.tokens_used.total_tokens}
                        </div>
                      )}
                      {msg.actions && msg.actions.length > 0 && (
                        <div style={{ marginTop: 8 }}>
                          <Tag color="blue" icon={<CheckCircleOutlined />}>
                            AI 返回 {msg.actions.length} 个动作
                          </Tag>
                          {msg.executionResult && msg.executionResult.data && (
                            <>
                              <Text style={{ fontSize: 11, marginLeft: 8 }}>
                                成功: {msg.executionResult.data.successCount}
                              </Text>
                              {msg.executionResult.data.failedCount > 0 && (
                                <Text style={{ fontSize: 11, marginLeft: 8, color: '#ff4d4f' }}>
                                  失败: {msg.executionResult.data.failedCount}
                                </Text>
                              )}
                            </>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </List.Item>
              )}
            />
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Token统计 */}
        {messages.some((m) => m.tokens_used) && (
          <div
            style={{
              padding: '8px 16px',
              borderTop: '1px solid #f0f0f0',
              fontSize: 12,
              color: '#666',
            }}
          >
            总消耗: {messages.reduce((sum, m) => sum + (m.tokens_used?.total_tokens || 0), 0)}{' '}
            tokens
          </div>
        )}

        {/* 输入框 */}
        <div style={{ padding: '16px', borderTop: '1px solid #f0f0f0' }}>
          {/* 指令提示按钮 */}
          <div style={{ marginBottom: 12 }}>
            <Button
              icon={<QuestionCircleOutlined />}
              onClick={() => setShowCommandHints(!showCommandHints)}
              block
              style={{ marginBottom: showCommandHints ? 8 : 0 }}
            >
              {showCommandHints ? '隐藏' : '显示'}AI指令提示
            </Button>

            {showCommandHints && (
              <Card
                size="small"
                style={{
                  marginTop: 8,
                  maxHeight: 300,
                  overflow: 'auto',
                  background: '#f6ffed',
                  borderColor: '#b7eb8f'
                }}
              >
                <Space direction="vertical" style={{ width: '100%' }} size={8}>
                  <div style={{ fontWeight: 'bold', color: '#389e0d' }}>
                    <QuestionCircleOutlined style={{ marginRight: 8 }} />
                    支持的AI指令
                  </div>

                  <Collapse
                    size="small"
                    items={[
                      {
                        key: 'camera',
                        label: <span style={{ fontWeight: 500 }}>📍 摄像机控制</span>,
                        children: (
                          <div style={{ fontSize: 12, color: '#666', marginLeft: 8 }}>
                            <div>• "飞行到北京"</div>
                            <div>• "跳转到上海浦东"</div>
                            <div>• "俯视深圳"</div>
                            <div>• "view Beijing from north"</div>
                          </div>
                        ),
                      },
                      {
                        key: 'building',
                        label: <span style={{ fontWeight: 500 }}>🏢 建筑查询</span>,
                        children: (
                          <div style={{ fontSize: 12, color: '#666', marginLeft: 8 }}>
                            <div>• "查询北京的高层建筑"</div>
                            <div>• "找出风险等级高的建筑"</div>
                            <div>• "统计上海的建筑类型"</div>
                            <div>• "show buildings over 100m"</div>
                          </div>
                        ),
                      },
                      {
                        key: 'layer',
                        label: <span style={{ fontWeight: 500 }}>🗺️ 图层控制</span>,
                        children: (
                          <div style={{ fontSize: 12, color: '#666', marginLeft: 8 }}>
                            <div>• "切换到卫星影像"</div>
                            <div>• "显示地形图"</div>
                            <div>• "switch to satellite view"</div>
                            <div>• "turn on 3D buildings"</div>
                          </div>
                        ),
                      },
                      {
                        key: 'analysis',
                        label: <span style={{ fontWeight: 500 }}>📊 空间分析</span>,
                        children: (
                          <div style={{ fontSize: 12, color: '#666', marginLeft: 8 }}>
                            <div>• "分析周边1公里的建筑"</div>
                            <div>• "测量从这里到那里的距离"</div>
                            <div>• "buffer 500m around point"</div>
                            <div>• "measure distance A to B"</div>
                          </div>
                        ),
                      },
                      {
                        key: 'data',
                        label: <span style={{ fontWeight: 500 }}>📦 数据加载</span>,
                        children: (
                          <div style={{ fontSize: 12, color: '#666', marginLeft: 8 }}>
                            <div>• "加载香港3D数据"</div>
                            <div>• "显示北京精细建筑"</div>
                            <div>• "load Hong Kong 3D model"</div>
                            <div>• "open Shanghai detailed data"</div>
                          </div>
                        ),
                      },
                      {
                        key: 'other',
                        label: <span style={{ fontWeight: 500 }}>🔄 其他</span>,
                        children: (
                          <div style={{ fontSize: 12, color: '#666', marginLeft: 8 }}>
                            <div>• "重置视图"</div>
                            <div>• "导出截图"</div>
                            <div>• "reset view"</div>
                            <div>• "export screenshot"</div>
                          </div>
                        ),
                      },
                    ]}
                  />
                </Space>
              </Card>
            )}
          </div>

          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              showCommandHints
                ? "试试：飞行到北京 / 查询高层建筑 / 切换卫星影像"
                : "输入消息，按Enter发送，Shift+Enter换行..."
            }
            autoSize={{ minRows: 3, maxRows: 6 }}
            disabled={loading}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={loading}
            style={{ marginTop: 8 }}
            block
          >
            发送
          </Button>
        </div>
      </div>
    </div>
  )
}

export default HomePage
