#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设置验证脚本
检查所有导入是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def check_imports():
    """检查所有关键导入"""
    print("检查导入...")

    try:
        # 1. 检查数据库导入
        print("✓ 检查数据库模块...")
        from app.database import Base, AsyncSessionLocal, SessionLocal, engine
        print("  ✓ 数据库模块导入成功")

        # 2. 检查模型导入
        print("✓ 检查模型模块...")
        from app.models import (
            User, UserConfig, AIProvider, AIModel, Building,
            AIConversation, OperationLog, AIUsageStats,
            SimulationRecord, CityEvent, AnalysisReport, ExecutionConfig
        )
        print("  ✓ 所有模型导入成功")

        # 3. 检查 API 路由导入
        print("✓ 检查 API 路由...")
        from app.api import auth, users, ai, chat, buildings, simulation, execution
        print("  ✓ auth.router 导入成功")
        print("  ✓ users.router 导入成功")
        print("  ✓ ai.router 导入成功")
        print("  ✓ chat.router 导入成功")
        print("  ✓ buildings.router 导入成功")
        print("  ✓ simulation.router 导入成功")
        print("  ✓ execution.router 导入成功")

        # 4. 检查路由器配置
        print("✓ 检查路由器配置...")
        assert hasattr(buildings, 'router'), "buildings.router 不存在"
        assert hasattr(simulation, 'router'), "simulation.router 不存在"
        assert hasattr(execution, 'router'), "execution.router 不存在"
        print("  ✓ 所有路由器配置正确")

        # 5. 检查安全性模块
        print("✓ 检查安全性模块...")
        from app.core.security import get_password_hash, verify_password, create_access_token
        print("  ✓ 安全性模块导入成功")

        print("\n" + "="*50)
        print("✅ 所有导入检查通过！")
        print("="*50)
        return True

    except Exception as e:
        print(f"\n❌ 导入检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_connection():
    """检查数据库连接"""
    print("\n检查数据库连接...")

    try:
        from app.database import sync_engine
        from sqlalchemy import text

        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

        print("✓ 数据库连接成功")
        return True

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("  请检查:")
        print("  1. MySQL 服务是否运行")
        print("  2. .env 文件中的 DATABASE_URL 是否正确")
        print("  3. 数据库是否已创建")
        return False

def check_env_file():
    """检查 .env 文件"""
    print("\n检查环境配置...")

    from pathlib import Path
    env_file = Path(__file__).parent / ".env"

    if not env_file.exists():
        print("❌ .env 文件不存在")
        print("  请从 .env.example 复制并配置:")
        print("  cp .env.example .env")
        return False

    print("✓ .env 文件存在")

    # 加载并检查关键配置
    from dotenv import load_dotenv
    load_dotenv()

    import os

    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"  ✓ {var} 已配置")

    if missing_vars:
        print(f"\n❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        return False

    return True

def main():
    """主函数"""
    print("="*50)
    print("智慧城市系统 - 设置验证")
    print("="*50 + "\n")

    # 1. 检查环境配置
    env_ok = check_env_file()

    # 2. 检查导入（即使环境配置有问题也要检查）
    imports_ok = check_imports()

    # 3. 如果前两项都通过，检查数据库连接
    db_ok = False
    if env_ok and imports_ok:
        db_ok = check_database_connection()

    # 总结
    print("\n" + "="*50)
    print("验证结果汇总:")
    print("="*50)
    print(f"环境配置: {'✅ 通过' if env_ok else '❌ 未通过'}")
    print(f"导入检查: {'✅ 通过' if imports_ok else '❌ 未通过'}")
    print(f"数据库连接: {'✅ 通过' if db_ok else '⚠️  跳过'}")

    if env_ok and imports_ok:
        if not db_ok:
            print("\n建议:")
            print("1. 确保 MySQL 服务正在运行")
            print("2. 运行数据库迁移: alembic upgrade head")
        else:
            print("\n✅ 系统已准备就绪！")
            print("可以启动服务: uvicorn main:app --reload")
        return True
    else:
        print("\n请解决上述问题后重新运行此脚本")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
