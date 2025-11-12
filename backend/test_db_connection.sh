#!/bin/bash

echo "=================================="
echo "数据库连接性能测试"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "步骤1: 重启后端服务..."
docker-compose restart backend
sleep 3

echo ""
echo "步骤2: 等待服务启动..."
for i in {1..10}; do
    if curl -s http://localhost:8000/api/schools/primary/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 服务已启动${NC}"
        break
    fi
    echo "  等待中... ($i/10)"
    sleep 2
done

echo ""
echo "步骤3: 发送测试请求..."
echo "=================================="

# 发送5次请求测试
for i in {1..5}; do
    echo ""
    echo "--- 请求 #$i ---"
    
    # 记录开始时间
    start_time=$(date +%s%3N)
    
    # 发送请求
    response=$(curl -s -w "\n%{time_total}" http://localhost:8000/api/schools/primary/)
    
    # 记录结束时间
    end_time=$(date +%s%3N)
    
    # 计算耗时
    total_time=$((end_time - start_time))
    
    # 提取curl报告的时间
    curl_time=$(echo "$response" | tail -n 1)
    
    echo "  ⏱️  总耗时: ${total_time}ms"
    echo "  ⏱️  curl耗时: ${curl_time}s"
    
    # 性能评估
    if [ $total_time -lt 100 ]; then
        echo -e "  ${GREEN}✅ 性能优秀！${NC}"
    elif [ $total_time -lt 500 ]; then
        echo -e "  ${YELLOW}⚠️  性能一般${NC}"
    else
        echo -e "  ${RED}❌ 性能较差${NC}"
    fi
    
    sleep 1
done

echo ""
echo "=================================="
echo "步骤4: 查看日志分析"
echo "=================================="
echo ""
echo "最近的SQL性能日志："
echo "---"
docker-compose logs backend --tail 50 | grep "\[SQL_DEBUG\]" | tail -20

echo ""
echo "=================================="
echo "测试完成！"
echo "=================================="
echo ""
echo "📊 性能指标说明："
echo "  - 连接获取耗时应该 < 10ms（第二次请求开始）"
echo "  - 网络+开销耗时应该 < 20ms"
echo "  - COUNT查询总耗时应该 < 50ms"
echo "  - API总响应时间应该 < 200ms"
echo ""
echo "如果看到连接获取耗时 > 100ms，说明连接池未生效"
echo ""

