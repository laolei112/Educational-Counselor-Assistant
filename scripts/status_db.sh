#!/bin/bash

# 数据库状态检查脚本

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

MYSQL_PASSWORD="fgdTv@4629uGdY"
MYSQL_DB="dev_yundisoft"
REDIS_PORT=6380
REDIS_PASSWORD="HaWSD*9265tZYj"

echo "========================================="
echo "  数据库服务状态检查"
echo "========================================="

# MySQL 状态
echo -n "MySQL 服务: "
if brew services list | grep mysql | grep -q "started"; then
    echo -e "${GREEN}运行中${NC}"
else
    echo -e "${RED}未运行${NC}"
fi

echo -n "MySQL 连接: "
if mysql -u root -p"${MYSQL_PASSWORD}" -e "SELECT 1;" &> /dev/null; then
    echo -e "${GREEN}正常${NC}"
else
    echo -e "${RED}失败${NC}"
fi

echo -n "数据库 ${MYSQL_DB}: "
if mysql -u root -p"${MYSQL_PASSWORD}" -e "USE ${MYSQL_DB};" &> /dev/null; then
    echo -e "${GREEN}存在${NC}"
else
    echo -e "${RED}不存在${NC}"
fi

echo ""

# Redis 状态
echo -n "Redis (端口 ${REDIS_PORT}): "
if redis-cli -p ${REDIS_PORT} -a "${REDIS_PASSWORD}" ping 2>/dev/null | grep -q "PONG"; then
    echo -e "${GREEN}运行中${NC}"
else
    echo -e "${RED}未运行${NC}"
fi

echo ""
echo "========================================="
