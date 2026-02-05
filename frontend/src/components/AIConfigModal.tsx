import { useState, useEffect } from 'react'
import { Card, List, Form, Input, Select, Button, Tag, message, Modal, Tabs } from 'antd'
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
  const [selectedProvider, setSelectedProvider] = useState<string>('zhipu')
  const [form] = Form.useForm()

  useEffect(() => {
    if (visible) {
      loadData()
    }
  }, [visible])

  // 当选择的provider改变时，更新API Key的必填状态
  const handleProviderChange = (value: string) => {
    setSelectedProvider(value)
  }

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
      setSelectedProvider('zhipu')
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

  // 判断是否为免费模型
  const isFreeProvider = (providerCode: string) => {
    const freeProviders = ['zhipu', 'qwen', 'deepseek', 'ernie', 'xinghuo']
    return freeProviders.includes(providerCode)
  }

  const providerOptions = [
    { value: 'zhipu', label: '智谱AI', freeModel: 'GLM-4-Flash', isFree: true },
    { value: 'qwen', label: '通义千问', freeModel: 'Qwen-Turbo', isFree: true },
    { value: 'deepseek', label: 'DeepSeek', freeModel: 'DeepSeek-Chat', isFree: true },
    { value: 'openai', label: 'OpenAI', freeModel: null, isFree: false },
    { value: 'anthropic', label: 'Anthropic Claude', freeModel: null, isFree: false },
    { value: 'ernie', label: '百度文心一言', freeModel: 'ERNIE Speed', isFree: true },
    { value: 'xinghuo', label: '讯飞星火', freeModel: 'Spark Lite', isFree: true },
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
                <Select
                  style={{ width: 200 }}
                  onChange={handleProviderChange}
                >
                  {providerOptions.map((opt) => (
                    <Option key={opt.value} value={opt.value}>
                      {opt.label} {opt.isFree && `(免费: ${opt.freeModel})`}
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
                rules={!isFreeProvider(selectedProvider) ? [{ required: true, message: '请输入API Key' }] : []}
              >
                <Input.Password
                  placeholder={
                    isFreeProvider(selectedProvider)
                      ? '免费模型无需API Key（可选）'
                      : '请输入API Key'
                  }
                  style={{ width: 300 }}
                />
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
            {isFreeProvider(selectedProvider) && (
              <div style={{ marginTop: 8, fontSize: 12, color: '#52c41a' }}>
                ✓ 该提供商有免费模型，无需API Key即可使用
              </div>
            )}
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
