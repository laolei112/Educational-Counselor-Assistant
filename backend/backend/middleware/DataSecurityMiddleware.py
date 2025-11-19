"""
数据安全中间件
负责API响应数据的加密，实现"双模响应"
"""

from django.http import JsonResponse, HttpResponse
from utils.data_encryptor import DataEncryptor
from common.logger import loginfo, logerror
import json

class DataSecurityMiddleware:
    """
    数据安全中间件
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
        
        # 1. 全局开关检查
        if not self.ENABLE_ENCRYPTION:
            return response
            
        # 2. 检查是否为 JSON 响应
        content_type = response.get('Content-Type', '')
        if 'application/json' not in content_type:
            return response
            
        # 3. 检查路径
        if not any(request.path.startswith(p) for p in self.ENCRYPT_PATHS):
            return response
            
        # 4. SEO白名单检查
        is_seo = getattr(request, 'is_verified_seo_bot', False)
        if is_seo:
            loginfo(f"SEO Bot访问，跳过加密: {request.path}")
            return response
            
        # 5. 加密数据
        try:
            if hasattr(response, 'render') and callable(response.render):
                 response.render()
                 
            original_content = response.content.decode('utf-8')
            json_data = json.loads(original_content)
            
            # 检查是否有 data 字段
            if isinstance(json_data, dict) and 'data' in json_data:
                if json_data['data'] is not None:
                    # 执行加密
                    encrypted_result = DataEncryptor.encrypt_data(json_data['data'])
                    
                    # 检查加密结果
                    if not isinstance(encrypted_result, dict) or not encrypted_result.get('encrypted'):
                        logerror(f"加密失败，返回了原始数据: {request.path}")
                        return response

                    json_data['data'] = encrypted_result
                    
                    # 重建响应
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
                            
                    # 添加调试头 (生产环境可移除)
                    new_response['X-Encryption-Status'] = 'Encrypted'
                    return new_response
            else:
                # 响应格式不符合预期（没有data字段），不加密
                pass
                    
        except Exception as e:
            logerror(f"数据加密异常: {str(e)} Path: {request.path}")
            # 在响应头中添加错误信息以便调试
            response['X-Encryption-Error'] = str(e)[:100]
            
        return response
