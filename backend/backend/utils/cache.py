"""
Redis缓存工具类
提供统一的缓存接口和装饰器
"""
import json
import hashlib
from functools import wraps
from django.core.cache import cache
from django.conf import settings


class CacheManager:
    """缓存管理器"""
    
    # 缓存前缀
    PREFIX_SCHOOL_LIST = "school:list:"
    PREFIX_SCHOOL_DETAIL = "school:detail:"
    PREFIX_SCHOOL_STATS = "school:stats:"
    
    # 缓存过期时间（秒）
    TIMEOUT_SHORT = 300      # 5分钟 - 用于列表数据
    TIMEOUT_MEDIUM = 1800    # 30分钟 - 用于详情数据
    TIMEOUT_LONG = 3600      # 1小时 - 用于统计数据
    
    @staticmethod
    def generate_cache_key(prefix: str, **kwargs) -> str:
        """
        生成缓存key
        :param prefix: 缓存前缀
        :param kwargs: 参数字典
        :return: 缓存key
        """
        # 将参数排序并序列化
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        
        # 生成hash值（避免key过长）
        hash_value = hashlib.md5(params_str.encode()).hexdigest()
        
        return f"{prefix}{hash_value}"
    
    @staticmethod
    def get(key: str):
        """获取缓存"""
        return cache.get(key)
    
    @staticmethod
    def set(key: str, value, timeout=None):
        """设置缓存"""
        return cache.set(key, value, timeout)
    
    @staticmethod
    def delete(key: str):
        """删除缓存"""
        return cache.delete(key)
    
    @staticmethod
    def delete_pattern(pattern: str):
        """
        删除匹配模式的所有缓存
        注意：这需要Redis支持，Django默认缓存后端不支持
        """
        try:
            from django.core.cache import caches
            redis_cache = caches['default']
            if hasattr(redis_cache, 'delete_pattern'):
                return redis_cache.delete_pattern(pattern)
        except Exception:
            pass
        return False
    
    @staticmethod
    def clear_school_cache():
        """清除所有学校相关缓存"""
        CacheManager.delete_pattern(CacheManager.PREFIX_SCHOOL_LIST + "*")
        CacheManager.delete_pattern(CacheManager.PREFIX_SCHOOL_DETAIL + "*")
        CacheManager.delete_pattern(CacheManager.PREFIX_SCHOOL_STATS + "*")


def cache_response(prefix: str, timeout: int = 300):
    """
    缓存响应的装饰器
    :param prefix: 缓存key前缀
    :param timeout: 过期时间（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 从request中提取查询参数
            request = args[0] if args else None
            if not request:
                return func(*args, **kwargs)
            
            # 生成缓存key
            cache_params = dict(request.GET.items())
            cache_key = CacheManager.generate_cache_key(prefix, **cache_params)
            
            # 尝试从缓存获取
            cached_data = CacheManager.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            # 执行函数获取数据
            response = func(*args, **kwargs)
            
            # 缓存结果
            if hasattr(response, 'status_code') and response.status_code == 200:
                CacheManager.set(cache_key, response, timeout)
            
            return response
        
        return wrapper
    return decorator


def cache_queryset(prefix: str, timeout: int = 300):
    """
    缓存QuerySet结果的装饰器
    :param prefix: 缓存key前缀  
    :param timeout: 过期时间（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存key
            cache_key = CacheManager.generate_cache_key(
                prefix, 
                args=str(args),
                kwargs=str(kwargs)
            )
            
            # 尝试从缓存获取
            cached_data = CacheManager.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            # 执行查询
            result = func(*args, **kwargs)
            
            # 缓存结果（转为list，因为QuerySet不能直接缓存）
            if hasattr(result, '__iter__'):
                result = list(result)
            
            CacheManager.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    return decorator

