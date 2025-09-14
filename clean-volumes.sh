#!/bin/bash

# Docker Compose Volume 清理脚本

echo "🧹 Docker Compose Volume 清理工具"
echo "=================================="

# 显示当前 volumes
echo "📋 当前项目相关的 volumes:"
docker-compose config --volumes 2>/dev/null || echo "无法获取 volumes 信息"

echo ""
echo "请选择清理方式:"
echo "1) 清理前端缓存 volume (frontend_dist)"
echo "2) 清理数据库 volumes (mysql_data, redis_data) - ⚠️ 会丢失数据"
echo "3) 清理所有项目 volumes"
echo "4) 清理所有未使用的 volumes"
echo "5) 完全重置项目 (停止+删除+重建)"
echo "6) 查看 volumes 使用情况"
echo "0) 退出"

read -p "请输入选择 (0-6): " choice

case $choice in
    1)
        echo "🗑️ 清理前端缓存 volume..."
        docker-compose down
        docker volume rm educational-counselor-assistant_frontend_dist 2>/dev/null || echo "Volume 不存在或已被删除"
        docker-compose build --no-cache frontend
        docker-compose up -d
        echo "✅ 前端缓存已清理并重新构建"
        ;;
    2)
        echo "⚠️ 警告: 这将删除所有数据库数据!"
        read -p "确认继续? (y/N): " confirm
        if [[ $confirm == [yY] ]]; then
            echo "🗑️ 清理数据库 volumes..."
            docker-compose down
            docker volume rm educational-counselor-assistant_mysql_data 2>/dev/null || echo "MySQL volume 不存在"
            docker volume rm educational-counselor-assistant_redis_data 2>/dev/null || echo "Redis volume 不存在"
            docker-compose up -d
            echo "✅ 数据库 volumes 已清理"
        else
            echo "❌ 操作已取消"
        fi
        ;;
    3)
        echo "🗑️ 清理所有项目 volumes..."
        docker-compose down -v
        echo "✅ 所有项目 volumes 已清理"
        ;;
    4)
        echo "🗑️ 清理所有未使用的 volumes..."
        docker volume prune -f
        echo "✅ 未使用的 volumes 已清理"
        ;;
    5)
        echo "🔄 完全重置项目..."
        docker-compose down -v --remove-orphans
        docker-compose build --no-cache
        docker-compose up -d
        echo "✅ 项目已完全重置"
        ;;
    6)
        echo "📊 Volumes 使用情况:"
        docker system df -v
        echo ""
        echo "📋 项目相关 volumes:"
        docker-compose config --volumes 2>/dev/null || echo "无法获取信息"
        ;;
    0)
        echo "👋 退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🔍 当前 volumes 状态:"
docker volume ls | grep educational-counselor-assistant || echo "没有找到项目相关的 volumes"
