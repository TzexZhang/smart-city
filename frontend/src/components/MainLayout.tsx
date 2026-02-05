import { useState } from 'react'
import { Layout, Menu, Avatar, Dropdown, Button } from 'antd'
import {
  HomeOutlined,
  SettingOutlined,
  LogoutOutlined,
  UserOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
} from '@ant-design/icons'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import AIConfigModal from '../components/AIConfigModal'
import UserSettingsModal from '../components/UserSettingsModal'

const { Header, Sider, Content } = Layout

const MainLayout = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const [configModalVisible, setConfigModalVisible] = useState(false)
  const [settingsModalVisible, setSettingsModalVisible] = useState(false)
  const [collapsed, setCollapsed] = useState(true)

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const getFullAvatarUrl = (url: string) => {
    if (!url) return ''
    if (url.startsWith('http')) return url
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${url}`
  }

  const userMenuItems = [
    {
      key: 'settings',
      icon: <UserOutlined />,
      label: '个人设置',
      onClick: () => setSettingsModalVisible(true),
    },
    {
      key: 'config',
      icon: <SettingOutlined />,
      label: 'AI配置',
      onClick: () => setConfigModalVisible(true),
    },
    { type: 'divider' as const },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        trigger={null}
        width={200}
        style={{
          background: '#001529',
          overflow: 'hidden',
        }}
      >
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          padding: collapsed ? 0 : '0 16px',
          color: '#fff',
          fontSize: 18,
          fontWeight: 'bold',
        }}>
          {!collapsed && '智慧城市'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          inlineCollapsed={collapsed}
        />
      </Sider>
      <Layout>
        <Header style={{
          background: '#fff',
          padding: '0 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid #f0f0f0',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{ fontSize: 16 }}
            />
            <div style={{ fontSize: 16, fontWeight: 500 }}>
              智慧城市数字孪生系统
            </div>
          </div>
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar
                size={32}
                src={getFullAvatarUrl(user?.avatar_url || '')}
                icon={<UserOutlined />}
              />
              <span>{user?.username || '用户'}</span>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ padding: 24, background: '#f0f2f5' }}>
          <Outlet />
        </Content>
      </Layout>

      <AIConfigModal
        visible={configModalVisible}
        onCancel={() => setConfigModalVisible(false)}
      />

      <UserSettingsModal
        visible={settingsModalVisible}
        onCancel={() => setSettingsModalVisible(false)}
      />
    </Layout>
  )
}

export default MainLayout
