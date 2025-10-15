from django.urls import include, re_path, path
from backend.api.schools import urls as schools_urls
from backend.api import signature_views


urls = [
    re_path(r"^schools/", include(schools_urls)),
    # 签名生成API（用于前端请求签名）
    path('generate-signature', signature_views.generate_signature, name='generate_signature'),
    path('signature/health', signature_views.signature_health, name='signature_health'),
]
