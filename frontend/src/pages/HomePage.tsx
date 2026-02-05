import React, { useState, useEffect, useRef } from 'react'
import { Input, Button, List, Typography, Tag, Spin, message } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons'
import { chatApi } from '../services'

const { TextArea } = Input
const { Text, Title } = Typography

interface Message {
  role: string
  content: string
  created_at: string
  actions?: any[]
  tokens_used?: any
}

const CesiumPlaceholder = () => (
  <div
    id="cesiumContainer"
    style={{
      width: '100%',
      height: 'calc(100vh - 200px)',
      background: '#000',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#fff',
    }}
  >
    <div style={{ textAlign: 'center' }}>
      <Title level={3} style={{ color: '#fff' }}>
        3D数字孪生城市
      </Title>
      <Text style={{ color: '#999' }}>Cesium.js 加载中...</Text>
      <Spin style={{ marginTop: 16 }} />
    </div>
  </div>
)

const HomePage = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | undefined>(undefined)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!inputValue.trim() || loading) return

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

      if (res.data.session_id) {
        setSessionId(res.data.session_id)
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
        <CesiumPlaceholder />
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
                <li>飞到中国尊</li>
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
                        <Tag color="blue" style={{ marginTop: 8 }}>
                          已执行 {msg.actions.length} 个动作
                        </Tag>
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
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入消息，按Enter发送，Shift+Enter换行..."
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
