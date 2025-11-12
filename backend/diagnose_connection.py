#!/usr/bin/env python
"""
诊断Django数据库连接池配置
运行方法: python manage.py shell < diagnose_connection.py
或: docker-compose exec backend python manage.py shell < diagnose_connection.py
"""
import os
import sys
import time

print("=" * 80)
print("Django数据库连接池诊断工具")
print("=" * 80)

# 1. 检查Django配置
print("\n1️⃣ 检查Django数据库配置")
print("-" * 80)

from django.conf import settings
from django.db import connection

db_settings = settings.DATABASES['default']
print(f"ENGINE: {db_settings.get('ENGINE')}")
print(f"HOST: {db_settings.get('HOST')}")
print(f"PORT: {db_settings.get('PORT')}")
print(f"NAME: {db_settings.get('NAME')}")
print(f"CONN_MAX_AGE: {db_settings.get('CONN_MAX_AGE', 'NOT SET')}")
print(f"CONN_HEALTH_CHECKS: {db_settings.get('CONN_HEALTH_CHECKS', 'NOT SET')}")

# 检查连接配置
print(f"\n从connection对象读取:")
print(f"CONN_MAX_AGE: {connection.settings_dict.get('CONN_MAX_AGE', 'NOT SET')}")
print(f"CONN_HEALTH_CHECKS: {connection.settings_dict.get('CONN_HEALTH_CHECKS', 'NOT SET')}")

if connection.settings_dict.get('CONN_MAX_AGE', 0) == 0:
    print("❌ 警告：CONN_MAX_AGE = 0，连接池未启用！")
elif connection.settings_dict.get('CONN_MAX_AGE') is None:
    print("❌ 警告：CONN_MAX_AGE = None，永久连接（可能导致问题）")
else:
    print(f"✅ CONN_MAX_AGE = {connection.settings_dict.get('CONN_MAX_AGE')}秒")

# 2. 测试连接性能
print("\n2️⃣ 测试数据库连接性能")
print("-" * 80)

from backend.models.tb_primary_schools import TbPrimarySchools

# 关闭现有连接
connection.close()
print("已关闭现有连接")

# 第1次查询（需要建立连接）
print("\n第1次查询（需要建立连接）:")
start = time.time()
connection.ensure_connection()
conn_time1 = (time.time() - start) * 1000
print(f"  连接建立耗时: {conn_time1:.2f}ms")

start = time.time()
count1 = TbPrimarySchools.objects.count()
query_time1 = (time.time() - start) * 1000
print(f"  查询耗时: {query_time1:.2f}ms")
print(f"  查询结果: {count1}条记录")

# 检查连接是否打开
print(f"  连接状态: {'打开' if connection.connection else '关闭'}")

# 第2次查询（应该复用连接）
print("\n第2次查询（应该复用连接）:")
start = time.time()
connection.ensure_connection()
conn_time2 = (time.time() - start) * 1000
print(f"  连接获取耗时: {conn_time2:.2f}ms")

start = time.time()
count2 = TbPrimarySchools.objects.count()
query_time2 = (time.time() - start) * 1000
print(f"  查询耗时: {query_time2:.2f}ms")

# 检查连接是否打开
print(f"  连接状态: {'打开' if connection.connection else '关闭'}")

# 性能对比
print(f"\n性能对比:")
print(f"  第1次连接: {conn_time1:.2f}ms")
print(f"  第2次连接: {conn_time2:.2f}ms")
print(f"  性能提升: {conn_time1 / conn_time2:.1f}倍" if conn_time2 > 0 else "  性能提升: N/A")

if conn_time2 < 10:
    print("  ✅ 连接复用成功！")
elif conn_time2 < 50:
    print("  ⚠️  连接复用可能有问题")
else:
    print("  ❌ 连接复用失败！每次都建立新连接")

# 3. 检查环境信息
print("\n3️⃣ 环境信息")
print("-" * 80)
print(f"Python版本: {sys.version}")
print(f"Django版本: {__import__('django').get_version()}")
print(f"进程ID: {os.getpid()}")

# 检查是否在gunicorn中运行
try:
    import gunicorn
    print(f"Gunicorn版本: {gunicorn.__version__}")
except:
    print("Gunicorn: 未安装或未在gunicorn中运行")

# 检查是否使用gevent
try:
    import gevent
    print(f"Gevent版本: {gevent.__version__}")
    print("⚠️  警告: 使用gevent可能影响Django连接池行为")
except:
    print("Gevent: 未安装")

# 4. 检查MySQL服务器状态
print("\n4️⃣ MySQL服务器状态")
print("-" * 80)

try:
    with connection.cursor() as cursor:
        # 当前连接ID
        cursor.execute("SELECT CONNECTION_ID()")
        conn_id = cursor.fetchone()[0]
        print(f"当前连接ID: {conn_id}")
        
        # 连接数
        cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
        result = cursor.fetchone()
        threads_connected = result[1] if result else "N/A"
        
        cursor.execute("SHOW VARIABLES LIKE 'max_connections'")
        result = cursor.fetchone()
        max_connections = result[1] if result else "N/A"
        
        print(f"当前连接数: {threads_connected}")
        print(f"最大连接数: {max_connections}")
        
        if threads_connected != "N/A" and max_connections != "N/A":
            usage = int(threads_connected) / int(max_connections) * 100
            print(f"连接池使用率: {usage:.1f}%")
            if usage > 80:
                print("⚠️  警告: 连接数接近上限！")
        
        # wait_timeout
        cursor.execute("SHOW VARIABLES LIKE 'wait_timeout'")
        result = cursor.fetchone()
        wait_timeout = result[1] if result else "N/A"
        print(f"wait_timeout: {wait_timeout}秒")
        
except Exception as e:
    print(f"❌ 无法获取MySQL状态: {e}")

# 5. 推荐的修复方案
print("\n5️⃣ 诊断结果与建议")
print("-" * 80)

issues = []
recommendations = []

if connection.settings_dict.get('CONN_MAX_AGE', 0) == 0:
    issues.append("CONN_MAX_AGE = 0，连接池未启用")
    recommendations.append("在settings.py中设置 CONN_MAX_AGE = 600")

if conn_time1 > 200:
    issues.append(f"首次连接耗时 {conn_time1:.0f}ms，超过200ms")
    recommendations.append("检查网络延迟和MySQL服务器性能")

if conn_time2 > 50:
    issues.append(f"第二次连接耗时 {conn_time2:.0f}ms，应该 < 10ms")
    recommendations.append("连接未被复用，检查是否使用多worker或gevent")

try:
    import gevent
    issues.append("使用了gevent worker")
    recommendations.append("考虑使用 sync 或 gthread worker类型，避免gevent影响连接池")
except:
    pass

if issues:
    print("❌ 发现以下问题:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    
    print("\n💡 建议:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
else:
    print("✅ 未发现明显问题")

print("\n" + "=" * 80)
print("诊断完成")
print("=" * 80)

