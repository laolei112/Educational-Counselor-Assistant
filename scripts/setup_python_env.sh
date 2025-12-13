#!/bin/bash

# ============================================
# Python 虚拟环境安装脚本
# 创建 venv 并安装依赖
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="${PROJECT_DIR}/venv"
BACKEND_DIR="${PROJECT_DIR}/backend"
REQUIREMENTS_FILE="${BACKEND_DIR}/requirements.txt"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Python 虚拟环境安装脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查并安装 Python
check_python() {
    echo -e "\n${YELLOW}>>> 检查 Python...${NC}"
    
    # 优先使用 Homebrew 的 Python 3.11
    if [ -x "/opt/homebrew/bin/python3.11" ]; then
        PYTHON_BIN="/opt/homebrew/bin/python3.11"
    elif [ -x "/opt/homebrew/opt/python@3.11/bin/python3.11" ]; then
        PYTHON_BIN="/opt/homebrew/opt/python@3.11/bin/python3.11"
    elif command -v python3.11 &> /dev/null; then
        PYTHON_BIN="python3.11"
    else
        echo -e "${YELLOW}Python 3.11 未安装，正在通过 Homebrew 安装...${NC}"
        brew install python@3.11
        PYTHON_BIN="/opt/homebrew/opt/python@3.11/bin/python3.11"
    fi
    
    if [ -x "${PYTHON_BIN}" ] || command -v "${PYTHON_BIN}" &> /dev/null; then
        PYTHON_VERSION=$(${PYTHON_BIN} --version 2>&1)
        echo -e "${GREEN}✓ ${PYTHON_VERSION} (${PYTHON_BIN})${NC}"
    else
        echo -e "${RED}✗ Python 安装失败${NC}"
        exit 1
    fi
}

# 安装编译依赖 (mysqlclient 需要)
install_build_deps() {
    echo -e "\n${YELLOW}>>> 检查编译依赖...${NC}"
    
    # 检查并安装 pkg-config
    if ! command -v pkg-config &> /dev/null; then
        echo "安装 pkg-config..."
        brew install pkg-config
    else
        echo -e "${GREEN}✓ pkg-config 已安装${NC}"
    fi
    
    # 检查并安装 mysql-client (mysqlclient 编译需要)
    if ! brew list mysql-client &> /dev/null && ! brew list mysql &> /dev/null; then
        echo "安装 mysql-client..."
        brew install mysql-client
    else
        echo -e "${GREEN}✓ mysql-client 已安装${NC}"
    fi
    
    # 设置环境变量让 mysqlclient 能找到 mysql 库
    # mysql-client 是 keg-only，需要手动设置 PKG_CONFIG_PATH
    if brew list mysql-client &> /dev/null; then
        export PKG_CONFIG_PATH="/opt/homebrew/opt/mysql-client/lib/pkgconfig:${PKG_CONFIG_PATH}"
        export LDFLAGS="-L/opt/homebrew/opt/mysql-client/lib ${LDFLAGS}"
        export CPPFLAGS="-I/opt/homebrew/opt/mysql-client/include ${CPPFLAGS}"
    fi
    
    echo -e "${GREEN}✓ 编译依赖检查完成${NC}"
}

# 创建虚拟环境
create_venv() {
    echo -e "\n${YELLOW}>>> 创建虚拟环境...${NC}"
    
    if [ -d "${VENV_DIR}" ]; then
        echo -e "${YELLOW}虚拟环境已存在，是否重建? (删除旧环境)${NC}"
        # 自动使用已存在的环境
        echo -e "${GREEN}✓ 使用已存在的虚拟环境: ${VENV_DIR}${NC}"
        return
    fi
    
    echo "创建虚拟环境: ${VENV_DIR}"
    ${PYTHON_BIN} -m venv "${VENV_DIR}"
    
    if [ -d "${VENV_DIR}" ]; then
        echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
    else
        echo -e "${RED}✗ 虚拟环境创建失败${NC}"
        exit 1
    fi
}

# 激活虚拟环境并升级 pip
activate_and_upgrade_pip() {
    echo -e "\n${YELLOW}>>> 激活虚拟环境并升级 pip...${NC}"
    
    source "${VENV_DIR}/bin/activate"
    
    echo "升级 pip..."
    pip install --upgrade pip -q
    
    echo -e "${GREEN}✓ pip 已升级${NC}"
}

# 安装依赖
install_dependencies() {
    echo -e "\n${YELLOW}>>> 安装 Python 依赖...${NC}"
    
    if [ ! -f "${REQUIREMENTS_FILE}" ]; then
        echo -e "${RED}✗ requirements.txt 不存在: ${REQUIREMENTS_FILE}${NC}"
        exit 1
    fi
    
    echo "安装依赖: ${REQUIREMENTS_FILE}"
    pip install -r "${REQUIREMENTS_FILE}"
    
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
}

# 验证安装
verify_installation() {
    echo -e "\n${YELLOW}>>> 验证安装...${NC}"
    
    echo -n "Django: "
    if python -c "import django; print(django.get_version())" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗ 未安装${NC}"
    fi
    
    echo -n "mysqlclient: "
    if python -c "import MySQLdb; print('OK')" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗ 未安装${NC}"
    fi
    
    echo -n "redis: "
    if python -c "import redis; print('OK')" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗ 未安装${NC}"
    fi
}

# 打印使用说明
print_usage() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  安装完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e ""
    echo -e "${YELLOW}激活虚拟环境:${NC}"
    echo -e "  source ${VENV_DIR}/bin/activate"
    echo -e ""
    echo -e "${YELLOW}退出虚拟环境:${NC}"
    echo -e "  deactivate"
    echo -e ""
    echo -e "${YELLOW}运行 Django 开发服务器:${NC}"
    echo -e "  cd ${BACKEND_DIR}"
    echo -e "  python manage.py runserver"
    echo -e ""
    echo -e "${YELLOW}数据库迁移:${NC}"
    echo -e "  python manage.py migrate"
}

# 主函数
main() {
    check_python
    install_build_deps
    create_venv
    activate_and_upgrade_pip
    install_dependencies
    verify_installation
    print_usage
}

# 运行
main
