#!/usr/bin/env python3
"""
测试中学 API 接口
验证从 tb_secondary_schools 表读取数据
"""

import requests
import json

# API 基础 URL
BASE_URL = "http://localhost:8000"
# 如果在 Docker 环境，使用以下 URL
# BASE_URL = "http://backend:8000"


def test_api(endpoint, params=None):
    """测试 API 接口"""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, params=params)
        print(f"\n{'='*60}")
        print(f"测试接口: {endpoint}")
        if params:
            print(f"查询参数: {json.dumps(params, ensure_ascii=False)}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应成功: {data.get('success', False)}")
            print(f"消息: {data.get('message', '')}")
            
            if 'data' in data:
                result = data['data']
                
                # 如果是列表数据
                if isinstance(result, dict) and 'list' in result:
                    print(f"总记录数: {result.get('total', 0)}")
                    print(f"当前页: {result.get('page', 0)}")
                    print(f"每页数量: {result.get('pageSize', 0)}")
                    print(f"总页数: {result.get('totalPages', 0)}")
                    
                    schools = result.get('list', [])
                    print(f"\n前 3 条数据:")
                    for i, school in enumerate(schools[:3], 1):
                        print(f"\n  {i}. {school.get('name', 'Unknown')}")
                        print(f"     ID: {school.get('id')}")
                        print(f"     类型: {school.get('type')}")
                        print(f"     区域: {school.get('district')}")
                        print(f"     类别: {school.get('category')}")
                        if school.get('schoolGroup'):
                            print(f"     组别: {school.get('schoolGroup')}")
                        if school.get('gender'):
                            print(f"     性别: {school.get('gender')}")
                
                # 如果是详情数据
                elif isinstance(result, dict) and 'name' in result:
                    print(f"\n学校详情:")
                    print(f"  名称: {result.get('name')}")
                    print(f"  ID: {result.get('id')}")
                    print(f"  类型: {result.get('type')}")
                    print(f"  区域: {result.get('district')}")
                    print(f"  地址: {result.get('address', 'N/A')}")
                    print(f"  电话: {result.get('phone', 'N/A')}")
                    print(f"  邮箱: {result.get('email', 'N/A')}")
                    print(f"  网站: {result.get('website', 'N/A')}")
                    if result.get('schoolGroup'):
                        print(f"  组别: {result.get('schoolGroup')}")
                    if result.get('totalClasses'):
                        print(f"  总班数: {result.get('totalClasses')}")
                
                # 如果是统计数据
                elif isinstance(result, dict) and 'totalSchools' in result:
                    print(f"\n统计信息:")
                    print(f"  总学校数: {result.get('totalSchools', 0)}")
                    
                    if 'districtStats' in result:
                        print(f"\n  区域分布:")
                        for district, count in list(result['districtStats'].items())[:5]:
                            print(f"    {district}: {count}")
                    
                    if 'categoryStats' in result:
                        print(f"\n  类别分布:")
                        for category, count in result['categoryStats'].items():
                            print(f"    {category}: {count}")
                    
                    if 'groupStats' in result:
                        print(f"\n  组别分布:")
                        for group, count in list(result['groupStats'].items())[:5]:
                            print(f"    {group}: {count}")
            
            print(f"{'='*60}")
            return True
        else:
            print(f"请求失败: {response.text}")
            print(f"{'='*60}")
            return False
            
    except Exception as e:
        print(f"错误: {str(e)}")
        print(f"{'='*60}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("中学 API 接口测试")
    print("=" * 60)
    
    # 测试计数
    total_tests = 0
    passed_tests = 0
    
    # 1. 测试中学列表接口
    total_tests += 1
    if test_api("/api/schools/secondary", {"page": 1, "pageSize": 20}):
        passed_tests += 1
    
    # 2. 测试中学列表（带关键词搜索）
    total_tests += 1
    if test_api("/api/schools/secondary", {"keyword": "拔萃", "page": 1, "pageSize": 10}):
        passed_tests += 1
    
    # 3. 测试中学列表（按区域筛选）
    total_tests += 1
    if test_api("/api/schools/secondary", {"district": "九龙城区", "page": 1, "pageSize": 10}):
        passed_tests += 1
    
    # 4. 测试中学列表（按组别筛选）
    total_tests += 1
    if test_api("/api/schools/secondary", {"schoolGroup": "1B", "page": 1, "pageSize": 10}):
        passed_tests += 1
    
    # 5. 测试中学详情接口（需要先确认有数据）
    total_tests += 1
    if test_api("/api/schools/secondary/1"):
        passed_tests += 1
    
    # 6. 测试中学统计接口
    total_tests += 1
    if test_api("/api/schools/secondary/stats"):
        passed_tests += 1
    
    # 7. 测试小学列表接口（确保小学接口不受影响）
    total_tests += 1
    if test_api("/api/schools/primary", {"page": 1, "pageSize": 10}):
        passed_tests += 1
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试数: {total_tests}")
    print(f"通过: {passed_tests}")
    print(f"失败: {total_tests - passed_tests}")
    print(f"通过率: {passed_tests / total_tests * 100:.1f}%")
    print("=" * 60)
    
    if passed_tests == total_tests:
        print("✓ 所有测试通过！")
    else:
        print("✗ 部分测试失败，请检查日志")


if __name__ == '__main__':
    main()

