#!/bin/bash
set -e

echo "🐳 Starting Educational Counselor Backend..."
echo "============================================="

# 等待数据库启动
echo "⏳ Waiting for MySQL database..."
while ! nc -z mysql 3306; do
  echo "   Database is not ready yet, waiting 1 second..."
  sleep 1
done
echo "✅ Database connected!"

# 等待 Redis 启动
echo "⏳ Waiting for Redis..."
while ! nc -z redis 6380; do
  echo "   Redis is not ready yet, waiting 1 second..."
  sleep 1
done
echo "✅ Redis connected!"

# 运行数据库迁移
echo "🔄 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# 启动 Django 服务器
echo "🚀 Starting Django development server..."
echo "   Server will be available at http://localhost:8080"
echo "============================================="

exec python manage.py runserver 0.0.0.0:8080