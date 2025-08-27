#!/bin/bash

echo "🐳 香港升学助手 - Docker 启动脚本"
echo "=================================="

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查 docker-compose 是否可用
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安装，请先安装 docker-compose"
    exit 1
fi

echo "✅ Docker 环境检查通过"

# 停止现有容器（如果有）
echo "🛑 停止现有容器..."
docker-compose down

# 构建并启动服务
echo "🚀 构建并启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 显示日志
echo "📋 显示后端启动日志..."
docker-compose logs backend | tail -20

echo ""
echo "🎉 启动完成！"
echo "=================================="
echo "服务访问地址："
echo "- 后端 API: http://localhost:8080"
echo "- API 文档: http://localhost:8080/swagger/"
echo "- MySQL: localhost:3306"
echo "- Redis: localhost:6380"
echo ""
echo "常用命令："
echo "- 查看日志: docker-compose logs -f backend"
echo "- 停止服务: docker-compose down"
echo "- 重启服务: docker-compose restart"
echo ""
echo "测试 API："
echo "curl http://localhost:8080/api/schools/" 