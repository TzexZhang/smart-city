import React, { useEffect, useRef } from 'react'
import { Typography } from 'antd'
import MessageList, { Message } from './MessageList'
import ChatInput from './ChatInput'
import TypingIndicator from './TypingIndicator'

const { Title } = Typography

interface ChatContainerProps {
  messages: Message[]
  inputValue: string
  onInputChange: (value: string) => void
  onSend: () => void
  loading?: boolean
  sessionId?: string
  onGetLocation?: () => void
  hasLocation?: boolean
}

const ChatContainer: React.FC<ChatContainerProps> = ({
  messages,
  inputValue,
  onInputChange,
  onSend,
  loading = false,
  sessionId,
  onGetLocation,
  hasLocation = false,
}) => {
  const messagesAreaRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    if (messagesAreaRef.current) {
      messagesAreaRef.current.scrollTop = messagesAreaRef.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  // Calculate total tokens
  const totalTokens = messages.reduce(
    (sum, m) => sum + (m.tokens_used?.total_tokens || 0),
    0
  )

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <Title level={4} style={styles.headerTitle}>
          <span style={styles.headerIcon}>🤖</span>
          智慧城市AI助手
        </Title>
        {sessionId && (
          <div style={styles.sessionInfo}>
            <span style={styles.sessionDot} />
            会话已连接
          </div>
        )}
      </div>

      {/* Messages Area */}
      <div ref={messagesAreaRef} style={styles.messagesArea}>
        <MessageList messages={messages} />
        {loading && <TypingIndicator visible />}
      </div>

      {/* Token Usage Display */}
      {totalTokens > 0 && (
        <div style={styles.tokenBar}>
          总消耗: {totalTokens.toLocaleString()} tokens
        </div>
      )}

      {/* Input Area */}
      <ChatInput
        value={inputValue}
        onChange={onInputChange}
        onSend={onSend}
        loading={loading}
        onGetLocation={onGetLocation}
        hasLocation={hasLocation}
      />
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    width: '420px',  // 设置固定宽度，让对话框更宽敞
    flexShrink: 0,  // 防止被压缩
    background: 'rgba(255, 255, 255, 0.85)',
    backdropFilter: 'blur(20px)',
    borderLeft: '1px solid rgba(255, 255, 255, 0.3)',
    boxShadow: '-4px 0 24px rgba(0, 0, 0, 0.08)',
    overflow: 'hidden',  // 禁止容器滚动
  },
  header: {
    padding: '20px 24px',
    borderBottom: '1px solid rgba(0, 0, 0, 0.06)',
    background: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(20px)',
    flexShrink: 0,  // 防止头部被压缩
  },
  headerTitle: {
    margin: 0,
    display: 'flex',
    alignItems: 'center',
    color: '#1a1a1a',
  },
  headerIcon: {
    marginRight: 8,
  },
  sessionInfo: {
    display: 'flex',
    alignItems: 'center',
    fontSize: 12,
    color: '#52c41a',
    marginTop: 8,
  },
  sessionDot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    background: '#52c41a',
    marginRight: 6,
    animation: 'pulse 2s infinite',
  },
  messagesArea: {
    flex: 1,
    overflowY: 'auto' as 'auto',  // 允许滚动
    padding: '20px 24px',
    background: 'rgba(250, 250, 250, 0.5)',
    backdropFilter: 'blur(10px)',
    // 隐藏滚动条但保留滚动功能
    scrollbarWidth: 'none' as 'none',  // Firefox
    msOverflowStyle: 'none' as 'none',  // IE/Edge
  } as React.CSSProperties,
  tokenBar: {
    padding: '8px 24px',
    borderTop: '1px solid rgba(0, 0, 0, 0.06)',
    fontSize: 12,
    color: '#666',
    background: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(20px)',
    flexShrink: 0,  // 防止token bar被压缩
  },
}

export default ChatContainer
