"""
性能监控中间件
记录请求耗时和数据库查询统计
"""
import time
import logging
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('performance')


class PerformanceMonitorMiddleware(MiddlewareMixin):
    """
    性能监控中间件
    记录每个请求的：
    1. 总耗时
    2. SQL查询数量
    3. SQL总耗时
    """
    
    def process_request(self, request):
        """请求开始时记录时间"""
        request._start_time = time.time()
        request._queries_before = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        """请求结束时计算性能指标"""
        if not hasattr(request, '_start_time'):
            return response
        
        # 计算总耗时
        duration = time.time() - request._start_time
        
        # 计算SQL查询统计
        queries_count = len(connection.queries) - request._queries_before
        queries_time = sum(float(q['time']) for q in connection.queries[request._queries_before:])
        
        # 记录到响应头
        response['X-Request-Duration'] = f'{duration:.3f}s'
        response['X-Database-Queries'] = str(queries_count)
        response['X-Database-Time'] = f'{queries_time:.3f}s'
        
        # 如果请求耗时超过1秒，记录警告日志
        if duration > 1.0:
            logger.warning(
                f'Slow request: {request.method} {request.path} '
                f'took {duration:.3f}s '
                f'({queries_count} queries, {queries_time:.3f}s)'
            )
        
        # 如果SQL查询过多，记录警告
        if queries_count > 20:
            logger.warning(
                f'Too many queries: {request.method} {request.path} '
                f'executed {queries_count} database queries'
            )
        
        # 记录到控制台（开发模式）
        if hasattr(request, '_start_time'):
            print(
                f'\n[Performance] {request.method} {request.path}\n'
                f'  Total Time: {duration:.3f}s\n'
                f'  DB Queries: {queries_count} ({queries_time:.3f}s)\n'
                f'  Cache Hit: {response.get("X-Cache-Hit", "N/A")}\n'
            )
        
        return response


class CacheHitMiddleware(MiddlewareMixin):
    """
    缓存命中率监控中间件
    """
    
    def process_response(self, request, response):
        """标记缓存是否命中"""
        # 这个需要在视图中设置
        if not hasattr(response, '_cache_hit'):
            response['X-Cache-Hit'] = 'MISS'
        
        return response


class SQLDebugMiddleware(MiddlewareMixin):
    """
    SQL调试中间件（仅在开发环境使用）
    打印每个SQL查询的详细信息
    """
    
    def process_response(self, request, response):
        """打印SQL查询详情"""
        if not hasattr(request, '_queries_before'):
            return response
        
        queries = connection.queries[request._queries_before:]
        
        if queries:
            print(f'\n[SQL Debug] {request.method} {request.path}')
            print(f'Total Queries: {len(queries)}\n')
            
            for i, query in enumerate(queries, 1):
                sql = query['sql']
                time_taken = query['time']
                
                # 高亮慢查询
                prefix = '⚠️  SLOW' if float(time_taken) > 0.1 else '   '
                
                print(f'{prefix} Query #{i} ({time_taken}s):')
                print(f'  {sql[:200]}...' if len(sql) > 200 else f'  {sql}')
                print()
        
        return response

