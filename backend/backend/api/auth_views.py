"""
Token认证API视图
提供Token的获取、刷新等功能
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from utils.jwt_utils import generate_token, verify_token, token_manager
from common.logger import loginfo
import json


def _get_client_identifier(request):
    """
    获取客户端唯一标识
    
    优先级：设备ID > IP地址
    """
    # 优先使用设备指纹
    device_id = (
        request.META.get('HTTP_X_DEVICE_ID') or
        request.META.get('HTTP_X_DEVICE_FINGERPRINT')
    )
    
    if device_id:
        return f"device:{device_id}"
    
    # 使用IP地址
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    
    return f"ip:{ip}"


def _verify_client_origin(request):
    """
    验证请求来源
    防止其他站点调用
    """
    referer = request.META.get('HTTP_REFERER', '')
    origin = request.META.get('HTTP_ORIGIN', '')
    
    # 允许的来源列表
    allowed_origins = [
        'https://betterschool.hk',
        'https://www.betterschool.hk',
        'http://localhost:3000',
        'http://localhost:5173',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
    ]
    
    # 检查来源
    for allowed in allowed_origins:
        if referer.startswith(allowed) or origin == allowed:
            return True
    
    # 开发环境：如果没有referer/origin也允许（本地测试）
    if not referer and not origin:
        return True
    
    return False


@csrf_exempt
@require_http_methods(["POST"])
def get_token(request):
    """
    获取访问Token
    
    POST /api/auth/token
    
    请求体（可选）:
    {
        "platform": "web",  // 平台标识
        "version": "1.0.0"  // 客户端版本
    }
    
    响应:
    {
        "code": 200,
        "success": true,
        "data": {
            "token": "eyJ...",
            "expires_in": 86400,
            "token_type": "Bearer"
        }
    }
    """
    try:
        # 验证请求来源
        if not _verify_client_origin(request):
            client_ip = _get_client_identifier(request)
            loginfo(f"Token获取被拒绝（来源验证失败）, Client: {client_ip}")
            return JsonResponse({
                'code': 403,
                'message': '请求来源验证失败',
                'success': False,
                'data': None
            }, status=403)
        
        # 获取客户端标识
        client_id = _get_client_identifier(request)
        
        # 解析额外信息（可选）
        metadata = {}
        try:
            if request.body:
                data = json.loads(request.body.decode('utf-8'))
                metadata = {
                    'platform': data.get('platform', 'web'),
                    'version': data.get('version', 'unknown'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]  # 限制长度
                }
        except (json.JSONDecodeError, UnicodeDecodeError):
            # 如果解析失败，使用默认metadata
            pass
        
        # 生成Token
        token = generate_token(client_id, metadata)
        
        loginfo(f"Token生成成功, Client: {client_id}, Platform: {metadata.get('platform', 'unknown')}")
        
        return JsonResponse({
            'code': 200,
            'message': '成功',
            'success': True,
            'data': {
                'token': token,
                'expires_in': 86400,  # 24小时（秒）
                'token_type': 'Bearer'
            }
        })
        
    except Exception as e:
        loginfo(f"Token生成失败: {str(e)}")
        return JsonResponse({
            'code': 500,
            'message': f'Token生成失败: {str(e)}',
            'success': False,
            'data': None
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def refresh_token(request):
    """
    刷新Token
    
    POST /api/auth/refresh
    Header: Authorization: Bearer <old_token>
    
    响应:
    {
        "code": 200,
        "success": true,
        "data": {
            "token": "eyJ...",
            "expires_in": 86400
        }
    }
    """
    try:
        # 获取旧Token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'code': 401,
                'message': '缺少Token',
                'success': False,
                'data': None
            }, status=401)
        
        old_token = auth_header[7:]  # 移除 "Bearer "
        
        # 验证旧Token
        is_valid, payload = verify_token(old_token)
        if not is_valid:
            return JsonResponse({
                'code': 401,
                'message': payload,  # payload包含错误信息
                'success': False,
                'data': None
            }, status=401)
        
        # 检查是否被撤销
        if token_manager.is_revoked(old_token):
            return JsonResponse({
                'code': 401,
                'message': 'Token已被撤销',
                'success': False,
                'data': None
            }, status=401)
        
        # 生成新Token（保留原有的client_id和metadata）
        client_id = payload.get('client_id')
        metadata = payload.get('metadata', {})
        new_token = generate_token(client_id, metadata)
        
        loginfo(f"Token刷新成功, Client: {client_id}")
        
        return JsonResponse({
            'code': 200,
            'message': '成功',
            'success': True,
            'data': {
                'token': new_token,
                'expires_in': 86400,
                'token_type': 'Bearer'
            }
        })
        
    except Exception as e:
        loginfo(f"Token刷新失败: {str(e)}")
        return JsonResponse({
            'code': 500,
            'message': f'Token刷新失败: {str(e)}',
            'success': False,
            'data': None
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def revoke_token(request):
    """
    撤销Token
    
    POST /api/auth/revoke
    Header: Authorization: Bearer <token>
    
    响应:
    {
        "code": 200,
        "success": true,
        "message": "Token已撤销"
    }
    """
    try:
        # 获取Token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'code': 401,
                'message': '缺少Token',
                'success': False
            }, status=401)
        
        token = auth_header[7:]
        
        # 撤销Token
        token_manager.revoke_token(token)
        
        loginfo(f"Token已撤销")
        
        return JsonResponse({
            'code': 200,
            'message': 'Token已撤销',
            'success': True
        })
        
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'success': False
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def token_info(request):
    """
    获取Token信息
    
    GET /api/auth/token-info
    Header: Authorization: Bearer <token>
    
    响应:
    {
        "code": 200,
        "success": true,
        "data": {
            "client_id": "device:xxx",
            "issued_at": 1697366400,
            "expires_at": 1697452800,
            "metadata": {...}
        }
    }
    """
    try:
        # 获取Token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'code': 401,
                'message': '缺少Token',
                'success': False
            }, status=401)
        
        token = auth_header[7:]
        
        # 验证Token
        is_valid, payload = verify_token(token)
        if not is_valid:
            return JsonResponse({
                'code': 401,
                'message': payload,
                'success': False
            }, status=401)
        
        return JsonResponse({
            'code': 200,
            'success': True,
            'data': {
                'client_id': payload.get('client_id'),
                'issued_at': payload.get('iat'),
                'expires_at': payload.get('exp'),
                'metadata': payload.get('metadata', {})
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'success': False
        }, status=500)

