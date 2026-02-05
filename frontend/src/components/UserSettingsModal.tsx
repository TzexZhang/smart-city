import { useState, useEffect } from 'react'
import { Modal, Form, Input, Button, Upload, message, Tabs, Avatar } from 'antd'
import { UploadOutlined, UserOutlined, LockOutlined } from '@ant-design/icons'
import api from '../services/api'
import { useAuthStore } from '../stores/authStore'

interface UserSettingsModalProps {
  visible: boolean
  onCancel: () => void
}

const UserSettingsModal = ({ visible, onCancel }: UserSettingsModalProps) => {
  const [activeTab, setActiveTab] = useState('profile')
  const [profileForm] = Form.useForm()
  const [passwordForm] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [avatarUrl, setAvatarUrl] = useState<string>('')
  const [uploading, setUploading] = useState(false)
  const { updateUser, logout } = useAuthStore()

  useEffect(() => {
    if (visible) {
      loadUserProfile()
    }
  }, [visible])

  const loadUserProfile = async () => {
    setLoading(true)
    try {
      const response: any = await api.get('/users/me')
      setAvatarUrl(response.data.avatar_url || '')
      profileForm.setFieldsValue({
        username: response.data.username,
        email: response.data.email,
        full_name: response.data.full_name,
        phone: response.data.phone,
      })
    } catch (error) {
      message.error('加载用户信息失败')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateProfile = async (values: any) => {
    try {
      await api.put('/users/me', values)
      // 更新store中的用户信息
      updateUser(values)
      message.success('个人信息更新成功')
      loadUserProfile()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '更新失败')
    }
  }

  const handleChangePassword = async (values: any) => {
    try {
      await api.put('/users/me/password', values)
      message.success('密码修改成功，请重新登录')
      passwordForm.resetFields()
      // 延迟跳转登录页
      setTimeout(() => {
        logout()
        window.location.href = '/login'
      }, 1500)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '密码修改失败')
    }
  }

  const handleAvatarUpload = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    try {
      setUploading(true)
      const response: any = await api.post('/users/me/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      const url = response.data?.avatar_url
      if (url) {
        setAvatarUrl(url)
        // 更新store中的头像URL
        updateUser({ avatar_url: url })
        message.success('头像上传成功')
        loadUserProfile()
      }
    } catch (error) {
      message.error('头像上传失败')
      throw error
    } finally {
      setUploading(false)
    }
  }

  const beforeUpload = (file: File) => {
    const isImage = file.type.startsWith('image/')
    if (!isImage) {
      message.error('只能上传图片文件')
      return false
    }
    const isLt5M = file.size / 1024 / 1024 < 5
    if (!isLt5M) {
      message.error('图片大小不能超过5MB')
      return false
    }
    return true
  }

  const getFullAvatarUrl = (url: string) => {
    if (!url) return ''
    if (url.startsWith('http')) return url
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${url}`
  }

  return (
    <Modal
      title="用户设置"
      open={visible}
      onCancel={onCancel}
      width={600}
      footer={null}
    >
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <Tabs.TabPane
          tab={<span><UserOutlined />个人信息</span>}
          key="profile"
        >
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <Avatar
              size={100}
              src={getFullAvatarUrl(avatarUrl)}
              icon={<UserOutlined />}
            />
          </div>

          <Form
            form={profileForm}
            layout="vertical"
            onFinish={handleUpdateProfile}
          >
            <Form.Item
              label="用户名"
              name="username"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, max: 50, message: '用户名长度为3-50个字符' }
              ]}
            >
              <Input placeholder="请输入用户名" />
            </Form.Item>

            <Form.Item
              label="邮箱"
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '请输入有效的邮箱地址' }
              ]}
            >
              <Input placeholder="请输入邮箱" />
            </Form.Item>

            <Form.Item
              label="真实姓名"
              name="full_name"
            >
              <Input placeholder="请输入真实姓名" />
            </Form.Item>

            <Form.Item
              label="手机号"
              name="phone"
            >
              <Input placeholder="请输入手机号" />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block>
                更新信息
              </Button>
            </Form.Item>
          </Form>
        </Tabs.TabPane>

        <Tabs.TabPane
          tab={<span><LockOutlined />修改密码</span>}
          key="password"
        >
          <Form
            form={passwordForm}
            layout="vertical"
            onFinish={handleChangePassword}
          >
            <Form.Item
              label="当前密码"
              name="old_password"
              rules={[{ required: true, message: '请输入当前密码' }]}
            >
              <Input.Password placeholder="请输入当前密码" />
            </Form.Item>

            <Form.Item
              label="新密码"
              name="new_password"
              rules={[
                { required: true, message: '请输入新密码' },
                { min: 8, max: 100, message: '密码长度为8-100个字符' }
              ]}
            >
              <Input.Password placeholder="请输入新密码（至少8个字符）" />
            </Form.Item>

            <Form.Item
              label="确认新密码"
              name="confirm_password"
              dependencies={['new_password']}
              rules={[
                { required: true, message: '请确认新密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('new_password') === value) {
                      return Promise.resolve()
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'))
                  },
                }),
              ]}
            >
              <Input.Password placeholder="请再次输入新密码" />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block>
                修改密码
              </Button>
            </Form.Item>
          </Form>
        </Tabs.TabPane>

        <Tabs.TabPane
          tab={<span><UploadOutlined />头像上传</span>}
          key="avatar"
        >
          <div style={{ textAlign: 'center', padding: '24px 0' }}>
            <Avatar
              size={120}
              src={getFullAvatarUrl(avatarUrl)}
              icon={<UserOutlined />}
              style={{ marginBottom: 16 }}
            />
            <Upload
              name="file"
              showUploadList={false}
              beforeUpload={beforeUpload}
              customRequest={({ file, onSuccess, onError }) => {
                handleAvatarUpload(file as File)
                  .then(() => onSuccess?.('ok'))
                  .catch((err) => onError?.(err))
              }}
              disabled={uploading}
            >
              <Button
                icon={<UploadOutlined />}
                loading={uploading}
              >
                {uploading ? '上传中...' : '更换头像'}
              </Button>
            </Upload>
            <div style={{ marginTop: 16, color: '#999', fontSize: 12 }}>
              支持 JPG、PNG、GIF、WebP 格式，文件大小不超过5MB
            </div>
          </div>
        </Tabs.TabPane>
      </Tabs>
    </Modal>
  )
}

export default UserSettingsModal
