#!/bin/bash

# Redis 停止脚本

REDIS_PORT=6380
REDIS_PASSWORD="HaWSD*9265tZYj"

echo "停止 Redis (端口: ${REDIS_PORT})..."

# 优雅关闭
redis-cli -p ${REDIS_PORT} -a "${REDIS_PASSWORD}" shutdown 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Redis 已停止"
else
    echo "Redis 可能未在运行"
fi
