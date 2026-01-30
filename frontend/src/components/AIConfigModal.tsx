import { useState, useEffect } from 'react'
import { Card, List, Form, Input, Select, Button, Tag, message, Modal, Tabs, Switch } from 'antd'
import { PlusOutlined, DeleteOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { aiApi } from '../services'

const { Option } = Select

interface Provider {
  id: string
  provider_code: string
  provider_name: string
  api_key_encrypted: string
  is_enabled: boolean
  is_default: boolean
}

interface Model {
  code: string
  name: string
  description: string
  context_length: number
  is_free: boolean
  input_price: number
  output_price: number
  supports_function_calling: boolean
  max_tokens: number
}

const AIConfigModal = ({ visible, onCancel }: { visible: boolean; onCancel: () => void }) => {
  const [activeTab, setActiveTab] = useState('providers')
  const [providers, setProviders] = useState<Provider[]>([])
  const [models, setModels] = useState<Model[]>([])
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    if (visible) {
      loadData()
    }
  }, [visible])

  const loadData = async () => {
    setLoading(true)
    try {
      const [providersRes, modelsRes]: any[] = await Promise.all([
        aiApi.getProviders(),
        aiApi.getModels(),
      ])
      setProviders(providersRes.data)
      setModels(modelsRes.data)
    } catch (error) {
      message.error('加载数据失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAddProvider = async (values: any) => {
    try {
      await aiApi.addProvider(values)
      message.success('添加成功')
      loadData()
      form.resetFields()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '添加失败')
    }
  }

  const handleDeleteProvider = async (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个AI提供商吗？',
      onOk: async () => {
        try {
          await aiApi.deleteProvider(id)
          message.success('删除成功')
          loadData()
        } catch (error: any) {
          message.error('删除失败')
        }
      },
    })
  }

  const handleSetDefault = async (id: string) => {
    try {
      await aiApi.setDefaultProvider(id)
      message.success('设置成功')
      loadData()
    } catch (error: any) {
      message.error('设置失败')
    }
  }

  const providerOptions = [
    { value: 'zhipu', label: '智谱AI', free: 'GLM-4-Flash' },
    { value: 'qwen', label: '通义千问', free: 'Qwen-Turbo' },
    { value: 'deepseek', label: 'DeepSeek', free: 'DeepSeek-Chat' },
  ]

  return (
    <Modal
      title="AI配置"
      open={visible}
      onCancel={onCancel}
      width={900}
      footer={null}
    >
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <Tabs.TabPane tab="AI提供商" key="providers">
          <Card title="添加AI提供商" size="small" style={{ marginBottom: 16 }}>
            <Form layout="inline" onFinish={handleAddProvider} form={form}>
              <Form.Item
                name="provider_code"
                label="提供商"
                rules={[{ required: true }]}
              >
                <Select style={{ width: 200 }}>
                  {providerOptions.map((opt) => (
                    <Option key={opt.value} value={opt.value}>
                      {opt.label} (免费: {opt.free})
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                name="provider_name"
                label="名称"
                initialValue="自定义配置"
                rules={[{ required: true }]}
              >
                <Input placeholder="自定义名称" />
              </Form.Item>

              <Form.Item
                name="api_key"
                label="API Key"
                rules={[{ required: true }]}
              >
                <Input.Password placeholder="请输入API Key" style={{ width: 300 }} />
              </Form.Item>

              <Form.Item name="base_url" label="API地址（可选）">
                <Input placeholder="默认使用官方地址" style={{ width: 250 }} />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" icon={<PlusOutlined />}>
                  添加
                </Button>
              </Form.Item>
            </Form>
          </Card>

          <Card title="已配置的提供商" loading={loading}>
            <List
              dataSource={providers}
              renderItem={(provider) => (
                <List.Item
                  actions={[
                    <Button
                      type="link"
                      disabled={provider.is_default}
                      onClick={() => handleSetDefault(provider.id)}
                      icon={provider.is_default ? <CheckCircleOutlined /> : undefined}
                    >
                      {provider.is_default ? '默认' : '设为默认'}
                    </Button>,
                    <Button
                      type="link"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => handleDeleteProvider(provider.id)}
                    >
                      删除
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    title={provider.provider_name}
                    description={
                      <span>
                        代码: {provider.provider_code} | API Key: ****
                        {provider.api_key_encrypted}
                      </span>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Tabs.TabPane>

        <Tabs.TabPane tab="可用模型" key="models">
          <Card loading={loading}>
            <List
              dataSource={models}
              renderItem={(model) => (
                <List.Item>
                  <List.Item.Meta
                    title={
                      <span>
                        {model.name}
                        {model.is_free && (
                          <Tag color="green" style={{ marginLeft: 8 }}>
                            免费
                          </Tag>
                        )}
                      </span>
                    }
                    description={
                      <div>
                        <div>描述: {model.description}</div>
                        <div>
                          上下文: {model.context_length.toLocaleString()} | 价格:
                          ¥{model.input_price}/{model.output_price} per 1K tokens
                        </div>
                        <div>
                          Function Calling: {model.supports_function_calling ? '✓' : '✗'} |
                          最大输出: {model.max_tokens} tokens
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Tabs.TabPane>
      </Tabs>
    </Modal>
  )
}

export default AIConfigModal
