"""
数据安全中间件
负责API响应数据的加密，实现"双模响应"
"""

from django.http import JsonResponse
from utils.data_encryptor import DataEncryptor
import json

class DataSecurityMiddleware:
    """
    数据安全中间件
    
    逻辑：
    1. 检查 request.is_verified_seo_bot 标记（由DynamicTokenMiddleware设置）
    2. 如果是验证过的SEO爬虫 -> 返回明文（Pass）
    3. 如果是普通用户 -> 对 JsonResponse 的 content 进行 AES 加密
    """
    
    # 需要加密的路径前缀
    ENCRYPT_PATHS = [
        '/api/schools/',
        '/api/primary/',
        '/api/secondary/',
    ]
    
    ENABLE_ENCRYPTION = True

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if not self.ENABLE_ENCRYPTION:
            return response
            
        # 仅处理 JsonResponse
        if not isinstance(response, JsonResponse):
            return response
            
        # 检查路径
        if not any(request.path.startswith(p) for p in self.ENCRYPT_PATHS):
            return response
            
        # 关键判断：如果是验证过的SEO爬虫，返回明文！
        if getattr(request, 'is_verified_seo_bot', False):
            return response
            
        # 否则，加密数据
        try:
            # 获取原始数据
            # JsonResponse.content 是 bytes，需要解码后加载
            original_content = response.content.decode('utf-8')
            json_data = json.loads(original_content)
            
            # 仅加密 data 字段，保留外层结构（code, message等）
            # 这样前端容易判断请求状态
            if isinstance(json_data, dict) and 'data' in json_data:
                if json_data['data'] is not None:
                    encrypted_result = DataEncryptor.encrypt_data(json_data['data'])
                    json_data['data'] = encrypted_result
                    
                    # 重建响应
                    new_response = JsonResponse(json_data, status=response.status_code)
                    # 复制原响应头
                    for k, v in response.items():
                        new_response[k] = v
                    return new_response
                    
        except Exception as e:
            # 加密失败降级为明文，或记录错误
            print(f"Response encryption failed: {e}")
            
        return response

