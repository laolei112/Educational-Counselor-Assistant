"""
Token认证中间件
使用JWT Token进行请求认证，替代签名验证
"""

from django.http import JsonResponse
from utils.jwt_utils import verify_token, token_manager
from common.logger import loginfo


class TokenAuthMiddleware:
    """
    Token认证中间件
    
    验证请求头中的JWT Token，确保请求来自已认证的客户端
    """
    
    # 白名单路径（不需要Token认证）
    WHITELIST_PATHS = [
        '/api/auth/',           # Token获取和刷新接口
        '/api/health',
        '/nginx-health',
        '/swagger/',
        '/admin/',
    ]
    
    # 搜索引擎爬虫白名单（允许无Token访问，支持SEO）
    SEARCH_ENGINE_USER_AGENTS = [
        'Googlebot',
        'Bingbot',
        'Slurp',  # Yahoo
        'DuckDuckBot',
        'Baiduspider',
        'YandexBot',
        'Sogou',
        'Exabot',
    ]
    
    # 是否启用Token认证
    ENABLE_TOKEN_AUTH = True  # 设置为False可临时禁用
    
    # 是否允许搜索引擎爬虫无Token访问
    ALLOW_SEARCH_ENGINES = True  # 设置为False将拦截所有搜索引擎
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 检查是否启用Token认证
        if not self.ENABLE_TOKEN_AUTH:
            return self.get_response(request)
        
        # 检查路径是否在白名单中
        path = request.path
        for whitelist_path in self.WHITELIST_PATHS:
            if path.startswith(whitelist_path):
                return self.get_response(request)
        
        # 检查是否为搜索引擎爬虫（允许无Token访问以支持SEO）
        if self.ALLOW_SEARCH_ENGINES and self._is_search_engine(request):
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
            loginfo(f"搜索引擎访问（已允许）: {user_agent}, Path: {path}, IP: {self._get_client_ip(request)}")
            return self.get_response(request)
        
        # 验证Token
        is_valid, error_msg = self._validate_token(request)
        
        if not is_valid:
            loginfo(f"Token验证失败: {error_msg}, Path: {path}, IP: {self._get_client_ip(request)}")
            return JsonResponse({
                'code': 401,
                'message': f'Token验证失败: {error_msg}',
                'success': False,
                'data': None
            }, status=401)
        
        # 继续处理请求
        response = self.get_response(request)
        return response
    
    def _validate_token(self, request):
        """
        验证Token
        
        Returns:
            (is_valid, error_message)
        """
        # 从Header获取Token
        # 支持两种格式：
        # 1. Authorization: Bearer <token>
        # 2. X-Access-Token: <token>
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        x_token_header = request.META.get('HTTP_X_ACCESS_TOKEN', '')
        
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # 移除 "Bearer "
        elif x_token_header:
            token = x_token_header
        
        if not token:
            return False, '缺少Token'
        
        # 检查Token是否被撤销
        if token_manager.is_revoked(token):
            return False, 'Token已被撤销'
        
        # 验证Token
        is_valid, payload = verify_token(token)
        if not is_valid:
            return False, payload  # payload包含错误信息
        
        # 将payload存到request中供后续使用
        request.jwt_payload = payload
        request.jwt_client_id = payload.get('client_id')
        
        return True, None
    
    def _is_search_engine(self, request):
        """
        检查是否为搜索引擎爬虫
        
        Returns:
            bool: True表示是搜索引擎爬虫
        """
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 检查User-Agent是否包含搜索引擎标识
        for bot in self.SEARCH_ENGINE_USER_AGENTS:
            if bot.lower() in user_agent.lower():
                return True
        
        return False
    
    def _get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip

