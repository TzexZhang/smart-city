# 智慧城市数字孪生系统

基于 CesiumJS 和 FastAPI 的智慧城市三维可视化平台，支持 AI 驱动的空间分析和模拟。

## 🌟 主要特性

### 1. 三维可视化
- **真实地形**: Cesium World Terrain 全球地形数据
- **3D 建筑**: 全球 3.5 亿建筑三维模型（通过 Cesium OSM Buildings）
- **多图层影像**: 高德地图（中国）+ 卫星影像（全球）
- **时间控制**: 支持时间动态变化

### 2. AI 驱动
- **自然语言交互**: 通过对话控制地图
- **智能分析**: AI 驱动的风险分析和资产优化
- **动作执行**: 自动解析并执行地图控制指令
- **极客模式**: 完整显示 AI 分析过程

### 3. 资产管理
- **多维检索**: 按高度、类型、风险等级、区域筛选
- **空间查询**: 圆形范围搜索，计算影响范围
- **统计概览**: 建筑数据统计和可视化

### 4. 空间模拟
- **圆形模拟**: 灾害影响范围分析
- **受影响计算**: 自动计算受影响建筑
- **可视化生成**: 生成地图可视化操作

### 5. 执行策略
- **自动模式**: 立即执行所有动作
- **确认模式**: 需要用户确认后才执行
- **手动模式**: 仅记录日志，不执行

## 🏗️ 技术栈

### 前端
- **React 18**: 用户界面框架
- **TypeScript**: 类型安全
- **CesiumJS**: 3D 地球和地图引擎
- **Vite**: 前端构建工具
- **Ant Design**: UI 组件库
- **Zustand**: 状态管理

### 后端
- **FastAPI**: 高性能 Python Web 框架
- **SQLAlchemy**: ORM 和数据库管理
- **MySQL**: 关系型数据库
- **Alembic**: 数据库迁移工具
- **JWT**: 用户认证

### 3D GIS
- **Cesium Ion**: 3D 地理空间内容平台
- **OSM Buildings**: 开放街道地图建筑数据
- **高德地图**: 中国地图服务

## 📁 项目结构

```
smart-city/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   ├── auth.py     # 认证接口
│   │   │   ├── users.py    # 用户管理
│   │   │   ├── ai.py       # AI 对话
│   │   │   ├── chat.py     # 聊天接口
│   │   │   ├── buildings.py    # 资产检索 ✨
│   │   │   ├── simulation.py   # 空间模拟 ✨
│   │   │   └── execution.py    # 执行配置 ✨
│   │   ├── core/           # 核心功能
│   │   ├── models/         # 数据模型
│   │   └── database.py     # 数据库配置
│   ├── alembic/            # 数据库迁移
│   ├── database/           # 数据库脚本
│   │   └── seed_sample_data.py  # 示例数据 ✨
│   ├── main.py             # 应用入口
│   ├── verify_setup.py     # 设置验证 ✨
│   ├── QUICKSTART.bat      # Windows 快速启动 ✨
│   └── SETUP_GUIDE.md      # 后端设置指南 ✨
│
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # React 组件
│   │   │   └── CesiumViewer.tsx    # 3D 地图组件
│   │   ├── contexts/       # React Context
│   │   │   └── CesiumContext.tsx   # Cesium 全局上下文 ✨
│   │   ├── pages/          # 页面组件
│   │   ├── utils/          # 工具函数
│   │   │   └── aiActionExecutor.ts # AI 动作执行 ✨
│   │   └── ...
│   ├── .env.example        # 环境变量示例 ✨
│   ├── FRONTEND_INTEGRATION.md  # 前端集成指南 ✨
│   └── vite.config.ts      # Vite 配置
│
├── SYSTEM_DESIGN.md        # 系统设计文档 ✨
├── IMPLEMENTATION_STATUS.md   # 实现状态报告 ✨
└── README.md               # 本文件
```

✨ = 本次新增

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+ 或 8.0+

### 方式一：使用快速启动脚本（推荐）

**Windows:**
```bash
cd backend
QUICKSTART.bat
```

**Linux/Mac:**
```bash
cd backend
chmod +x QUICKSTART.sh
./QUICKSTART.sh
```

### 方式二：手动设置

#### 1. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 文件，配置数据库连接和密钥

# 验证设置
python verify_setup.py

# 运行数据库迁移
alembic upgrade head

# 加载示例数据
python database/seed_sample_data.py

# 启动后端服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 配置 Cesium Ion Token（可选但推荐）
# 1. 访问 https://ion.cesium.com/signup 注册
# 2. 访问 https://ion.cesium.com/tokens 获取 token
# 3. 在 .env 文件中添加: VITE_CESIUM_ION_TOKEN=your_token

# 启动前端服务
npm run dev
```

#### 3. 访问应用

- **前端应用**: http://localhost:5173
- **后端 API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| planner | planner123 | 规划师 |
| geek | geek123 | 极客 |

## 📚 文档

- [系统设计文档](SYSTEM_DESIGN.md) - 完整的系统架构和设计
- [实现状态报告](IMPLEMENTATION_STATUS.md) - 当前实现进度和待办事项
- [后端设置指南](backend/SETUP_GUIDE.md) - 后端设置详细说明
- [前端集成指南](frontend/FRONTEND_INTEGRATION.md) - 前端开发指南

## 🎯 核心功能演示

### 1. AI 对话控制

```
用户: "帮我找到北京朝阳区高度超过100米的建筑"
系统: [AI 分析] → [执行动作]
      - 飞行到北京朝阳区
      - 筛选高度 > 100m 的建筑
      - 高亮显示这些建筑
```

### 2. 空间模拟

```
用户: "模拟中国尊周围500米火灾影响范围"
系统: [计算圆形范围] → [查找受影响建筑] → [生成可视化]
      - 添加火灾影响范围圆圈
      - 高亮受影响建筑
      - 显示统计信息
```

### 3. 极客模式

启用极客模式后，AI 会显示完整的分析过程：

- 原始 AI 响应
- 解析步骤
- 最终可执行动作

### 4. 执行策略配置

用户可以自定义执行策略：

- **自动执行**: fly_to, add_marker, zoom_in 等
- **需要确认**: delete, modify, create 等
- **仅记录日志**: 所有操作

## 🔧 API 端点

### 资产检索
- `GET /api/v1/buildings/search` - 搜索建筑
- `GET /api/v1/buildings/search/spatial/circle` - 圆形范围搜索
- `GET /api/v1/buildings/statistics/overview` - 统计概览

### 空间模拟
- `POST /api/v1/simulation/circle` - 圆形范围模拟
- `POST /api/v1/ai/analyze` - AI 分析
- `GET /api/v1/analysis/reports` - 获取报告列表

### 执行配置
- `GET /api/v1/execution/config` - 获取配置
- `PUT /api/v1/execution/config` - 更新配置
- `POST /api/v1/execution/test-action` - 测试动作

更多 API 请查看: http://localhost:8000/docs

## 🔑 环境变量

### 后端 (.env)

```env
# 数据库
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/smart_city

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# 应用
APP_NAME=智慧城市数字孪生系统
APP_VERSION=1.0.0
DEBUG=True
```

### 前端 (.env)

```env
# Cesium Ion (可选)
VITE_CESIUM_ION_TOKEN=your_token_here
```

## 📊 数据库架构

### 扩展的表

**tb_buildings** (建筑资产表)
- 新增 20+ 字段支持详细的建筑属性
- 几何信息、高度范围、屋顶类型
- 消防等级、抗震等级、地下室信息
- 3D 模型链接、数据来源、维护状态

### 新增的表

**tb_simulation_records** (空间模拟记录)
- 模拟类型、中心点、半径
- 受影响建筑 ID 列表
- 影响摘要统计

**tb_city_events** (城市事件)
- 事件类型、时间、位置
- 严重程度、影响范围
- 响应措施

**tb_analysis_reports** (分析报告)
- 报告类型、标题、内容
- 摘要数据、可视化配置
- AI 模型

**tb_execution_configs** (执行配置)
- 执行模式
- 需要确认的动作列表
- 自动批准的动作列表

详见 [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)

## 🐛 故障排查

### 后端无法启动

1. 检查 MySQL 服务是否运行
2. 检查 .env 文件配置
3. 运行 `python verify_setup.py` 诊断

### 前端地图不显示

1. 检查 Cesium Ion Token 是否配置
2. 打开浏览器控制台查看错误
3. 检查网络连接（高德地图需要网络）

### AI 功能不工作

1. 检查 AI Provider 配置
2. 查看后端日志
3. 确认 API Key 有效

## 🗺️ 路线图

### ✅ 已完成 (v1.0)

- [x] 基础架构搭建
- [x] 用户认证系统
- [x] AI 对话功能
- [x] 3D 地图集成
- [x] 资产检索 API
- [x] 空间模拟 API
- [x] 执行配置系统
- [x] 极客模式支持

### 🚧 进行中

- [ ] 实际 AI 服务集成（当前使用模拟数据）
- [ ] 前端 UI 组件完善
- [ ] 性能优化

### 📋 计划中

- [ ] 更多空间分析类型（多边形、缓冲区）
- [ ] 趋势预测功能
- [ ] 数据可视化面板
- [ ] 实时事件监控
- [ ] 移动端适配

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**最后更新**: 2025-02-05
**版本**: 1.0.0
