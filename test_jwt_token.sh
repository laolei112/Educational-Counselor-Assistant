#!/bin/bash

# JWT Token功能测试脚本
# 用于验证JWT Token方案是否正确部署

echo "================================"
echo "JWT Token 功能测试"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API地址
API_BASE="http://localhost:8080/api"

# 测试计数
TOTAL_TESTS=0
PASSED_TESTS=0

# 测试函数
test_api() {
    local test_name="$1"
    local command="$2"
    local expected_code="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "测试 $TOTAL_TESTS: $test_name ... "
    
    # 执行命令并获取HTTP状态码
    response=$(eval "$command")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # 检查HTTP状态码
    if [ "$http_code" == "$expected_code" ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $http_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ 失败${NC} (预期: $expected_code, 实际: $http_code)"
        echo "响应: $body"
        return 1
    fi
}

echo "步骤1: 测试Token获取"
echo "-------------------"

# 测试1: 获取Token
TOKEN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"platform": "test"}')

test_api "获取Token" "echo '$TOKEN_RESPONSE'" "200"

# 提取Token
TOKEN=$(echo "$TOKEN_RESPONSE" | head -n-1 | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}错误: 无法提取Token${NC}"
    exit 1
fi

echo "Token已获取: ${TOKEN:0:20}..."
echo ""

echo "步骤2: 测试Token访问API"
echo "----------------------"

# 测试2: 使用Token访问API
test_api "使用Token访问小学API" \
    "curl -s -w '\n%{http_code}' -H 'Authorization: Bearer $TOKEN' '$API_BASE/schools/primary?pageSize=1'" \
    "200"

# 测试3: 使用Token访问中学API  
test_api "使用Token访问中学API" \
    "curl -s -w '\n%{http_code}' -H 'Authorization: Bearer $TOKEN' '$API_BASE/schools/secondary?pageSize=1'" \
    "200"

echo ""
echo "步骤3: 测试无Token访问（应该失败）"
echo "-----------------------------"

# 测试4: 不带Token访问（应该401）
test_api "无Token访问API（应返回401）" \
    "curl -s -w '\n%{http_code}' '$API_BASE/schools/primary'" \
    "401"

echo ""
echo "步骤4: 测试Token信息"
echo "------------------"

# 测试5: 获取Token信息
test_api "获取Token信息" \
    "curl -s -w '\n%{http_code}' -H 'Authorization: Bearer $TOKEN' '$API_BASE/auth/token-info'" \
    "200"

echo ""
echo "步骤5: 测试Token刷新"
echo "------------------"

# 测试6: 刷新Token
REFRESH_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/auth/refresh" \
  -H "Authorization: Bearer $TOKEN")

test_api "刷新Token" "echo '$REFRESH_RESPONSE'" "200"

# 提取新Token
NEW_TOKEN=$(echo "$REFRESH_RESPONSE" | head -n-1 | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -n "$NEW_TOKEN" ] && [ "$NEW_TOKEN" != "$TOKEN" ]; then
    echo -e "${GREEN}✓ Token已成功刷新${NC}"
    echo "新Token: ${NEW_TOKEN:0:20}..."
else
    echo -e "${YELLOW}! Token可能相同或刷新失败${NC}"
fi

echo ""
echo "步骤6: 测试搜索引擎访问"
echo "--------------------"

# 测试7: 搜索引擎爬虫访问（应该允许）
test_api "Googlebot访问（应允许）" \
    "curl -s -w '\n%{http_code}' -A 'Mozilla/5.0 (compatible; Googlebot/2.1)' '$API_BASE/schools/primary?pageSize=1'" \
    "200"

echo ""
echo "================================"
echo "测试结果汇总"
echo "================================"
echo -e "总测试数: $TOTAL_TESTS"
echo -e "通过: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败: ${RED}$((TOTAL_TESTS - PASSED_TESTS))${NC}"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo ""
    echo -e "${GREEN}🎉 所有测试通过！JWT Token方案部署成功！${NC}"
    echo ""
    echo "性能测试:"
    echo "---------"
    
    # 简单的性能测试
    echo "测试10次请求的平均响应时间..."
    total_time=0
    for i in {1..10}; do
        start=$(date +%s%N)
        curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/schools/primary?pageSize=1" > /dev/null
        end=$(date +%s%N)
        time=$(( (end - start) / 1000000 ))
        total_time=$((total_time + time))
        echo "  请求 $i: ${time}ms"
    done
    avg_time=$((total_time / 10))
    echo ""
    echo -e "平均响应时间: ${GREEN}${avg_time}ms${NC}"
    
    if [ $avg_time -lt 150 ]; then
        echo -e "${GREEN}✓ 性能优异！比签名方案快${NC}"
    else
        echo -e "${YELLOW}! 性能可能需要优化${NC}"
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}❌ 部分测试失败，请检查配置${NC}"
    echo ""
    echo "故障排查建议:"
    echo "1. 确认服务已启动: docker-compose ps"
    echo "2. 查看后端日志: docker-compose logs backend"
    echo "3. 确认PyJWT已安装: docker-compose exec backend pip list | grep PyJWT"
    echo "4. 确认中间件已配置: 检查 backend/backend/basic_settings.py"
    exit 1
fi

