@echo off
chcp 65001 >nul
echo 🐳 香港升学助手 - Docker 全栈启动脚本
echo ==================================

REM 检查 Docker 是否运行
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker 未运行，请先启动 Docker
    pause
    exit /b 1
)

REM 检查 docker-compose 是否可用
docker-compose --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ docker-compose 未安装，请先安装 docker-compose
    pause
    exit /b 1
)

echo ✅ Docker 环境检查通过

REM 停止现有容器（如果有）
echo 🛑 停止现有容器...
docker-compose down

REM 构建并启动服务
echo 🚀 构建并启动服务...
docker-compose up -d --build

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 20 /nobreak >nul

REM 检查服务状态
echo 📊 检查服务状态...
docker-compose ps

REM 显示日志
echo 📋 显示启动日志...
docker-compose logs --tail=10 nginx
docker-compose logs --tail=10 backend
docker-compose logs --tail=10 frontend

echo.
echo 🎉 启动完成！
echo ==================================
echo 服务访问地址：
echo - 前端应用: http://localhost
echo - 后端 API: http://localhost/api/
echo - API 文档: http://localhost/swagger/
echo - MySQL: localhost:3306
echo - Redis: localhost:6380
echo.
echo 常用命令：
echo - 查看日志: docker-compose logs -f [service_name]
echo - 停止服务: docker-compose down
echo - 重启服务: docker-compose restart
echo.
echo 测试 API：
echo curl http://localhost/api/schools/
pause 