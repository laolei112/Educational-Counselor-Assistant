"""
反爬虫中间件
用于检测和阻止爬虫访问
"""

from django.http import JsonResponse
from common.logger import loginfo
import re


class AntiCrawlerMiddleware:
    """
    反爬虫中间件
    
    检测常见爬虫的User-Agent和行为模式
    """
    
    # 爬虫User-Agent黑名单（常见爬虫标识）
    CRAWLER_USER_AGENTS = [
        r'bot', r'crawl', r'spider', r'scrape', r'curl', r'wget',
        r'python-requests', r'scrapy', r'httpclient', r'okhttp',
        r'java/', r'go-http-client', r'axios', r'node-fetch',
        r'headless', r'phantom', r'selenium', r'puppeteer',
        r'mechanize', r'aiohttp', r'httpx', r'urllib'
    ]
    
    # 白名单User-Agent（允许的爬虫，如搜索引擎）
    WHITELIST_USER_AGENTS = [
        r'Googlebot', r'Bingbot', r'Slurp', r'DuckDuckBot',
        r'Baiduspider', r'YandexBot', r'Sogou', r'Exabot'
    ]
    
    # 可疑行为模式
    SUSPICIOUS_PATTERNS = {
        'no_user_agent': '缺少User-Agent',
        'too_simple': 'User-Agent过于简单',
        'no_accept_header': '缺少Accept请求头',
        'no_accept_language': '缺少Accept-Language',
    }
    
    # 白名单路径
    WHITELIST_PATHS = [
        '/nginx-health',
        '/admin/',
        '/swagger/',
    ]
    
    # 是否启用反爬虫检测
    ENABLE_ANTI_CRAWLER = True  # 设置为False可临时禁用
    
    # 检测模式：'strict'（严格）或 'moderate'（适中）
    DETECTION_MODE = 'moderate'
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 编译正则表达式以提高性能
        self.crawler_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.CRAWLER_USER_AGENTS
        ]
        self.whitelist_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.WHITELIST_USER_AGENTS
        ]
    
    def __call__(self, request):
        # 检查是否启用反爬虫
        if not self.ENABLE_ANTI_CRAWLER:
            return self.get_response(request)
        
        # 检查路径是否在白名单中
        path = request.path
        for whitelist_path in self.WHITELIST_PATHS:
            if path.startswith(whitelist_path):
                return self.get_response(request)
        
        # 检测爬虫
        is_crawler, reason = self._detect_crawler(request)
        
        if is_crawler:
            client_ip = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
            
            loginfo(
                f"检测到爬虫访问: {reason}, "
                f"IP: {client_ip}, "
                f"User-Agent: {user_agent}, "
                f"Path: {path}"
            )
            
            return JsonResponse({
                'code': 403,
                'message': '访问被拒绝',
                'success': False,
                'data': None
            }, status=403)
        
        # 继续处理请求
        return self.get_response(request)
    
    def _detect_crawler(self, request):
        """
        检测是否为爬虫
        
        Returns:
            (is_crawler, reason)
        """
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 1. 检查是否在白名单中（允许的爬虫）
        for pattern in self.whitelist_patterns:
            if pattern.search(user_agent):
                return False, None
        
        # 2. 检查User-Agent黑名单
        for pattern in self.crawler_patterns:
            if pattern.search(user_agent):
                return True, f"匹配爬虫特征: {pattern.pattern}"
        
        # 3. 检查可疑行为（仅在严格模式下）
        if self.DETECTION_MODE == 'strict':
            # 缺少User-Agent
            if not user_agent:
                return True, self.SUSPICIOUS_PATTERNS['no_user_agent']
            
            # User-Agent过于简单
            if len(user_agent) < 10:
                return True, self.SUSPICIOUS_PATTERNS['too_simple']
            
            # 缺少Accept请求头
            if not request.META.get('HTTP_ACCEPT'):
                return True, self.SUSPICIOUS_PATTERNS['no_accept_header']
            
            # 缺少Accept-Language（正常浏览器都有）
            if not request.META.get('HTTP_ACCEPT_LANGUAGE'):
                return True, self.SUSPICIOUS_PATTERNS['no_accept_language']
        
        # 4. 检查请求频率模式（如果需要更复杂的检测）
        # 这里可以添加更多的启发式检测规则
        
        return False, None
    
    def _get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip

