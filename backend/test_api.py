#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单的API测试脚本
用于验证学校API接口是否正常工作
"""

import requests
import json

BASE_URL = "http://localhost:8080/api"

def test_schools_list():
    """测试学校列表接口"""
    print("Testing GET /api/schools")
    try:
        response = requests.get(f"{BASE_URL}/schools/")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_schools_with_filter():
    """测试带筛选的学校列表接口"""
    print("Testing GET /api/schools?type=secondary")
    try:
        response = requests.get(f"{BASE_URL}/schools/", params={"type": "secondary"})
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_school_detail():
    """测试学校详情接口"""
    print("Testing GET /api/schools/1/")
    try:
        response = requests.get(f"{BASE_URL}/schools/1/")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_schools_stats():
    """测试学校统计接口"""
    print("Testing GET /api/schools/stats/")
    try:
        response = requests.get(f"{BASE_URL}/schools/stats/")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_schools_stats_with_type():
    """测试带类型筛选的学校统计接口"""
    print("Testing GET /api/schools/stats/?type=primary")
    try:
        response = requests.get(f"{BASE_URL}/schools/stats/", params={"type": "primary"})
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """运行所有测试"""
    print("🚀 开始测试学校API接口...")
    print("=" * 60)
    
    tests = [
        ("学校列表", test_schools_list),
        ("学校列表(筛选)", test_schools_with_filter),
        ("学校详情", test_school_detail),
        ("学校统计", test_schools_stats),
        ("学校统计(筛选)", test_schools_stats_with_type),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"📋 {test_name}:")
        success = test_func()
        results.append((test_name, success))
        if success:
            print("✅ 通过")
        else:
            print("❌ 失败")
        print()
    
    print("=" * 60)
    print("📊 测试结果汇总:")
    success_count = 0
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n🎯 总体结果: {success_count}/{len(results)} 个测试通过")
    
    if success_count == len(results):
        print("🎉 所有API接口测试通过！前端可以正常连接。")
    else:
        print("⚠️  部分测试失败，请检查Django服务器是否正常运行。")

if __name__ == "__main__":
    main() 