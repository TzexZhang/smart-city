#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本

功能：
1. 读取.env文件中的数据库配置
2. 创建数据库和表结构
3. 插入初始数据

使用方法：
    python init_database.py
"""

import os
import sys
from urllib.parse import urlparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import pymysql
except ImportError:
    print("错误: 未安装 pymysql 库")
    print("请运行: pip install pymysql")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("错误: 未安装 python-dotenv 库")
    print("请运行: pip install python-dotenv")
    sys.exit(1)


def parse_database_url(database_url: str) -> dict:
    """
    解析DATABASE_URL，提取连接参数

    格式: mysql+pymysql://username:password@host:port/database
    """
    # 移除 mysql+pymysql:// 前缀
    url = database_url.replace("mysql+pymysql://", "")

    # 解析URL
    parsed = urlparse(f"mysql://{url}")

    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 3306,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip("/") if parsed.path else None
    }


def load_sql_file(file_path: str) -> str:
    """加载SQL文件内容"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"SQL文件不存在: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def execute_sql_file(connection_params: dict, sql_content: str, description: str, use_database: bool = False):
    """执行SQL文件内容"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"{'='*60}")

    try:
        # 创建数据库连接
        conn_params = connection_params.copy()
        if not use_database:
            conn_params.pop("database", None)  # 移除数据库名，用于创建数据库

        connection = pymysql.connect(
            host=conn_params["host"],
            port=conn_params["port"],
            user=conn_params["user"],
            password=conn_params.get("password"),
            database=conn_params.get("database"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.Cursor
        )

        try:
            with connection.cursor() as cursor:
                # 分割SQL语句（按分号分隔，但忽略注释和空行）
                # 移除以 -- 开头的注释行
                lines = []
                for line in sql_content.split('\n'):
                    stripped = line.strip()
                    if stripped and not stripped.startswith('--'):
                        lines.append(line)

                # 按分号分割，但保留完整语句
                sql_content_clean = '\n'.join(lines)
                sql_statements = []
                current_statement = []

                for part in sql_content_clean.split(';'):
                    part = part.strip()
                    if part:
                        sql_statements.append(part)

                executed_count = 0
                for i, statement in enumerate(sql_statements, 1):
                    if statement:
                        try:
                            cursor.execute(statement)
                            executed_count += 1
                            # 显示进度
                            if executed_count % 5 == 0 or executed_count == len(sql_statements):
                                print(f"  进度: {executed_count}/{len(sql_statements)}")
                        except pymysql.Error as e:
                            # 某些语句可能因为已存在而失败，这是正常的
                            error_msg = str(e)
                            if "already exists" in error_msg or "Duplicate entry" in error_msg:
                                print(f"  ✓ 跳过（已存在）")
                            else:
                                print(f"  ✗ 语句 {i} 执行失败: {e}")
                                print(f"     语句预览: {statement[:80]}...")

                connection.commit()
                print(f"✓ {description} 完成 (执行了 {executed_count} 条语句)")

        finally:
            connection.close()

    except pymysql.Error as e:
        print(f"✗ 数据库操作失败: {e}")
        raise


def test_database_connection(connection_params: dict) -> bool:
    """测试数据库连接"""
    print(f"\n{'='*60}")
    print("测试数据库连接")
    print(f"{'='*60}")

    try:
        connection = pymysql.connect(
            host=connection_params["host"],
            port=connection_params["port"],
            user=connection_params["user"],
            password=connection_params["password"],
            database=connection_params["database"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.Cursor
        )
        connection.close()
        print("✓ 数据库连接成功")
        return True
    except pymysql.Error as e:
        print(f"✗ 数据库连接失败: {e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("智慧城市数字孪生系统 - 数据库初始化工具")
    print("="*60)

    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent.absolute()

    # 加载.env文件
    env_file = current_dir.parent / ".env"
    if not env_file.exists():
        print(f"\n✗ 错误: .env 文件不存在")
        print(f"   期望路径: {env_file}")
        print("\n请先创建 .env 文件并配置数据库连接信息")
        sys.exit(1)

    print(f"\n正在读取环境配置: {env_file}")
    load_dotenv(env_file)

    # 获取数据库URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("\n✗ 错误: .env 文件中未找到 DATABASE_URL 配置")
        sys.exit(1)

    # 解析数据库连接参数
    try:
        db_params = parse_database_url(database_url)
        print(f"\n数据库连接信息:")
        print(f"  主机: {db_params['host']}:{db_params['port']}")
        print(f"  用户: {db_params['user']}")
        print(f"  数据库: {db_params['database']}")
    except Exception as e:
        print(f"\n✗ 错误: 无法解析 DATABASE_URL")
        print(f"   {e}")
        sys.exit(1)

    # 确认执行
    print(f"\n{'='*60}")
    print("即将执行以下操作:")
    print("  1. 创建数据库和表结构")
    print("  2. 插入初始数据（AI模型、示例建筑）")
    print(f"{'='*60}")

    response = input("\n是否继续? (y/N): ").strip().lower()
    if response not in ["y", "yes"]:
        print("已取消操作")
        sys.exit(0)

    try:
        # 1. 执行init.sql（不指定数据库，创建数据库和表）
        init_sql_path = current_dir / "init.sql"
        init_sql = load_sql_file(str(init_sql_path))
        execute_sql_file(db_params, init_sql, "创建数据库和表结构", use_database=False)

        # 2. 执行seed.sql（连接到smart_city数据库）
        seed_sql_path = current_dir / "seed.sql"
        seed_sql = load_sql_file(str(seed_sql_path))
        execute_sql_file(db_params, seed_sql, "插入初始数据", use_database=True)

        # 3. 测试数据库连接
        test_database_connection(db_params)

        print(f"\n{'='*60}")
        print("✓ 数据库初始化完成！")
        print(f"{'='*60}")
        print("\n下一步:")
        print("  1. 启动后端服务: cd backend && python main.py")
        print("  2. 启动前端服务: cd frontend && npm run dev")
        print("  3. 访问应用: http://localhost:5173")
        print("="*60)

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ 数据库初始化失败")
        print(f"{'='*60}")
        print(f"错误信息: {e}")
        print("\n请检查:")
        print("  1. MySQL服务是否已启动")
        print("  2. .env文件中的数据库配置是否正确")
        print("  3. 数据库用户是否有创建数据库和表的权限")
        sys.exit(1)


if __name__ == "__main__":
    main()
