import React, { useState } from 'react'
import { Tag, Typography, Collapse, Descriptions, Card, Alert } from 'antd'
import { RobotOutlined, UserOutlined, CheckCircleOutlined, CloudOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import { Message } from './MessageList'

const { Text } = Typography

interface ChatMessageProps {
  message: Message
}

// 解析执行结果的内容
const parseExecutionResult = (executionResult?: Message['executionResult']) => {
  if (!executionResult?.data?.results) return null

  const results = executionResult.data.results
  const rawData = executionResult.data // 原始数据
  const parsedData: any = {
    weather: null,
    flyTo: null,
    analysis: null,
    others: []
  }

  results.forEach((result: string) => {
    // 解析天气数据 - 优先从原始数据获取
    if (result.includes('获取天气成功') || result.includes('当前天气') || result.includes('℃') || result.includes('温度')) {
      // 尝试从原始数据中提取天气信息
      const weatherData = (rawData as any)?.weatherData || {}

      parsedData.weather = {
        city: weatherData.city || weatherData.name || '未知城市',
        temperature: weatherData.temperature !== undefined ? weatherData.temperature : 'N/A',
        condition: weatherData.description || getConditionName(weatherData.condition) || '未知',
        humidity: weatherData.humidity,
        windSpeed: weatherData.wind_speed,
        raw: result
      }
    }
    // 解析飞行结果
    else if (result.includes('已飞行到') || result.includes('flyTo')) {
      parsedData.flyTo = result
    }
    // 解析分析结果
    else if (result.includes('分析') || result.includes('建筑') || result.includes('周边')) {
      parsedData.analysis = result
    }
    // 其他结果
    else {
      parsedData.others.push(result)
    }
  })

  return parsedData
}

// 获取天气状况中文名
const getConditionName = (condition: string): string | null => {
  const conditionMap: Record<string, string> = {
    'Clear': '晴',
    'Clouds': '多云',
    'Rain': '雨',
    'Drizzle': '小雨',
    'Thunderstorm': '雷阵雨',
    'Snow': '雪',
    'Mist': '薄雾',
    'Fog': '雾',
    'Haze': '霾'
  }
  return conditionMap[condition] || null
}

// 天气结果显示组件
const WeatherResult: React.FC<{ data: any }> = ({ data }) => (
  <Card
    size="small"
    style={{
      marginTop: 12,
      background: 'linear-gradient(135deg, #e6f7ff 0%, #f0f9ff 100%)',
      border: '1px solid #91d5ff',
      borderRadius: 8
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
      <CloudOutlined style={{ fontSize: 20, color: '#1890ff', marginRight: 8 }} />
      <Text strong style={{ color: '#0050b3' }}>天气信息</Text>
    </div>
    <Descriptions size="small" column={1}>
      <Descriptions.Item label="城市">{data.city}</Descriptions.Item>
      <Descriptions.Item label="温度">
        <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#fa8c16' }}>
          {data.temperature}°C
        </Text>
      </Descriptions.Item>
      <Descriptions.Item label="天气状况">{data.condition}</Descriptions.Item>
    </Descriptions>
  </Card>
)

// 执行结果展示组件
const ExecutionResultDisplay: React.FC<{ executionResult?: Message['executionResult'] }> = ({ executionResult }) => {
  const [expanded, setExpanded] = useState(false)

  if (!executionResult?.data?.results) return null

  const parsedData = parseExecutionResult(executionResult)
  const { weather, flyTo, analysis, others } = parsedData || {}

  const collapseItems = [
    {
      key: '1',
      label: (
        <span style={{ fontSize: 13, color: '#666' }}>
          {executionResult.success ? '✅' : '⚠️'} 执行详情 ({executionResult.data?.successCount || 0}/{executionResult.data?.results?.length || 0})
        </span>
      ),
      children: (
        <div style={{
          fontSize: 12,
          color: '#666',
          lineHeight: '20px',
          maxHeight: '300px',
          overflowY: 'auto',
          paddingRight: '8px'
        }}>
          {flyTo && (
            <Alert
              message="飞行操作"
              description={flyTo}
              type="success"
              showIcon
              style={{ marginBottom: 8 }}
            />
          )}
          {analysis && (
            <Alert
              message="分析结果"
              description={analysis}
              type="info"
              showIcon
              style={{ marginBottom: 8 }}
            />
          )}
          {others.map((other: string, idx: number) => (
            <div key={idx} style={{ padding: '4px 0', borderBottom: '1px solid #f0f0f0' }}>
              {other}
            </div>
          ))}
        </div>
      ),
    },
  ]

  return (
    <div style={{ marginTop: 12 }}>
      {/* 天气结果 - 始终显示 */}
      {weather && <WeatherResult data={weather} />}

      {/* 其他结果 - 可折叠 */}
      {(flyTo || analysis || others.length > 0) && (
        <Collapse
          ghost
          activeKey={expanded ? ['1'] : undefined}
          onChange={(keys) => setExpanded(keys.includes('1' as never))}
          items={collapseItems}
          style={{ marginTop: 8 }}
        />
      )}
    </div>
  )
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={styles.container}
    >
      <div
        style={{
          ...styles.messageWrapper,
          justifyContent: isUser ? 'flex-end' : 'flex-start',
        }}
      >
        <div
          style={{
            ...styles.messageBubble,
            ...(isUser ? styles.userBubble : styles.assistantBubble),
          }}
        >
          {/* Message Header */}
          <div style={styles.messageHeader}>
            {isUser ? <UserOutlined /> : <RobotOutlined />}
            <span style={styles.senderName}>
              {isUser ? '我' : 'AI助手'}
            </span>
          </div>

          {/* Message Content */}
          <div style={styles.messageContent}>
            {isUser ? (
              <div>{message.content}</div>
            ) : (
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p style={styles.markdownParagraph}>{children}</p>,
                  ul: ({ children }) => <ul style={styles.markdownList}>{children}</ul>,
                  ol: ({ children }) => <ol style={styles.markdownList}>{children}</ol>,
                  li: ({ children }) => <li style={styles.markdownListItem}>{children}</li>,
                  code: ({ inline, children }: any) =>
                    inline ? (
                      <code style={styles.inlineCode}>{children}</code>
                    ) : (
                      <code style={styles.blockCode}>{children}</code>
                    ),
                  strong: ({ children }) => <strong style={styles.boldText}>{children}</strong>,
                }}
              >
                {message.content}
              </ReactMarkdown>
            )}
          </div>

          {/* Token Usage */}
          {message.tokens_used && (
            <div style={styles.tokenInfo}>
              Tokens: {message.tokens_used.total_tokens}
            </div>
          )}

          {/* Actions Info */}
          {message.actions && message.actions.length > 0 && (
            <div style={styles.actionsInfo}>
              <Tag color="blue" icon={<CheckCircleOutlined />} style={styles.actionTag}>
                AI 返回 {message.actions.length} 个动作
              </Tag>
              {message.executionResult?.data && (
                <>
                  <Text style={styles.executionText}>
                    成功: {message.executionResult.data.successCount}
                  </Text>
                  {message.executionResult.data.failedCount > 0 && (
                    <Text style={{ ...styles.executionText, color: '#ff4d4f' }}>
                      失败: {message.executionResult.data.failedCount}
                    </Text>
                  )}
                </>
              )}
            </div>
          )}

          {/* Execution Result Display */}
          {!isUser && <ExecutionResultDisplay executionResult={message.executionResult} />}
        </div>
      </div>
    </motion.div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    marginBottom: 16,
  },
  messageWrapper: {
    display: 'flex',
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '75%',
    padding: '16px 20px',
    borderRadius: 16,
    wordBreak: 'break-word' as const,
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
  },
  userBubble: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: '#fff',
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    background: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    color: '#1a1a1a',
    borderBottomLeftRadius: 4,
  },
  messageHeader: {
    display: 'flex',
    alignItems: 'center',
    fontSize: 13,
    marginBottom: 8,
    opacity: 0.9,
    fontWeight: 500,
  },
  senderName: {
    marginLeft: 6,
  },
  messageContent: {
    fontSize: 15,
    lineHeight: '24px',
  },
  tokenInfo: {
    fontSize: 11,
    opacity: 0.7,
    marginTop: 8,
    paddingTop: 8,
    borderTop: '1px solid rgba(255, 255, 255, 0.2)',
  },
  actionsInfo: {
    marginTop: 8,
    paddingTop: 8,
    borderTop: '1px solid rgba(255, 255, 255, 0.2)',
    display: 'flex',
    alignItems: 'center',
    flexWrap: 'wrap' as const,
    gap: 8,
  },
  actionTag: {
    margin: 0,
  },
  executionText: {
    fontSize: 12,
  },
  // Markdown styles
  markdownParagraph: {
    margin: '8px 0',
    lineHeight: '24px',
  },
  markdownList: {
    margin: '8px 0',
    paddingLeft: 20,
  },
  markdownListItem: {
    margin: '4px 0',
    lineHeight: '22px',
  },
  inlineCode: {
    background: 'rgba(0, 0, 0, 0.06)',
    padding: '2px 6px',
    borderRadius: 4,
    fontFamily: 'monospace',
    fontSize: '0.9em',
  },
  blockCode: {
    display: 'block',
    background: 'rgba(0, 0, 0, 0.06)',
    padding: '12px',
    borderRadius: 8,
    fontFamily: 'monospace',
    fontSize: '0.9em',
    overflowX: 'auto' as const,
    margin: '8px 0',
  },
  boldText: {
    fontWeight: 600,
  },
}

export default ChatMessage
