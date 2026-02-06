"""enhance building and simulation tables

Revision ID: enhance_building_and_simulation
Revises:
Create Date: 2025-02-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'enhance_building_and_simulation'
down_revision = None


def upgrade():
    """Upgrade: 扩展建筑表，新增模拟、事件、报告表"""

    # 扩展 tb_buildings 表
    op.add_column('tb_buildings', sa.Column('geometry_type', sa.String(50), comment='几何类型'))
    op.add_column('tb_buildings', sa.Column('centroid_lon', sa.DECIMAL(11, 8), comment='中心点经度'))
    op.add_column('tb_buildings', sa.Column('centroid_lat', sa.DECIMAL(11, 8), comment='中心点纬度'))
    op.add_column('tb_buildings', sa.Column('min_height', sa.DECIMAL(10, 2), comment='最低高度'))
    op.add_column('tb_buildings', sa.Column('max_height', sa.DECIMAL(10, 2), comment='最高高度'))
    op.add_column('tb_buildings', sa.Column('roof_type', sa.String(50), comment='屋顶类型'))
    op.add_column('tb_buildings', sa.Column('material_type', sa.String(50), comment='建材类型'))
    op.add_column('tb_buildings', sa.Column('owner_name', sa.String(200), comment='业主名称'))
    op.add_column('tb_buildings', sa.Column('usage_type', sa.String(50), comment='使用性质'))
    op.add_column('tb_buildings', sa.Column('fire_resistance_level', sa.Integer, comment='耐火等级'))
    op.add_column('tb_buildings', sa.Column('seismic_fortification_level', sa.Integer, comment='抗震等级'))
    op.add_column('tb_buildings', sa.Column('has_basement', sa.Boolean(), comment='是否有地下室'))
    op.add_column('tb_buildings', sa.Column('basement_floors', sa.Integer, comment='地下室层数'))
    op.add_column('tb_buildings', sa.Column('model_url', sa.String(500), comment='3D模型URL'))
    op.add_column('tb_buildings', sa.Column('osm_id', sa.BigInteger(), comment='OpenStreetMap ID'))
    op.add_column('tb_buildings', sa.Column('data_source', sa.String(50), comment='数据来源'))
    op.add_column('tb_buildings', sa.Column('data_quality', sa.Integer, comment='数据质量'))
    op.add_column('tb_buildings', sa.Column('last_inspected_date', sa.Date(), comment='最近检查日期'))
    op.add_column('tb_buildings', sa.Column('maintenance_status', sa.String(20), comment='维护状态'))
    op.add_column('tb_buildings', sa.Column('tags', sa.JSON(), comment='标签'))
    op.add_column('tb_buildings', sa.Column('attributes', sa.JSON(), comment='扩展属性'))

    # 创建索引
    op.create_index('tb_buildings', 'idx_location', ['longitude', 'latitude'])
    op.create_index('tb_buildings', 'idx_height', ['height'])
    op.create_index('tb_buildings', 'idx_category', ['category'])
    op.create_index('tb_buildings', 'idx_risk_level', ['risk_level'])
    op.create_index('tb_buildings', 'idx_city_district', ['city', 'district'])

    # 创建 tb_simulation_records 表
    op.create_table(
        'tb_simulation_records',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('simulation_type', sa.String(50), nullable=False, comment='模拟类型'),
        sa.Column('center_lon', sa.DECIMAL(11, 8), nullable=False),
        sa.Column('center_lat', sa.DECIMAL(11, 8), nullable=False),
        sa.Column('radius', sa.DECIMAL(10, 2), comment='半径(米)'),
        sa.Column('affected_building_ids', sa.JSON(), comment='受影响建筑ID列表'),
        sa.Column('impact_summary', sa.JSON(), comment='影响摘要'),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['tb_users.id'], ondelete='CASCADE')
    )
    op.create_index('tb_simulation_records', 'idx_user', ['user_id'])
    op.create_index('tb_simulation_records', 'idx_type', ['simulation_type'])

    # 创建 tb_city_events 表
    op.create_table(
        'tb_city_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_name', sa.String(200), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False, comment='事件类型'),
        sa.Column('event_date', sa.DateTime(), comment='事件时间'),
        sa.Column('longitude', sa.DECIMAL(11, 8)),
        sa.Column('latitude', sa.DECIMAL(11, 8)),
        sa.Column('radius', sa.DECIMAL(10, 2), comment='影响半径'),
        sa.Column('severity', sa.Integer(), comment='严重程度 1-5'),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('description', sa.Text()),
        sa.Column('affected_areas', sa.JSON(), comment='受影响区域'),
        sa.Column('response_actions', sa.JSON(), comment='响应措施'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index('tb_city_events', 'idx_type', ['event_type'])
    op.create_index('tb_city_events', 'idx_date', ['event_date'])

    # 创建 tb_analysis_reports 表
    op.create_table(
        'tb_analysis_reports',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False, comment='报告类型'),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False, comment='Markdown格式'),
        sa.Column('summary', sa.JSON(), comment='摘要数据'),
        sa.Column('visualization_config', sa.JSON(), comment='可视化配置'),
        sa.Column('ai_model', sa.String(50), comment='使用的AI模型'),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['tb_users.id'], ondelete='CASCADE')
    )
    op.create_index('tb_analysis_reports', 'idx_user', ['user_id'])
    op.create_index('tb_analysis_reports', 'idx_type', ['report_type'])

    # 创建 tb_execution_configs 表
    op.create_table(
        'tb_execution_configs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('execution_mode', sa.String(20), default='auto'),
        sa.Column('confirm_required_actions', sa.JSON()),
        sa.Column('auto_approve_actions', sa.JSON()),
        sa.Column('log_all_actions', sa.Boolean(), default=True),
        sa.Column('show_geek_mode', sa.Boolean(), default=False),
        sa.Column('max_undo_count', sa.Integer(), default=10),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['tb_users.id'], ondelete='CASCADE')
    )


def downgrade():
    """Downgrade: 回滚更改"""

    # 删除新增表
    op.drop_table('tb_execution_configs')
    op.drop_table('tb_analysis_reports')
    op.drop_table('tb_city_events')
    op.drop_table('tb_simulation_records')

    # 删除 tb_buildings 的扩展字段和索引
    op.drop_index('tb_buildings', 'idx_city_district')
    op.drop_index('tb_buildings', 'idx_risk_level')
    op.drop_index('tb_buildings', 'idx_category')
    op.drop_index('tb_buildings', 'idx_height')
    op.drop_index('tb_buildings', 'idx_location')

    op.drop_column('tb_buildings', 'attributes')
    op.drop_column('tb_buildings', 'tags')
    op.drop_column('tb_buildings', 'maintenance_status')
    op.drop_column('tb_buildings', 'last_inspected_date')
    op.drop_column('tb_buildings', 'data_quality')
    op.drop_column('tb_buildings', 'data_source')
    op.drop_column('tb_buildings', 'osm_id')
    op.drop_column('tb_buildings', 'model_url')
    op.drop_column('tb_buildings', 'basement_floors')
    op.drop_column('tb_buildings', 'has_basement')
    op.drop_column('tb_buildings', 'seismic_fortification_level')
    op.drop_column('tb_buildings', 'fire_resistance_level')
    op.drop_column('tb_buildings', 'usage_type')
    op.drop_column('tb_buildings', 'owner_name')
    op.drop_column('tb_buildings', 'material_type')
    op.drop_column('tb_buildings', 'roof_type')
    op.drop_column('tb_buildings', 'max_height')
    op.drop_column('tb_buildings', 'min_height')
    op.drop_column('tb_buildings', 'centroid_lat')
    op.drop_column('tb_buildings', 'centroid_lon')
    op.drop_column('tb_buildings', 'geometry_type')
