-- 智慧城市数字孪生系统 - 数据库初始化脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS smart_city DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE smart_city;

-- 用户表
CREATE TABLE IF NOT EXISTS tb_users (
    id VARCHAR(36) PRIMARY KEY COMMENT '用户ID (UUID)',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    full_name VARCHAR(100) COMMENT '真实姓名',
    phone VARCHAR(20) COMMENT '手机号',
    avatar_url VARCHAR(500) COMMENT '头像URL',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-禁用, 1-正常',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否删除',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 用户配置表
CREATE TABLE IF NOT EXISTS tb_user_configs (
    id VARCHAR(36) PRIMARY KEY COMMENT '配置ID (UUID)',
    user_id VARCHAR(36) UNIQUE NOT NULL COMMENT '用户ID',
    provider VARCHAR(50) DEFAULT 'zhipu' COMMENT 'AI提供商',
    model_name VARCHAR(50) DEFAULT 'glm-4-flash' COMMENT 'AI模型名称',
    persona VARCHAR(20) DEFAULT 'admin' COMMENT '角色',
    temperature DECIMAL(3,2) DEFAULT 0.7 COMMENT '温度参数',
    top_p DECIMAL(3,2) DEFAULT 0.9 COMMENT 'Top-P参数',
    auto_execute BOOLEAN DEFAULT FALSE COMMENT '是否自动执行指令',
    default_city VARCHAR(50) DEFAULT '北京' COMMENT '默认城市',
    language VARCHAR(10) DEFAULT 'zh-CN' COMMENT '语言',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES tb_users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户配置表';

-- AI Provider配置表
CREATE TABLE IF NOT EXISTS tb_ai_providers (
    id VARCHAR(36) PRIMARY KEY COMMENT '配置ID (UUID)',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    provider_code VARCHAR(50) NOT NULL COMMENT '提供商代码',
    provider_name VARCHAR(100) NOT NULL COMMENT '提供商名称',
    api_key_encrypted TEXT COMMENT '加密的API Key',
    api_secret_encrypted TEXT COMMENT '加密的API Secret',
    base_url VARCHAR(500) COMMENT '自定义API地址',
    is_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否为默认提供商',
    priority INT DEFAULT 0 COMMENT '优先级',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES tb_users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_provider (user_id, provider_code),
    INDEX idx_user_id (user_id),
    INDEX idx_provider_code (provider_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI提供商配置表';

-- AI模型元数据表
CREATE TABLE IF NOT EXISTS tb_ai_models (
    id VARCHAR(36) PRIMARY KEY COMMENT '模型ID (UUID)',
    provider_code VARCHAR(50) NOT NULL COMMENT '提供商代码',
    model_code VARCHAR(100) NOT NULL COMMENT '模型代码',
    model_name VARCHAR(200) NOT NULL COMMENT '模型显示名称',
    description TEXT COMMENT '模型描述',
    context_length INT COMMENT '上下文长度',
    is_free BOOLEAN DEFAULT FALSE COMMENT '是否免费',
    input_price DECIMAL(10,4) COMMENT '输入价格',
    output_price DECIMAL(10,4) COMMENT '输出价格',
    supports_function_calling BOOLEAN DEFAULT FALSE COMMENT '是否支持Function Calling',
    supports_vision BOOLEAN DEFAULT FALSE COMMENT '是否支持视觉',
    max_tokens INT COMMENT '最大输出tokens',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    display_order INT DEFAULT 0 COMMENT '显示顺序',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_provider_model (provider_code, model_code),
    INDEX idx_provider_code (provider_code),
    INDEX idx_is_free (is_free),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI模型元数据表';

-- 建筑资产表
CREATE TABLE IF NOT EXISTS tb_buildings (
    id VARCHAR(36) PRIMARY KEY COMMENT '建筑ID (UUID)',
    name VARCHAR(200) NOT NULL COMMENT '建筑名称',
    category VARCHAR(50) COMMENT '类型',
    height DECIMAL(10,2) COMMENT '建筑高度(米)',
    longitude DECIMAL(11,8) NOT NULL COMMENT '经度',
    latitude DECIMAL(11,8) NOT NULL COMMENT '纬度',
    address VARCHAR(500) COMMENT '详细地址',
    district VARCHAR(100) COMMENT '所属区县',
    city VARCHAR(50) COMMENT '所属城市',
    status VARCHAR(20) DEFAULT 'normal' COMMENT '状态',
    risk_level INT DEFAULT 0 COMMENT '风险等级',
    floors INT COMMENT '楼层数',
    build_year INT COMMENT '建成年份',
    area DECIMAL(15,2) COMMENT '建筑面积',
    description TEXT COMMENT '描述信息',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否删除',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_category (category),
    INDEX idx_status (status),
    INDEX idx_city_district (city, district),
    INDEX idx_height (height)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='建筑资产表';

-- AI对话记录表
CREATE TABLE IF NOT EXISTS tb_ai_conversations (
    id VARCHAR(36) PRIMARY KEY COMMENT '对话ID (UUID)',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    session_id VARCHAR(36) NOT NULL COMMENT '会话ID',
    role VARCHAR(20) NOT NULL COMMENT '角色',
    content TEXT NOT NULL COMMENT '对话内容',
    model_name VARCHAR(50) COMMENT '使用的模型',
    tokens_used INT COMMENT 'Token消耗量',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES tb_users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI对话记录表';

-- 操作日志表
CREATE TABLE IF NOT EXISTS tb_operation_logs (
    id VARCHAR(36) PRIMARY KEY COMMENT '日志ID (UUID)',
    user_id VARCHAR(36) COMMENT '用户ID',
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    operation_data TEXT COMMENT '操作数据(JSON格式)',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    status VARCHAR(20) DEFAULT 'success' COMMENT '状态',
    error_message TEXT COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES tb_users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- 用户使用统计表
CREATE TABLE IF NOT EXISTS tb_ai_usage_stats (
    id VARCHAR(36) PRIMARY KEY COMMENT '统计ID (UUID)',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    provider_code VARCHAR(50) NOT NULL COMMENT '提供商代码',
    model_code VARCHAR(100) NOT NULL COMMENT '模型代码',
    date DATE NOT NULL COMMENT '统计日期',
    request_count INT DEFAULT 0 COMMENT '请求次数',
    input_tokens INT DEFAULT 0 COMMENT '输入tokens',
    output_tokens INT DEFAULT 0 COMMENT '输出tokens',
    total_tokens INT DEFAULT 0 COMMENT '总tokens',
    estimated_cost DECIMAL(10,4) DEFAULT 0 COMMENT '估算成本',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES tb_users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_model_date (user_id, provider_code, model_code, date),
    INDEX idx_user_id (user_id),
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI使用统计表';
