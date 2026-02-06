# 后端设置指南

## 环境准备

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并配置以下变量：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/smart_city

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS配置
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

## 数据库初始化

### 1. 创建数据库

```bash
mysql -u root -p
CREATE DATABASE smart_city CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 2. 运行数据库迁移

```bash
# 查看迁移历史
alembic history

# 升级到最新版本
alembic upgrade head

# 如果需要回滚
alembic downgrade -1
```

### 3. 加载示例数据

```bash
python database/seed_sample_data.py
```

这将创建：
- 3个测试用户（admin, planner, geek）
- 4个AI模型配置
- 8个示例建筑（北京朝阳区）

## 启动服务

### 开发模式

```bash
# 启动后端服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
# 使用 Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API 文档

启动服务后，访问以下URL查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 新增功能

### 1. 资产检索 API

```bash
# 搜索建筑
GET /api/v1/buildings/search?min_height=100&category=commercial

# 圆形范围搜索
GET /api/v1/buildings/search/spatial/circle?center_lon=116.3974&center_lat=39.9093&radius=500

# 建筑统计
GET /api/v1/buildings/statistics/overview?city=北京
```

### 2. 空间模拟 API

```bash
# 圆形影响范围模拟
POST /api/v1/simulation/circle
{
  "center_lon": 116.3974,
  "center_lat": 39.9093,
  "radius": 500,
  "hazard_type": "fire"
}

# AI分析
POST /api/v1/ai/analyze?geek_mode=true
{
  "analysis_type": "risk_assessment",
  "location": {"city": "北京", "district": "朝阳区"},
  "filters": {"min_height": 100}
}
```

### 3. 执行配置 API

```bash
# 获取执行配置
GET /api/v1/execution/config

# 更新执行配置
PUT /api/v1/execution/config
{
  "execution_mode": "confirm",
  "confirm_required_actions": ["delete", "modify"],
  "show_geek_mode": true
}
```

## 默认用户账号

示例数据创建后，可以使用以下账号登录：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | 管理员 | 系统管理员 |
| planner | planner123 | 规划师 | 城市规划师 |
| geek | geek123 | 极客 | 技术极客 |

## 故障排查

### 1. 数据库连接失败

检查 `.env` 文件中的数据库连接字符串是否正确。

### 2. Alembic 迁移失败

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 强制重置
alembic stamp head
```

### 3. 模型导入错误

确保所有新模型已在 `app/models/__init__.py` 中定义。

### 4. JSON 类型不支持

如果使用 MySQL 5.7 或更早版本，可能需要修改 JSON 字段为 TEXT。

## 开发建议

1. **使用虚拟环境**：推荐使用 venv 或 conda
2. **代码格式化**：使用 black 和 isort
3. **类型检查**：使用 mypy
4. **测试**：运行 pytest 进行单元测试

## 数据库结构

### 扩展的建筑表字段

- 几何信息：geometry_type, centroid_lon, centroid_lat
- 高度范围：min_height, max_height
- 屋顶类型：roof_type
- 材料类型：material_type
- 业主信息：owner_name
- 使用性质：usage_type
- 消防等级：fire_resistance_level
- 抗震等级：seismic_fortification_level
- 地下室：has_basement, basement_floors
- 3D模型：model_url
- 数据来源：data_source, data_quality
- 维护状态：maintenance_status, last_inspected_date
- 扩展字段：tags, attributes (JSON)

### 新增表

1. **tb_simulation_records**：空间模拟记录
2. **tb_city_events**：城市事件
3. **tb_analysis_reports**：分析报告
4. **tb_execution_configs**：执行配置

## 更新日志

### 2025-02-05

- ✅ 扩展建筑表，新增20+字段
- ✅ 创建空间模拟、分析报告、执行配置表
- ✅ 实现资产检索API（多维度筛选、空间查询）
- ✅ 实现空间模拟API（圆形范围分析）
- ✅ 实现AI分析API（支持极客模式）
- ✅ 实现执行配置API（自动/确认/手动模式）
- ✅ 添加示例数据脚本
