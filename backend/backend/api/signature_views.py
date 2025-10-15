"""
签名生成API
为可信前端客户端生成请求签名
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from utils.crypto_utils import signature_validator
from common.logger import loginfo
import json
import time
import secrets


def _get_client_ip(request):
    """获取客户端IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


def _verify_client_origin(request):
    """验证客户端来源（简单的反CSRF保护）"""
    # 检查Referer或Origin
    referer = request.META.get('HTTP_REFERER', '')
    origin = request.META.get('HTTP_ORIGIN', '')
    
    # 允许的来源（根据实际情况配置）
    allowed_origins = [
        'https://betterschool.hk',
        'http://localhost:3000',
        'http://localhost:5173',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
    ]
    
    # 检查来源
    for allowed in allowed_origins:
        if referer.startswith(allowed) or origin == allowed:
            return True
    
    return False


@csrf_exempt
@require_http_methods(["POST"])
def generate_signature(request):
    """
    生成请求签名
    POST /api/generate-signature
    
    请求体：
    {
        "params": {"page": 1, "type": "primary"},  // 查询参数（可选）
        "body": "{...}",  // 请求体（可选）
        "method": "GET"   // 请求方法
    }
    
    响应：
    {
        "code": 200,
        "data": {
            "timestamp": 1697366400,
            "nonce": "abc123...",
            "apiKey": "web-client-v1",
            "signature": "sha256hash..."
        }
    }
    """
    try:
        # 验证客户端来源（防止其他站点调用）
        if not _verify_client_origin(request):
            client_ip = _get_client_ip(request)
            loginfo(f"签名生成请求被拒绝（来源验证失败）, IP: {client_ip}")
            return JsonResponse({
                'code': 403,
                'message': '请求来源验证失败',
                'success': False,
                'data': None
            }, status=403)
        
        # 解析请求数据
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({
                'code': 400,
                'message': '无效的JSON格式',
                'success': False,
                'data': None
            }, status=400)
        
        params = data.get('params', {})
        body = data.get('body')
        method = data.get('method', 'GET')
        
        # 生成时间戳和nonce
        timestamp = int(time.time())
        nonce = secrets.token_urlsafe(16)
        api_key = 'web-client-v1'
        
        # 使用签名验证器生成签名
        # 注意：我们直接调用内部方法，因为验证器的公开方法是用于验证的
        signature = signature_validator._generate_signature(
            timestamp=timestamp,
            nonce=nonce,
            api_key=api_key,
            params=params if method == 'GET' else None,
            body=body if method != 'GET' else None
        )
        
        return JsonResponse({
            'code': 200,
            'message': '成功',
            'success': True,
            'data': {
                'timestamp': timestamp,
                'nonce': nonce,
                'apiKey': api_key,
                'signature': signature
            }
        })
        
    except Exception as e:
        loginfo(f"生成签名失败: {str(e)}")
        return JsonResponse({
            'code': 500,
            'message': f'生成签名失败: {str(e)}',
            'success': False,
            'data': None
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def signature_health(request):
    """
    健康检查
    GET /api/signature/health
    """
    return JsonResponse({
        'code': 200,
        'message': '签名服务正常',
        'success': True,
        'data': {
            'service': 'signature-generator',
            'status': 'healthy'
        }
    })

