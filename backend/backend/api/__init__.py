from django.urls import include, re_path, path
from backend.api.schools import urls as schools_urls
from backend.api import signature_views, auth_views, scheduler_views


urls = [
    re_path(r"^schools/", include(schools_urls)),
    
    # Token认证API（推荐使用）
    path('auth/request-token', auth_views.request_dynamic_token, name='request_dynamic_token'),  # 新增：动态反爬Token
    path('auth/token', auth_views.get_token, name='get_token'),
    path('auth/refresh', auth_views.refresh_token, name='refresh_token'),
    path('auth/revoke', auth_views.revoke_token, name='revoke_token'),
    path('auth/token-info', auth_views.token_info, name='token_info'),
    
    # 签名生成API（旧方案，保留兼容性）
    path('generate-signature', signature_views.generate_signature, name='generate_signature'),
    path('signature/health', signature_views.signature_health, name='signature_health'),
    
    # 调度器管理API
    path('scheduler/status', scheduler_views.scheduler_status, name='scheduler_status'),
    path('scheduler/warmup', scheduler_views.trigger_warmup, name='trigger_warmup'),
    path('scheduler/clear-and-warmup', scheduler_views.clear_and_warmup, name='clear_and_warmup'),
]
