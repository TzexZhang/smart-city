@echo off
chcp 65001 >nul
echo ========================================
echo   智慧城市数字孪生系统 - 启动脚本
echo ========================================
echo.

echo [1/3] 检查数据库...
echo.
mysql -uroot -p -e "USE smart_city;" 2>nul
if errorlevel 1 (
    echo 数据库不存在，正在创建...
    mysql -uroot -p < database\init.sql
    if errorlevel 1 (
        echo.
        echo [错误] 数据库初始化失败！
        echo 请确保MySQL已启动，并检查 database\init.sql 中的密码配置
        pause
        exit /b 1
    )
    echo 数据库初始化完成
    echo.
)

echo [2/3] 安装依赖...
echo.

echo [后端依赖]
cd backend
if not exist "venv\" (
    echo 创建虚拟环境...
    python -m venv venv
)
call venv\Scripts\activate
echo 安装Python依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
cd ..

echo.
echo [前端依赖]
cd frontend
if not exist "node_modules\" (
    echo 安装Node依赖...
    call npm install
)
cd ..

echo.
echo [3/3] 启动服务...
echo.
echo 启动后端服务...
start cmd /k "cd backend && venv\Scripts\activate && python main.py"

timeout /t 3 >nul

echo 启动前端服务...
start cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo   服务启动完成！
echo ========================================
echo.
echo 后端API: http://localhost:8000
echo 前端地址: http://localhost:5173
echo API文档: http://localhost:8000/docs
echo.
echo 按任意键关闭此窗口...
pause >nul
