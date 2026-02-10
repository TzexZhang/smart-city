import React, { useState } from 'react'
import { Input, Button, Collapse, Card, Space } from 'antd'
import { SendOutlined, QuestionCircleOutlined, EnvironmentOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'

const { TextArea } = Input

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  loading?: boolean
  onGetLocation?: () => void
  hasLocation?: boolean
}

const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  loading = false,
  onGetLocation,
  hasLocation = false,
}) => {
  const [showHints, setShowHints] = useState(false)

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSend()
    }
  }

  return (
    <div style={styles.container}>
      {/* Location Button */}
      <div style={styles.locationSection}>
        <Button
          icon={<EnvironmentOutlined />}
          onClick={onGetLocation}
          type={hasLocation ? 'primary' : 'default'}
          size="small"
        >
          {hasLocation ? '已定位' : '获取我的位置'}
        </Button>
      </div>

      {/* Command Hints Toggle */}
      <div style={styles.hintToggle}>
        <Button
          icon={<QuestionCircleOutlined />}
          onClick={() => setShowHints(!showHints)}
          block
          type="text"
        >
          {showHints ? '隐藏' : '显示'}AI指令提示
        </Button>

        {showHints && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Card
              size="small"
              style={styles.hintCard}
              bodyStyle={styles.hintCardBody}
            >
              <Space direction="vertical" style={{ width: '100%' }} size={12}>
                <div style={styles.hintTitle}>
                  <QuestionCircleOutlined style={{ marginRight: 8 }} />
                  支持的AI指令
                </div>

                <Collapse
                  size="small"
                  items={[
                    {
                      key: 'camera',
                      label: <span style={styles.categoryLabel}>📍 摄像机控制</span>,
                      children: (
                        <div style={styles.hintItems}>
                          <div>• "飞行到北京"</div>
                          <div>• "跳转到上海浦东"</div>
                          <div>• "俯视深圳"</div>
                          <div>• "view Beijing from north"</div>
                        </div>
                      ),
                    },
                    {
                      key: 'building',
                      label: <span style={styles.categoryLabel}>🏢 建筑查询</span>,
                      children: (
                        <div style={styles.hintItems}>
                          <div>• "查询北京的高层建筑"</div>
                          <div>• "找出风险等级高的建筑"</div>
                          <div>• "统计上海的建筑类型"</div>
                          <div>• "show buildings over 100m"</div>
                        </div>
                      ),
                    },
                    {
                      key: 'layer',
                      label: <span style={styles.categoryLabel}>🗺️ 图层控制</span>,
                      children: (
                        <div style={styles.hintItems}>
                          <div>• "切换到卫星影像"</div>
                          <div>• "显示地形图"</div>
                          <div>• "switch to satellite view"</div>
                          <div>• "turn on 3D buildings"</div>
                        </div>
                      ),
                    },
                    {
                      key: 'weather',
                      label: <span style={styles.categoryLabel}>🌤️ 天气效果</span>,
                      children: (
                        <div style={styles.hintItems}>
                          <div>• "切换到雨天"</div>
                          <div>• "设置北京的天气为雪天"</div>
                          <div>• "上海多云天气"</div>
                          <div>• "深圳的大雾天气"</div>
                        </div>
                      ),
                    },
                    {
                      key: 'analysis',
                      label: <span style={styles.categoryLabel}>📊 空间分析</span>,
                      children: (
                        <div style={styles.hintItems}>
                          <div>• "分析周边1公里的建筑"</div>
                          <div>• "测量从这里到那里的距离"</div>
                          <div>• "buffer 500m around point"</div>
                          <div>• "测量可视范围"</div>
                        </div>
                      ),
                    },
                    {
                      key: 'other',
                      label: <span style={styles.categoryLabel}>🔄 其他</span>,
                      children: (
                        <div style={styles.hintItems}>
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
          </motion.div>
        )}
      </div>

      {/* Input Area */}
      <div style={styles.inputWrapper}>
        <TextArea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={
            showHints
              ? "试试：飞行到北京 / 设置北京为雨天 / 查询高层建筑"
              : "输入消息，按Enter发送，Shift+Enter换行..."
          }
          autoSize={{ minRows: 3, maxRows: 6 }}
          disabled={loading}
          style={styles.textArea}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={onSend}
          loading={loading}
          style={styles.sendButton}
          block
        >
          发送
        </Button>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: '16px 20px',
    background: 'rgba(255, 255, 255, 0.9)',
    backdropFilter: 'blur(20px)',
    borderTop: '1px solid rgba(255, 255, 255, 0.3)',
    flexShrink: 0,  // 防止被压缩
  },
  locationSection: {
    marginBottom: 12,
    display: 'flex',
    justifyContent: 'flex-end',
  },
  hintToggle: {
    marginBottom: 12,
  },
  hintCard: {
    marginTop: 8,
    background: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    borderRadius: 12,
    maxHeight: 350,  // 最大高度
    overflow: 'hidden',
  } as React.CSSProperties,
  hintCardBody: {
    padding: '12px 16px',
    // 允许内部滚动
    overflowY: 'auto' as 'auto',
    overflowX: 'hidden' as 'hidden',
    maxHeight: 320,  // 内容区域最大高度
  } as React.CSSProperties,
  hintTitle: {
    fontWeight: 600,
    color: '#1890ff',
    fontSize: 14,
  },
  categoryLabel: {
    fontWeight: 500,
    fontSize: 13,
  },
  hintItems: {
    fontSize: 12,
    color: '#666',
    marginLeft: 8,
    lineHeight: '20px',
  },
  inputWrapper: {
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
  },
  textArea: {
    borderRadius: 12,
    border: '1px solid rgba(0, 0, 0, 0.1)',
    background: 'rgba(255, 255, 255, 0.8)',
    backdropFilter: 'blur(10px)',
    fontSize: 15,
  },
  sendButton: {
    height: 40,
    borderRadius: 12,
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    fontWeight: 500,
  },
}

export default ChatInput
