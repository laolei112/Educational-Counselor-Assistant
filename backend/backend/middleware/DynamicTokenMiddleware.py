"""
动态Token验证中间件 + SEO智能识别
"""

from django.http import JsonResponse
from django.core.cache import cache
from common.logger import loginfo
import secrets
import hashlib
import time
import json
import re
import socket

class DynamicTokenMiddleware:
    """
    动态Token验证中间件
    
    功能：
    1. 验证客户端动态Token
    2. 识别并验证搜索引擎爬虫 (SEO Friendly)
    3. 标记请求来源（机器人 vs 普通用户）
    """
    
    # 搜索引擎User-Agent白名单
    SEO_USER_AGENTS = [
        r'Googlebot', r'Bingbot', r'Slurp', r'DuckDuckBot',
        r'Baiduspider', r'YandexBot', r'Sogou', r'Exabot',
        r'Bytespider'
    ]
    
    # ⚠️ 强烈建议开启：严格SEO验证（反向DNS查找）
    # 因为我们计划对普通用户加密数据，如果不开启此项，黑客只需修改UA即可获取明文
    ENABLE_STRICT_SEO_VERIFY = True

    PROTECTED_PATHS = [
        '/api/schools/',
        '/api/primary/',
        '/api/secondary/',
    ]
    
    WHITELIST_PATHS = [
        '/api/auth/request-token',
        '/api/auth/login',
        '/api/auth/register',
        '/api/sitemap.xml',
        '/nginx-health',
        '/admin/',
    ]
    
    TOKEN_EXPIRE_TIME = 60
    MAX_TOKENS_PER_CLIENT = 10
    
    ENABLE_DYNAMIC_TOKEN = False
    # 暂时关闭Token鉴权，但保留SEO识别逻辑
    SKIP_TOKEN_VERIFICATION = True
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.seo_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.SEO_USER_AGENTS
        ]
    
    def __call__(self, request):
        # 初始化标记
        request.is_verified_seo_bot = False
        
        if not self.ENABLE_DYNAMIC_TOKEN:
            return self.get_response(request)
        
        path = request.path

        # 1. 白名单路径检查 (优先放行，避免不必要的DNS反查，解决GSC抓取超时问题)
        if self._is_whitelisted(path):
            return self.get_response(request)
        
        # 2. 检查是否为搜索引擎
        if self._is_search_engine(request):
            request.is_verified_seo_bot = True
            # 搜索引擎直接放行，跳过Token验证
            return self.get_response(request)
        
        # 3. Token验证
        if self._needs_token_verification(path):
            if path == '/api/auth/request-token':
                return self._handle_token_request(request)
            
            # 如果配置了跳过验证，直接放行
            if self.SKIP_TOKEN_VERIFICATION:
                return self.get_response(request)
                
            is_valid, error_msg = self._verify_token(request)
            if not is_valid:
                return self._reject(request, error_msg)
        
        return self.get_response(request)

    def _is_search_engine(self, request):
        """检查并验证是否为搜索引擎"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if not user_agent:
            return False
            
        # 初步UA匹配
        is_seo_ua = any(p.search(user_agent) for p in self.seo_patterns)
        if not is_seo_ua:
            return False
            
        if not self.ENABLE_STRICT_SEO_VERIFY:
            return True
            
        # 严格验证：IP反查
        client_ip = self._get_client_ip(request)
        # 缓存验证结果避免频繁DNS查询
        cache_key = f"seo_verify:{client_ip}"
        is_verified = cache.get(cache_key)
        
        if is_verified is None:
            is_verified = self._verify_bot_ip(client_ip, user_agent)
            # 缓存24小时
            cache.set(cache_key, is_verified, 60 * 60 * 24)
            
        return is_verified

    def _verify_bot_ip(self, ip, user_agent):
        """DNS反向验证"""
        try:
            host = socket.gethostbyaddr(ip)[0].lower()
            
            # 验证域名后缀
            valid_domains = [
                '.googlebot.com', '.google.com',
                '.baidu.com', '.baidu.jp',
                '.search.msn.com', # Bing
                '.yandex.com',
                '.sogou.com'
            ]
            
            if not any(host.endswith(d) for d in valid_domains):
                return False
                
            # 正向验证：防止DNS劫持
            real_ip = socket.gethostbyname(host)
            return real_ip == ip
        except Exception:
            return False

    def _is_whitelisted(self, path):
        return any(path.startswith(p) for p in self.WHITELIST_PATHS)
    
    def _needs_token_verification(self, path):
        return any(path.startswith(p) for p in self.PROTECTED_PATHS)

    def _handle_token_request(self, request):
        """生成Token"""
        client_id = self._get_client_identifier(request)
        token = secrets.token_hex(16)
        timestamp = int(time.time())
        
        data = {
            'client_id': client_id,
            'timestamp': timestamp
        }
        
        cache.set(f"dt:{token}", json.dumps(data), self.TOKEN_EXPIRE_TIME)
        
        return JsonResponse({
            'code': 200,
            'success': True,
            'data': {
                'token': token,
                'expires_in': self.TOKEN_EXPIRE_TIME
            }
        })

    def _verify_token(self, request):
        token = request.META.get('HTTP_X_REQUEST_TOKEN')
        if not token:
            return False, '缺少Token'
            
        data_str = cache.get(f"dt:{token}")
        if not data_str:
            return False, 'Token无效或过期'
            
        data = json.loads(data_str)
        if data['client_id'] != self._get_client_identifier(request):
            return False, '客户端不匹配'
            
        return True, None

    def _reject(self, request, msg):
        return JsonResponse({
            'code': 403,
            'success': False,
            'message': msg
        }, status=403)

    def _get_client_identifier(self, request):
        return self._get_client_ip(request)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')

