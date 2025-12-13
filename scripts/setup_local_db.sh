#!/bin/bash

# ============================================
# 本地开发环境数据库安装脚本
# MySQL 和 Redis 安装配置 (macOS)
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置参数 (来自 settings.json)
MYSQL_USER="root"
MYSQL_PASSWORD="fgdTv@4629uGdY"
MYSQL_PORT=3306
MYSQL_DB="dev_yundisoft"
MYSQL_CHARSET="utf8mb4"

REDIS_PORT=6380
REDIS_PASSWORD="HaWSD*9265tZYj"

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  本地开发环境数据库安装脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查是否安装了 Homebrew
check_homebrew() {
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}Homebrew 未安装，正在安装...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo -e "${GREEN}✓ Homebrew 已安装${NC}"
    fi
}

# 安装 MySQL
install_mysql() {
    echo -e "\n${YELLOW}>>> 安装 MySQL...${NC}"
    
    if brew list mysql &> /dev/null; then
        echo -e "${GREEN}✓ MySQL 已安装${NC}"
    else
        brew install mysql
        echo -e "${GREEN}✓ MySQL 安装完成${NC}"
    fi
}

# 配置 MySQL 监听 TCP 端口
configure_mysql_tcp() {
    echo -e "\n${YELLOW}>>> 配置 MySQL TCP 端口...${NC}"
    
    MYSQL_CONF="/opt/homebrew/etc/my.cnf"
    
    # 检查配置文件是否已包含 port 设置
    if grep -q "^port = ${MYSQL_PORT}" "${MYSQL_CONF}" 2>/dev/null; then
        echo -e "${GREEN}✓ MySQL TCP 配置已存在${NC}"
        return
    fi
    
    # 写入配置文件，确保监听 TCP 端口
    cat > "${MYSQL_CONF}" << EOF
# Default Homebrew MySQL server config
[mysqld]
# Only allow connections from localhost
bind-address = 127.0.0.1
mysqlx-bind-address = 127.0.0.1
port = ${MYSQL_PORT}
skip-networking = OFF
EOF
    
    echo -e "${GREEN}✓ MySQL TCP 配置已写入${NC}"
}

# 清理残留的 MySQL 进程
cleanup_mysql_processes() {
    echo "清理残留 MySQL 进程..."
    
    # 先停止服务
    brew services stop mysql 2>/dev/null || true
    sleep 1
    
    # 获取 mysqld_safe 的 PID 并杀掉
    local safe_pids=$(pgrep -f "mysqld_safe" 2>/dev/null || true)
    if [ -n "$safe_pids" ]; then
        echo "$safe_pids" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    # 杀掉所有 mysqld 进程
    killall -9 mysqld 2>/dev/null || true
    sleep 2
    
    # 确认清理完成
    if pgrep -f "mysqld" > /dev/null 2>&1; then
        echo -e "${YELLOW}警告: 仍有 MySQL 进程在运行，尝试强制清理...${NC}"
        pkill -9 -f mysqld 2>/dev/null || true
        sleep 2
    fi
    
    echo -e "${GREEN}✓ MySQL 进程已清理${NC}"
}

# 配置 MySQL (包含密码重置)
configure_mysql() {
    echo -e "\n${YELLOW}>>> 配置 MySQL...${NC}"
    
    # 先尝试用目标密码连接
    if mysql -u root -p"${MYSQL_PASSWORD}" -e "SELECT 1;" &> /dev/null; then
        echo -e "${GREEN}✓ MySQL 密码已正确配置${NC}"
        create_database
        return
    fi
    
    # 尝试无密码连接
    if mysql -u root -e "SELECT 1;" &> /dev/null; then
        echo "MySQL 无密码，正在设置密码..."
        mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${MYSQL_PASSWORD}';"
        echo -e "${GREEN}✓ MySQL 密码设置完成${NC}"
        create_database
        return
    fi
    
    # 密码不对，需要重置
    echo -e "${YELLOW}MySQL 密码需要重置...${NC}"
    reset_mysql_password
    create_database
}

# 重置 MySQL root 密码
reset_mysql_password() {
    echo "停止 MySQL 服务并清理进程..."
    cleanup_mysql_processes
    
    echo "以跳过授权模式启动 MySQL..."
    mysqld_safe --skip-grant-tables &
    SAFE_PID=$!
    sleep 5
    
    echo "重置 root 密码..."
    mysql -u root -e "FLUSH PRIVILEGES; ALTER USER 'root'@'localhost' IDENTIFIED BY '${MYSQL_PASSWORD}';" 2>/dev/null
    
    echo "重启 MySQL 正常模式..."
    # 先杀 mysqld_safe 进程
    kill -9 $SAFE_PID 2>/dev/null || true
    sleep 1
    # 再杀 mysqld 进程
    killall -9 mysqld 2>/dev/null || true
    sleep 2
    
    # 确保所有进程都已清理
    cleanup_mysql_processes
    
    # 正常启动 MySQL
    brew services start mysql
    sleep 3
    
    # 验证密码重置是否成功
    if mysql -u root -p"${MYSQL_PASSWORD}" -h 127.0.0.1 -P ${MYSQL_PORT} -e "SELECT 1;" &> /dev/null; then
        echo -e "${GREEN}✓ MySQL 密码重置成功${NC}"
    else
        echo -e "${RED}✗ MySQL 密码重置失败，请手动处理${NC}"
        exit 1
    fi
}

# 创建数据库
create_database() {
    echo "创建数据库 ${MYSQL_DB}..."
    mysql -u root -p"${MYSQL_PASSWORD}" -e "CREATE DATABASE IF NOT EXISTS ${MYSQL_DB} CHARACTER SET ${MYSQL_CHARSET} COLLATE utf8mb4_unicode_ci;" 2>/dev/null
    
    # 执行初始化脚本
    if [ -f "${PROJECT_DIR}/mysql-init/init.sql" ]; then
        echo "执行初始化脚本..."
        mysql -u root -p"${MYSQL_PASSWORD}" < "${PROJECT_DIR}/mysql-init/init.sql" 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✓ 数据库 ${MYSQL_DB} 创建完成${NC}"
}

# 确保 MySQL 服务运行
ensure_mysql_running() {
    echo -e "\n${YELLOW}>>> 确保 MySQL 服务运行...${NC}"
    
    # 先清理可能存在的残留进程
    if pgrep -f "skip-grant-tables" > /dev/null 2>&1; then
        echo "检测到残留的 skip-grant-tables 进程，正在清理..."
        cleanup_mysql_processes
    fi
    
    # 检查服务状态
    if ! brew services list | grep mysql | grep -q "started"; then
        echo "启动 MySQL 服务..."
        brew services start mysql
        sleep 3
    fi
    
    # 验证 TCP 端口是否正常
    local port_check=$(mysql -u root -p"${MYSQL_PASSWORD}" -e "SHOW VARIABLES LIKE 'port';" 2>/dev/null | grep -o "[0-9]*$" || echo "0")
    if [ "$port_check" = "0" ]; then
        echo -e "${YELLOW}MySQL 未监听 TCP 端口，重新配置...${NC}"
        cleanup_mysql_processes
        configure_mysql_tcp
        brew services start mysql
        sleep 3
    fi
    
    echo -e "${GREEN}✓ MySQL 服务已启动${NC}"
}

# 安装 Redis
install_redis() {
    echo -e "\n${YELLOW}>>> 安装 Redis...${NC}"
    
    if brew list redis &> /dev/null; then
        echo -e "${GREEN}✓ Redis 已安装${NC}"
    else
        brew install redis
        echo -e "${GREEN}✓ Redis 安装完成${NC}"
    fi
}

# 配置 Redis (使用自定义端口和密码)
configure_redis() {
    echo -e "\n${YELLOW}>>> 配置 Redis (端口: ${REDIS_PORT})...${NC}"
    
    # Redis 配置文件目录
    REDIS_CONF_DIR="${SCRIPT_DIR}/redis"
    REDIS_DATA_DIR="${SCRIPT_DIR}/redis/data"
    REDIS_CONF_FILE="${REDIS_CONF_DIR}/redis-${REDIS_PORT}.conf"
    
    # 创建目录
    mkdir -p "${REDIS_CONF_DIR}"
    mkdir -p "${REDIS_DATA_DIR}"
    
    # 创建自定义 Redis 配置文件
    cat > "${REDIS_CONF_FILE}" << EOF
# Redis 配置文件 - 端口 ${REDIS_PORT}
port ${REDIS_PORT}
bind 127.0.0.1
daemonize yes
pidfile ${REDIS_CONF_DIR}/redis-${REDIS_PORT}.pid
logfile ${REDIS_CONF_DIR}/redis-${REDIS_PORT}.log
dir ${REDIS_DATA_DIR}
requirepass ${REDIS_PASSWORD}

# 持久化配置
save 900 1
save 300 10
save 60 10000
dbfilename dump-${REDIS_PORT}.rdb
appendonly yes
appendfilename "appendonly-${REDIS_PORT}.aof"
EOF
    
    echo -e "${GREEN}✓ Redis 配置文件已创建${NC}"
}

# 启动 Redis
start_redis() {
    echo -e "\n${YELLOW}>>> 启动 Redis...${NC}"
    
    REDIS_CONF_FILE="${SCRIPT_DIR}/redis/redis-${REDIS_PORT}.conf"
    
    # 检查是否已经在运行
    if redis-cli -p ${REDIS_PORT} -a "${REDIS_PASSWORD}" ping 2>/dev/null | grep -q "PONG"; then
        echo -e "${GREEN}✓ Redis 已在端口 ${REDIS_PORT} 运行${NC}"
        return
    fi
    
    # 启动 Redis
    redis-server "${REDIS_CONF_FILE}"
    sleep 2
    
    # 验证启动
    if redis-cli -p ${REDIS_PORT} -a "${REDIS_PASSWORD}" ping 2>/dev/null | grep -q "PONG"; then
        echo -e "${GREEN}✓ Redis 启动成功 (端口: ${REDIS_PORT})${NC}"
    else
        echo -e "${RED}✗ Redis 启动失败${NC}"
        exit 1
    fi
}

# 验证安装
verify_installation() {
    echo -e "\n${YELLOW}>>> 验证安装...${NC}"
    
    local all_ok=true
    
    # 验证 MySQL TCP 连接
    echo -n "MySQL TCP 连接测试 (127.0.0.1:${MYSQL_PORT}): "
    if mysql -u root -p"${MYSQL_PASSWORD}" -h 127.0.0.1 -P ${MYSQL_PORT} -e "SELECT 1;" &> /dev/null; then
        echo -e "${GREEN}✓ 成功${NC}"
    else
        echo -e "${RED}✗ 失败${NC}"
        all_ok=false
    fi
    
    # 验证数据库
    echo -n "数据库 ${MYSQL_DB} 检查: "
    if mysql -u root -p"${MYSQL_PASSWORD}" -h 127.0.0.1 -P ${MYSQL_PORT} -e "USE ${MYSQL_DB};" &> /dev/null; then
        echo -e "${GREEN}✓ 存在${NC}"
    else
        echo -e "${RED}✗ 不存在${NC}"
        all_ok=false
    fi
    
    # 验证 Redis
    echo -n "Redis 连接测试 (端口 ${REDIS_PORT}): "
    if redis-cli -p ${REDIS_PORT} -a "${REDIS_PASSWORD}" ping 2>/dev/null | grep -q "PONG"; then
        echo -e "${GREEN}✓ 成功${NC}"
    else
        echo -e "${RED}✗ 失败${NC}"
        all_ok=false
    fi
    
    if [ "$all_ok" = false ]; then
        echo -e "\n${RED}部分服务验证失败，请检查上述错误${NC}"
        exit 1
    fi
}

# 打印连接信息
print_connection_info() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  安装完成！连接信息如下：${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e ""
    echo -e "${YELLOW}MySQL:${NC}"
    echo -e "  Host:     127.0.0.1"
    echo -e "  Port:     ${MYSQL_PORT}"
    echo -e "  User:     ${MYSQL_USER}"
    echo -e "  Password: ${MYSQL_PASSWORD}"
    echo -e "  Database: ${MYSQL_DB}"
    echo -e ""
    echo -e "${YELLOW}Redis:${NC}"
    echo -e "  Host:     127.0.0.1"
    echo -e "  Port:     ${REDIS_PORT}"
    echo -e "  Password: ${REDIS_PASSWORD}"
    echo -e ""
    echo -e "${YELLOW}常用命令:${NC}"
    echo -e "  MySQL 连接:  mysql -u root -p'${MYSQL_PASSWORD}' ${MYSQL_DB}"
    echo -e "  Redis 连接:  redis-cli -p ${REDIS_PORT} -a '${REDIS_PASSWORD}'"
    echo -e ""
    echo -e "${YELLOW}服务管理:${NC}"
    echo -e "  启动 MySQL:  brew services start mysql"
    echo -e "  停止 MySQL:  brew services stop mysql"
    echo -e "  启动 Redis:  ${SCRIPT_DIR}/start_redis.sh"
    echo -e "  停止 Redis:  ${SCRIPT_DIR}/stop_redis.sh"
    echo -e "  状态检查:    ${SCRIPT_DIR}/status_db.sh"
}

# 主函数
main() {
    check_homebrew
    install_mysql
    configure_mysql_tcp
    ensure_mysql_running
    configure_mysql
    install_redis
    configure_redis
    start_redis
    verify_installation
    print_connection_info
}

# 运行
main
