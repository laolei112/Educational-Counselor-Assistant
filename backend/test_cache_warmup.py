#!/usr/bin/env python
"""
缓存预热系统测试脚本

用法:
    python test_cache_warmup.py
"""
import os
import sys
import django
import time
from django.core.management import call_command

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.cache import cache
from backend.scheduler import get_scheduler
from common.logger import loginfo


def print_section(title):
    """打印章节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_redis_connection():
    """测试 Redis 连接"""
    print_section("测试 1: Redis 连接")
    
    try:
        # 测试写入
        test_key = 'test_warmup_connection'
        test_value = 'test_value_123'
        cache.set(test_key, test_value, timeout=60)
        
        # 测试读取
        result = cache.get(test_key)
        
        if result == test_value:
            print("✅ Redis 连接正常")
            print(f"   写入测试: {test_key} = {test_value}")
            print(f"   读取测试: {result}")
            return True
        else:
            print("❌ Redis 读取失败")
            return False
            
    except Exception as e:
        print(f"❌ Redis 连接失败: {str(e)}")
        return False


def test_warmup_command():
    """测试预热命令"""
    print_section("测试 2: 缓存预热命令")
    
    try:
        start_time = time.time()
        
        # 清除已有缓存
        print("清除已有缓存...")
        call_command('clear_cache', '--schools')
        
        # 执行预热
        print("\n开始预热缓存...")
        call_command('warmup_cache', '--verbose')
        
        elapsed = time.time() - start_time
        print(f"\n✅ 预热命令执行成功")
        print(f"   总耗时: {elapsed:.2f} 秒")
        return True
        
    except Exception as e:
        print(f"❌ 预热命令执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_content():
    """测试缓存内容"""
    print_section("测试 3: 验证缓存内容")
    
    try:
        # 检查小学首页缓存
        from backend.api.schools.primary_views import get_cache_key_for_query
        
        query_params = {'page': 1, 'pageSize': 20}
        cache_key = get_cache_key_for_query(query_params)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            print("✅ 小学首页缓存存在")
            print(f"   缓存键: {cache_key}")
            print(f"   数据类型: {type(cached_data)}")
            if isinstance(cached_data, dict):
                print(f"   学校数量: {len(cached_data.get('list', []))} 所")
                print(f"   总记录数: {cached_data.get('total', 0)} 所")
        else:
            print("⚠️  小学首页缓存不存在")
            return False
        
        # 检查筛选选项缓存
        filters_key = 'primary_filters'
        filters_data = cache.get(filters_key)
        
        if filters_data:
            print("\n✅ 小学筛选选项缓存存在")
            print(f"   片区数量: {len(filters_data.get('districts', []))}")
            print(f"   校网数量: {len(filters_data.get('schoolNets', []))}")
            print(f"   类别数量: {len(filters_data.get('categories', []))}")
        else:
            print("\n⚠️  筛选选项缓存不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 缓存内容验证失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_scheduler():
    """测试调度器"""
    print_section("测试 4: 调度器状态")
    
    try:
        scheduler = get_scheduler()
        
        # 检查调度器状态
        is_running = scheduler.scheduler.running if scheduler.scheduler else False
        
        if is_running:
            print("✅ 调度器正在运行")
        else:
            print("⚠️  调度器未运行")
        
        # 获取任务列表
        jobs = scheduler.get_jobs()
        print(f"\n已配置 {len(jobs)} 个定时任务:")
        
        for job in jobs:
            print(f"\n  📅 {job['name']}")
            print(f"     ID: {job['id']}")
            print(f"     下次执行: {job['next_run']}")
            print(f"     触发器: {job['trigger']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 调度器测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_performance():
    """测试性能提升"""
    print_section("测试 5: 性能对比")
    
    try:
        from django.test import RequestFactory
        from backend.api.schools.primary_views import primary_school_list_view
        
        factory = RequestFactory()
        
        # 清除缓存，测试无缓存性能
        print("测试 1: 无缓存性能")
        call_command('clear_cache', '--schools')
        
        request = factory.get('/api/schools/primary/', {'page': 1, 'pageSize': 20})
        start_time = time.time()
        response = primary_school_list_view(request)
        no_cache_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        print(f"   响应时间: {no_cache_time:.2f} ms")
        
        # 预热缓存，测试有缓存性能
        print("\n测试 2: 有缓存性能")
        call_command('warmup_cache', '--primary')
        
        request = factory.get('/api/schools/primary/', {'page': 1, 'pageSize': 20})
        start_time = time.time()
        response = primary_school_list_view(request)
        with_cache_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        print(f"   响应时间: {with_cache_time:.2f} ms")
        
        # 计算提升
        if no_cache_time > 0 and with_cache_time > 0:
            improvement = ((no_cache_time - with_cache_time) / no_cache_time) * 100
            speedup = no_cache_time / with_cache_time
            
            print(f"\n✅ 性能提升")
            print(f"   提升幅度: {improvement:.1f}%")
            print(f"   加速倍数: {speedup:.1f}x")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "🚀"*30)
    print("   缓存预热系统测试")
    print("🚀"*30)
    
    results = []
    
    # 执行测试
    results.append(("Redis 连接", test_redis_connection()))
    results.append(("预热命令", test_warmup_command()))
    results.append(("缓存内容", test_cache_content()))
    results.append(("调度器", test_scheduler()))
    results.append(("性能对比", test_performance()))
    
    # 总结
    print_section("测试总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}  {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！缓存预热系统运行正常。")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息。")
        return 1


if __name__ == '__main__':
    sys.exit(main())

