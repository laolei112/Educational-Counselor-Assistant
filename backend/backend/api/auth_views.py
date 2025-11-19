import secrets
import time
import json
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from common.logger import loginfo

@csrf_exempt
@require_http_methods(["GET"])
def request_dynamic_token(request):
    """
    获取动态反爬Token (替代中间件拦截)
    
    GET /api/auth/request-token
    """
    try:
        # 1. 获取客户端标识 (IP)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.META.get('REMOTE_ADDR', 'unknown')
            
        # 2. 生成Token
        token = secrets.token_hex(16)
        timestamp = int(time.time())
        
        # 3. 存入 Redis (有效期60秒)
        data = {
            'client_id': client_ip,
            'timestamp': timestamp
        }
        # 键名必须与 DynamicTokenMiddleware 中一致: "dt:{token}"
        cache.set(f"dt:{token}", json.dumps(data), 60)
        
        # 4. 返回
        return JsonResponse({
            'code': 200,
            'success': True,
            'message': 'success',
            'data': {
                'token': token,
                'expires_in': 60
            }
        })
        
    except Exception as e:
        loginfo(f"动态Token生成失败: {str(e)}")
        return JsonResponse({
            'code': 500,
            'success': False,
            'message': '系统错误'
        }, status=500)

# ----------------------------------------------------------
# 以下函数仅为兼容性保留 (如果有其他地方引用)，但不再包含JWT逻辑
# ----------------------------------------------------------

@csrf_exempt
def get_token(request):
    return JsonResponse({'code': 410, 'message': 'JWT认证已废弃'}, status=410)

@csrf_exempt
def refresh_token(request):
    return JsonResponse({'code': 410, 'message': 'JWT认证已废弃'}, status=410)

@csrf_exempt
def revoke_token(request):
    return JsonResponse({'code': 410, 'message': 'JWT认证已废弃'}, status=410)

@csrf_exempt
def token_info(request):
    return JsonResponse({'code': 410, 'message': 'JWT认证已废弃'}, status=410)
