import React from 'react'
import { List } from 'antd'
import ChatMessage from './ChatMessage'
import { RobotOutlined } from '@ant-design/icons'

export interface Message {
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

interface MessageListProps {
  messages: Message[]
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  if (messages.length === 0) {
    return (
      <div style={styles.emptyState}>
        <RobotOutlined style={styles.emptyIcon} />
        <p style={styles.emptyText}>你好！我是智慧城市AI助手</p>
        <p style={styles.emptySubtext}>你可以问我：</p>
        <ul style={styles.emptyList}>
          <li>飞到中国</li>
          <li>显示朝阳区200米以上的建筑</li>
          <li>当前北京的天气怎么样？</li>
          <li>分析周边1公里的建筑</li>
        </ul>
      </div>
    )
  }

  return (
    <List
      dataSource={messages}
      renderItem={(msg, index) => (
        <ChatMessage
          key={index}
          message={msg}
        />
      )}
    />
  )
}

const styles: Record<string, React.CSSProperties> = {
  emptyState: {
    textAlign: 'center' as const,
    marginTop: 100,
    color: '#666',
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 24,
    color: '#1890ff',
    opacity: 0.8,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 500,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    marginBottom: 16,
  },
  emptyList: {
    textAlign: 'left' as const,
    display: 'inline-block',
    fontSize: 14,
    lineHeight: '24px',
  },
}

export default MessageList
