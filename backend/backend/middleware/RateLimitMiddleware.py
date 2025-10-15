"""
频率限制中间件
用于防止恶意爬虫和DDoS攻击
"""

from django.http import JsonResponse
from utils.crypto_utils import rate_limiter
from common.logger import loginfo


class RateLimitMiddleware:
    """
    频率限制中间件
    
    限制单个客户端在指定时间窗口内的请求次数
    """
    
    # 白名单路径（不受频率限制）
    WHITELIST_PATHS = [
        '/nginx-health',
        '/admin/',
    ]
    
    # 是否启用频率限制
    ENABLE_RATE_LIMIT = True  # 设置为False可临时禁用频率限制
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 检查是否启用频率限制
        if not self.ENABLE_RATE_LIMIT:
            return self.get_response(request)
        
        # 检查路径是否在白名单中
        path = request.path
        for whitelist_path in self.WHITELIST_PATHS:
            if path.startswith(whitelist_path):
                return self.get_response(request)
        
        # 获取客户端标识
        client_id = self._get_client_identifier(request)
        
        # 检查频率限制
        is_allowed, error_msg = rate_limiter.is_allowed(client_id)
        
        if not is_allowed:
            loginfo(f"频率限制触发: {error_msg}, Client: {client_id}, Path: {path}")
            
            # 返回429 Too Many Requests
            response = JsonResponse({
                'code': 429,
                'message': error_msg,
                'success': False,
                'data': None
            }, status=429)
            
            # 添加Rate Limit响应头
            response['X-RateLimit-Limit'] = str(rate_limiter.max_requests)
            response['X-RateLimit-Remaining'] = '0'
            response['Retry-After'] = str(rate_limiter.time_window)
            
            return response
        
        # 继续处理请求
        response = self.get_response(request)
        
        # 添加Rate Limit信息到响应头
        remaining = rate_limiter.get_remaining_requests(client_id)
        response['X-RateLimit-Limit'] = str(rate_limiter.max_requests)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Reset'] = str(rate_limiter.time_window)
        
        return response
    
    def _get_client_identifier(self, request):
        """
        获取客户端唯一标识
        
        优先级：Device-ID > IP
        """
        # 尝试从请求头获取设备ID
        device_id = (
            request.META.get('HTTP_X_DEVICE_ID') or
            request.META.get('HTTP_X_DEVICE_FINGERPRINT')
        )
        
        if device_id:
            return f"device:{device_id}"
        
        # 使用IP作为标识
        ip = self._get_client_ip(request)
        return f"ip:{ip}"
    
    def _get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip

