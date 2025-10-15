"""
签名验证中间件
用于验证API请求签名，防止数据被爬取
"""

from django.http import JsonResponse
from utils.crypto_utils import signature_validator
from common.logger import loginfo
import json


class SignatureMiddleware:
    """
    签名验证中间件
    
    验证请求头中的签名信息，确保请求来自可信客户端
    """
    
    # 白名单路径（不需要签名验证）
    WHITELIST_PATHS = [
        '/api/health',
        '/nginx-health',
        '/swagger/',
        '/admin/',
    ]
    
    # 是否启用签名验证
    ENABLE_SIGNATURE_CHECK = True  # 设置为False可临时禁用签名验证
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 检查是否启用签名验证
        if not self.ENABLE_SIGNATURE_CHECK:
            return self.get_response(request)
        
        # 检查路径是否在白名单中
        path = request.path
        for whitelist_path in self.WHITELIST_PATHS:
            if path.startswith(whitelist_path):
                return self.get_response(request)
        
        # 验证签名
        is_valid, error_msg = self._validate_request(request)
        
        if not is_valid:
            loginfo(f"签名验证失败: {error_msg}, Path: {path}, IP: {self._get_client_ip(request)}")
            return JsonResponse({
                'code': 403,
                'message': f'签名验证失败: {error_msg}',
                'success': False,
                'data': None
            }, status=403)
        
        # 继续处理请求
        response = self.get_response(request)
        return response
    
    def _validate_request(self, request):
        """
        验证请求签名
        
        Returns:
            (is_valid, error_message)
        """
        # 提取请求头
        headers = {
            key: value for key, value in request.META.items()
            if key.startswith('HTTP_')
        }
        
        # 转换请求头键名（Django会将HTTP_X_API_KEY转换为HTTP_X_API_KEY）
        normalized_headers = {}
        for key, value in headers.items():
            if key.startswith('HTTP_'):
                # HTTP_X_API_KEY -> X-Api-Key
                normalized_key = '-'.join(
                    word.capitalize() for word in key[5:].split('_')
                )
                normalized_headers[normalized_key] = value
        
        # 获取查询参数
        params = dict(request.GET.items()) if request.GET else None
        
        # 获取请求体
        body = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.content_type == 'application/json' and request.body:
                    body = request.body.decode('utf-8')
            except Exception as e:
                loginfo(f"读取请求体失败: {str(e)}")
        
        # 验证签名
        return signature_validator.validate_request(
            normalized_headers,
            params,
            body
        )
    
    def _get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

