# 智慧城市数字孪生系统

基于AI的智慧城市数字孪生平台，支持自然语言控制3D城市场景。

## 技术栈

### 前端
- React 18 + TypeScript
- Vite 5
- Ant Design 5
- TailwindCSS 3
- Cesium.js 1.110+
- Zustand 4

### 后端
- Python 3.9+
- FastAPI 0.104+
- SQLAlchemy 2.x
- Pydantic 2.x
- MySQL 8.0+
- Redis 7.x (可选)

## 项目结构

```
smart-city/
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── components/       # 组件
│   │   ├── pages/           # 页面
│   │   ├── services/        # API服务
│   │   ├── stores/          # 状态管理
│   │   ├── hooks/           # 自定义Hooks
│   │   ├── types/           # TypeScript类型
│   │   └── utils/           # 工具函数
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # 后端项目
│   ├── app/
│   │   ├── api/             # API路由
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据库模型
│   │   ├── schemas/         # Pydantic模型
│   │   ├── services/        # 业务服务
│   │   │   └── ai/         # AI服务
│   │   └── utils/           # 工具函数
│   ├── main.py
│   └── requirements.txt
├── database/                 # 数据库脚本
│   ├── init.sql
│   └── seed.sql
└── README.md
```

## 快速开始

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 数据库初始化

```bash
mysql -u root -p < database/init.sql
```

## 功能特性

- ✅ 用户注册登录（JWT认证）
- ✅ 多AI模型支持（智谱、通义、DeepSeek等）
- ✅ 3D城市可视化（Cesium.js）
- ✅ 自然语言控制（AI语义理解）
- ✅ 实时数据接入（天气、地图）
- ✅ 使用统计和成本追踪

## 环境变量

参考 `.env.example` 创建环境变量文件。

## 许可证

MIT License
