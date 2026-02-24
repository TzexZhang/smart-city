import { useState } from 'react'
import { Layout, Menu, Avatar, Dropdown, Button } from 'antd'
import {
  HomeOutlined,
  SettingOutlined,
  LogoutOutlined,
  UserOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  BgColorsOutlined,
  EnvironmentOutlined,
  GlobalOutlined,
  PictureOutlined,
  BuildOutlined,
  CameraOutlined,
} from '@ant-design/icons'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useCesiumViewer } from '../contexts/CesiumContext'
import AIConfigModal from '../components/AIConfigModal'
import UserSettingsModal from '../components/UserSettingsModal'
import * as Cesium from 'cesium'

const { Header, Sider, Content } = Layout

const MainLayout = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { viewer } = useCesiumViewer()
  const [configModalVisible, setConfigModalVisible] = useState(false)
  const [settingsModalVisible, setSettingsModalVisible] = useState(false)
  const [collapsed, setCollapsed] = useState(true)
  const [currentLayer, setCurrentLayer] = useState('amap')

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

  // 底图切换处理
  const handleSwitchLayer = async (layerId: string, provider: () => any) => {
    if (!viewer?.imageryLayers) return

    try {
      // 移除所有现有图层
      viewer.imageryLayers.removeAll()

      // 添加新的底图
      const imageryProvider = await provider()
      viewer.imageryLayers.addImageryProvider(imageryProvider)

      setCurrentLayer(layerId)
      console.log(`✅ 已切换到 ${layerId}`)
    } catch (error) {
      console.error(`❌ 切换底图失败:`, error)
    }
  }

  // 底图菜单项
  const layerMenuItems = [
    {
      key: 'amap',
      label: (
        <span>
          <GlobalOutlined style={{ marginRight: 8 }} />
          矢量地图
        </span>
      ),
      onClick: () => handleSwitchLayer('amap', () =>
        new Cesium.UrlTemplateImageryProvider({
          url: 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
          minimumLevel: 3,
          maximumLevel: 18,
        })
      ),
    },
    {
      key: 'satellite',
      label: (
        <span>
          <PictureOutlined style={{ marginRight: 8 }} />
          卫星影像
        </span>
      ),
      onClick: () => handleSwitchLayer('satellite', () =>
        new Cesium.UrlTemplateImageryProvider({
          url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
          maximumLevel: 18,
        })
      ),
    },
    {
      key: 'terrain',
      label: (
        <span>
          <EnvironmentOutlined style={{ marginRight: 8 }} />
          地形图
        </span>
      ),
      onClick: () => handleSwitchLayer('terrain', () =>
        new Cesium.UrlTemplateImageryProvider({
          url: 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
          minimumLevel: 3,
          maximumLevel: 18,
        })
      ),
    },
    {
      key: 'building',
      label: (
        <span>
          <BuildOutlined style={{ marginRight: 8 }} />
          建筑白模
        </span>
      ),
      onClick: () => handleSwitchLayer('building', () =>
        new Cesium.UrlTemplateImageryProvider({
          url: 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=9&x={x}&y={y}&z={z}',
          minimumLevel: 3,
          maximumLevel: 18,
        })
      ),
    },
  ]

  // 获取当前底图名称
  const getCurrentLayerName = () => {
    const layerMap: Record<string, string> = {
      amap: '矢量地图',
      satellite: '卫星影像',
      terrain: '地形图',
      building: '建筑白模',
    }
    return layerMap[currentLayer] || '矢量地图'
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
    <Layout style={styles.layoutContainer}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        trigger={null}
        width={200}
        style={styles.sider}
      >
        <div style={styles.siderHeader}>
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
      <Layout style={styles.contentLayout}>
        <Header style={styles.header}>
          <div style={styles.headerLeft}>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{ fontSize: 16 }}
            />
            <div style={styles.headerTitle}>
              智慧城市数字孪生系统
            </div>
          </div>
          <div style={styles.headerRight}>
            {/* 底图切换按钮 */}
            <Dropdown menu={{ items: layerMenuItems }} placement="bottomRight" trigger={['click']}>
              <Button
                type="text"
                icon={<BgColorsOutlined />}
                style={{ fontSize: 16, color: '#666' }}
                title={`当前底图: ${getCurrentLayerName()}`}
              >
                <span style={{ marginLeft: 4, fontSize: 13 }}>底图</span>
              </Button>
            </Dropdown>

            {/* 用户下拉菜单 */}
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <div style={styles.userSection}>
                <Avatar
                  size={32}
                  src={getFullAvatarUrl(user?.avatar_url || '')}
                  icon={<UserOutlined />}
                />
                <span>{user?.username || '用户'}</span>
              </div>
            </Dropdown>
          </div>
        </Header>
        <Content style={styles.content}>
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

// MainLayout样式 - 确保无滚动条，完美适配视口
const styles = {
  layoutContainer: {
    minHeight: '100vh',
    height: '100vh',
    overflow: 'hidden',  // 禁止滚动
  } as React.CSSProperties,

  sider: {
    background: '#001529',
    overflow: 'hidden',
  } as React.CSSProperties,

  siderHeader: {
    height: 64,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center' as const,
    padding: '0 16px',
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  } as React.CSSProperties,

  contentLayout: {
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',  // 禁止滚动
  } as React.CSSProperties,

  header: {
    background: '#fff',
    padding: '0 24px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottom: '1px solid #f0f0f0',
    flexShrink: 0,  // 防止被压缩
  } as React.CSSProperties,

  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: 16,
  } as React.CSSProperties,

  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  } as React.CSSProperties,

  headerTitle: {
    fontSize: 16,
    fontWeight: 500,
  } as React.CSSProperties,

  userSection: {
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  } as React.CSSProperties,

  content: {
    padding: 0,  // 移除padding，让Outlet占满
    background: '#f0f2f5',
    flex: 1,  // 占据剩余空间
    overflow: 'hidden',  // 禁止滚动
    height: '100%',  // 确保高度100%
  } as React.CSSProperties,
}

export default MainLayout
