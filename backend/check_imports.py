#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导入验证脚本
检查所有 API 模块的导入是否正确
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def check_imports():
    """检查所有导入"""
    print("检查 API 模块导入...")

    try:
        print("✓ 检查 app.api.buildings...")
        from app.api import buildings
        print("  ✓ buildings 导入成功")

        print("✓ 检查 app.api.simulation...")
        from app.api import simulation
        print("  ✓ simulation 导入成功")

        print("✓ 检查 app.api.execution...")
        from app.api import execution
        print("  ✓ execution 导入成功")

        print("✓ 检查 app.api.auth...")
        from app.api import auth
        print("  ✓ auth 导入成功")

        print("✓ 检查 app.api.users...")
        from app.api import users
        print("  ✓ users 导入成功")

        print("✓ 检查 app.api.ai...")
        from app.api import ai
        print("  ✓ ai 导入成功")

        print("✓ 检查 app.api.chat...")
        from app.api import chat
        print("  ✓ chat 导入成功")

        print("\n" + "="*50)
        print("✅ 所有 API 模块导入成功！")
        print("="*50)
        return True

    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)
