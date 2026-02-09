-- 智慧城市数字孪生系统 - 初始数据

USE smart_city;

-- 插入AI模型元数据（系统预置）
INSERT INTO tb_ai_models (id, provider_code, model_code, model_name, description, context_length, is_free, input_price, output_price, supports_function_calling, supports_vision, max_tokens, is_active, display_order) VALUES
-- 智谱AI
('1', 'zhipu', 'glm-4-flash', 'GLM-4 Flash', '智谱AI免费模型，快速响应', 128000, TRUE, 0.0000, 0.0000, TRUE, FALSE, 8000, TRUE, 1),
('2', 'zhipu', 'glm-4-plus', 'GLM-4 Plus', '智谱AI增强模型，深度推理', 128000, FALSE, 0.0100, 0.0100, TRUE, TRUE, 8000, TRUE, 2),
('3', 'zhipu', 'glm-4-air', 'GLM-4 Air', '智谱AI轻量模型', 128000, FALSE, 0.0010, 0.0010, TRUE, FALSE, 8000, TRUE, 3),

-- 通义千问
('4', 'qwen', 'qwen-turbo', 'Qwen Turbo', '通义千问超高速模型', 8000, TRUE, 0.0000, 0.0000, TRUE, FALSE, 2000, TRUE, 4),
('5', 'qwen', 'qwen-plus', 'Qwen Plus', '通义千问增强版', 32000, FALSE, 0.0080, 0.0080, TRUE, FALSE, 6000, TRUE, 5),
('6', 'qwen', 'qwen-max', 'Qwen Max', '通义千问最强模型', 30000, FALSE, 0.0200, 0.0200, TRUE, TRUE, 8000, TRUE, 6),

-- DeepSeek
('7', 'deepseek', 'deepseek-chat', 'DeepSeek Chat', 'DeepSeek对话模型', 16000, TRUE, 0.0001, 0.0002, TRUE, FALSE, 4000, TRUE, 7),

-- 文心一言
('8', 'wenxin', 'ernie-speed', 'ERNIE Speed', '文心一言极速版', 8000, TRUE, 0.0000, 0.0000, TRUE, FALSE, 2000, TRUE, 8),
('9', 'wenxin', 'ernie-4.0', 'ERNIE 4.0', '文心大模型4.0', 8000, FALSE, 0.0120, 0.0120, TRUE, FALSE, 2000, TRUE, 9),

-- 腾讯混元
('10', 'hunyuan', 'hunyuan-lite', '混元Lite', '腾讯混元轻量版', 256000, TRUE, 0.0000, 0.0000, TRUE, FALSE, 6000, TRUE, 10),
('11', 'hunyuan', 'hunyuan-pro', '混元Pro', '腾讯混元专业版', 256000, FALSE, 0.0150, 0.0150, TRUE, TRUE, 6000, TRUE, 11);

-- 插入示例建筑数据（北京市地标建筑）
INSERT INTO tb_buildings (id, name, category, height, longitude, latitude, address, district, city, status, floors) VALUES
('b1', '中国', 'landmark', 528.0, 116.4347, 39.9087, '北京市朝阳区CBD核心区', '朝阳区', '北京', 'normal', 108),
('b2', '国贸三期', 'office', 330.0, 116.4586, 39.9095, '北京市朝阳区建国门外大街1号', '朝阳区', '北京', 'normal', 74),
('b3', '央视总部大楼', 'landmark', 234.0, 116.4732, 39.9129, '北京市朝阳区东三环中路32号', '朝阳区', '北京', 'normal', 52),
('b4', '北京银泰中心', 'commercial', 249.9, 116.4561, 39.9072, '北京市朝阳区建国门外大街2号', '朝阳区', '北京', 'normal', 63),
('b5', '中信大厦', 'office', 139.0, 116.4760, 39.9233, '北京市朝阳区光华路', '朝阳区', '北京', 'normal', 38);
