#!/usr/bin/env python
"""
测试数据库连接池配置是否生效
运行方法：python manage.py shell < test_connection_pool.py
"""
import time
from django.db import connection, reset_queries
from backend.models.tb_primary_schools import TbPrimarySchools

print("=" * 80)
print("数据库连接池测试")
print("=" * 80)

# 显示当前配置
print(f"\n📋 当前数据库配置:")
print(f"  - CONN_MAX_AGE: {connection.settings_dict.get('CONN_MAX_AGE', 'Not set')}")
print(f"  - CONN_HEALTH_CHECKS: {connection.settings_dict.get('CONN_HEALTH_CHECKS', 'Not set')}")
print(f"  - HOST: {connection.settings_dict.get('HOST')}")
print(f"  - PORT: {connection.settings_dict.get('PORT')}")

# 测试1: 单次查询性能
print("\n" + "=" * 80)
print("测试1: 单次COUNT查询性能")
print("=" * 80)

# 强制关闭现有连接
connection.close()
reset_queries()

start = time.time()
connection.ensure_connection()
conn_time = (time.time() - start) * 1000
print(f"  ⏱️  连接建立耗时: {conn_time:.2f}ms")

start = time.time()
count = TbPrimarySchools.objects.count()
query_time = (time.time() - start) * 1000
print(f"  ⏱️  COUNT查询耗时: {query_time:.2f}ms")
print(f"  📊 查询结果: {count}条记录")

if len(connection.queries) > 0:
    db_time = float(connection.queries[-1]['time']) * 1000
    overhead = query_time - db_time
    print(f"  📊 数据库执行时间: {db_time:.2f}ms")
    print(f"  📊 Python开销时间: {overhead:.2f}ms")

# 测试2: 连接复用性能
print("\n" + "=" * 80)
print("测试2: 连接复用测试（5次连续查询）")
print("=" * 80)

times = []
for i in range(5):
    reset_queries()
    start = time.time()
    count = TbPrimarySchools.objects.count()
    query_time = (time.time() - start) * 1000
    times.append(query_time)
    
    db_time = float(connection.queries[-1]['time']) * 1000 if connection.queries else 0
    overhead = query_time - db_time
    
    print(f"  查询 #{i+1}: 总耗时={query_time:.2f}ms, 数据库={db_time:.2f}ms, 开销={overhead:.2f}ms")

avg_time = sum(times) / len(times)
print(f"\n  📊 平均查询时间: {avg_time:.2f}ms")

# 测试3: 关闭连接后再查询
print("\n" + "=" * 80)
print("测试3: 关闭连接后重新建立")
print("=" * 80)

connection.close()
print("  ✅ 已关闭数据库连接")

reset_queries()
start = time.time()
count = TbPrimarySchools.objects.count()
query_time = (time.time() - start) * 1000

db_time = float(connection.queries[-1]['time']) * 1000 if connection.queries else 0
overhead = query_time - db_time

print(f"  ⏱️  重建连接+查询耗时: {query_time:.2f}ms")
print(f"  📊 数据库执行时间: {db_time:.2f}ms")
print(f"  📊 连接建立开销: {overhead:.2f}ms")

# 检查连接状态
print("\n" + "=" * 80)
print("连接状态检查")
print("=" * 80)

try:
    with connection.cursor() as cursor:
        # 检查当前连接ID
        cursor.execute("SELECT CONNECTION_ID()")
        conn_id = cursor.fetchone()[0]
        print(f"  📌 当前连接ID: {conn_id}")
        
        # 检查连接数
        cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
        result = cursor.fetchone()
        threads_connected = result[1] if result else "N/A"
        print(f"  📊 数据库连接数: {threads_connected}")
        
        # 检查最大连接数
        cursor.execute("SHOW VARIABLES LIKE 'max_connections'")
        result = cursor.fetchone()
        max_connections = result[1] if result else "N/A"
        print(f"  📊 最大连接数: {max_connections}")
        
        # 检查连接超时设置
        cursor.execute("SHOW VARIABLES LIKE 'wait_timeout'")
        result = cursor.fetchone()
        wait_timeout = result[1] if result else "N/A"
        print(f"  ⏰ wait_timeout: {wait_timeout}秒")
        
        cursor.execute("SHOW VARIABLES LIKE 'interactive_timeout'")
        result = cursor.fetchone()
        interactive_timeout = result[1] if result else "N/A"
        print(f"  ⏰ interactive_timeout: {interactive_timeout}秒")
        
except Exception as e:
    print(f"  ❌ 无法获取连接状态: {e}")

# 性能建议
print("\n" + "=" * 80)
print("性能分析与建议")
print("=" * 80)

if avg_time < 50:
    print("  ✅ 性能优秀！平均查询时间 < 50ms")
elif avg_time < 100:
    print("  ⚠️  性能良好，但还有优化空间")
else:
    print("  ❌ 性能较差！需要优化")
    print("\n  建议检查：")
    print("    1. 数据库索引是否正确")
    print("    2. MySQL服务器负载")
    print("    3. 网络延迟")
    print("    4. Docker网络配置")

# 检查CONN_MAX_AGE是否生效
if connection.settings_dict.get('CONN_MAX_AGE', 0) > 0:
    print(f"\n  ✅ CONN_MAX_AGE已启用: {connection.settings_dict['CONN_MAX_AGE']}秒")
    print("     连接将被复用，避免频繁建立/关闭连接")
else:
    print("\n  ❌ CONN_MAX_AGE未启用或为0")
    print("     每次请求都会建立新连接，性能较差")
    print("     建议在settings.py中设置: CONN_MAX_AGE = 600")

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)

