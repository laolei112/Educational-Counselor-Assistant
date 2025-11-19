"""
数据安全中间件
负责API响应数据的加密，实现"双模响应"
"""

from django.http import JsonResponse, HttpResponse
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
            
        # 1. 检查是否为 JSON 响应
        # DRF 返回的响应通常是 HttpResponse，但 Content-Type 是 application/json
        content_type = response.get('Content-Type', '')
        if 'application/json' not in content_type:
            return response
            
        # 2. 检查路径
        if not any(request.path.startswith(p) for p in self.ENCRYPT_PATHS):
            return response
            
        # 3. 关键判断：如果是验证过的SEO爬虫，返回明文！
        if getattr(request, 'is_verified_seo_bot', False):
            return response
            
        # 4. 加密数据
        try:
            # 获取原始数据
            # DRF 的 Response 如果还未渲染 (rendered_content)，可能需要先渲染
            # 但通常在中间件阶段 content 已经是 bytes
            if hasattr(response, 'render') and callable(response.render):
                 response.render()
                 
            original_content = response.content.decode('utf-8')
            json_data = json.loads(original_content)
            
            # 仅加密 data 字段
            if isinstance(json_data, dict) and 'data' in json_data:
                if json_data['data'] is not None:
                    encrypted_result = DataEncryptor.encrypt_data(json_data['data'])
                    json_data['data'] = encrypted_result
                    
                    # 重建响应 (使用 HttpResponse 确保兼容性)
                    new_content = json.dumps(json_data).encode('utf-8')
                    new_response = HttpResponse(
                        new_content, 
                        content_type='application/json',
                        status=response.status_code
                    )
                    
                    # 复制原响应头
                    for k, v in response.items():
                        if k not in ['Content-Length', 'Content-Type']:
                            new_response[k] = v
                            
                    return new_response
                    
        except Exception as e:
            # 打印错误但不中断流程，降级为明文
            print(f"Response encryption failed: {e}")
            pass
            
        return response
