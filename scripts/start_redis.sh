#!/bin/bash

# Redis 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REDIS_PORT=6380
REDIS_PASSWORD="HaWSD*9265tZYj"
REDIS_CONF_FILE="${SCRIPT_DIR}/redis/redis-${REDIS_PORT}.conf"

echo "启动 Redis (端口: ${REDIS_PORT})..."

# 检查是否已经在运行
if redis-cli -p ${REDIS_PORT} -a "${REDIS_PASSWORD}" ping 2>/dev/null | grep -q "PONG"; then
    echo "Redis 已在运行"
    exit 0
fi

# 检查配置文件
if [ ! -f "${REDIS_CONF_FILE}" ]; then
    echo "配置文件不存在，请先运行 setup_local_db.sh"
    exit 1
fi

# 启动 Redis
redis-server "${REDIS_CONF_FILE}"
sleep 2

# 验证
if redis-cli -p ${REDIS_PORT} -a "${REDIS_PASSWORD}" ping 2>/dev/null | grep -q "PONG"; then
    echo "✓ Redis 启动成功"
else
    echo "✗ Redis 启动失败"
    exit 1
fi
