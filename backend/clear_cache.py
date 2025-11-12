#!/usr/bin/env python
"""
清除Django缓存脚本
用于在更新序列化格式后清除旧的缓存数据
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.cache import cache

def clear_all_cache():
    """清除所有缓存"""
    try:
        cache.clear()
        print("✅ 成功清除所有缓存！")
        return True
    except Exception as e:
        print(f"❌ 清除缓存失败: {e}")
        return False

def clear_pattern_cache(pattern):
    """清除匹配模式的缓存"""
    try:
        # Redis backend 支持通配符删除
        from django.core.cache import cache
        if hasattr(cache, 'delete_pattern'):
            deleted = cache.delete_pattern(f"*{pattern}*")
            print(f"✅ 清除匹配 '{pattern}' 的缓存，共删除 {deleted} 个键")
        else:
            print("⚠️  当前缓存后端不支持模式删除，使用 clear_all_cache()")
            clear_all_cache()
    except Exception as e:
        print(f"❌ 清除缓存失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Django 缓存清除工具")
    print("=" * 50)
    
    # 清除小学和中学列表缓存
    print("\n清除列表接口缓存...")
    clear_pattern_cache("primary_schools_list:")
    clear_pattern_cache("secondary_schools_list:")
    
    # 如果需要清除所有缓存，取消下面的注释
    # print("\n清除所有缓存...")
    # clear_all_cache()
    
    print("\n" + "=" * 50)
    print("✅ 缓存清除完成！")
    print("=" * 50)

