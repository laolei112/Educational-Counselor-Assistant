# JWT Token机制 - 最佳实践方案

## 🎯 方案概述

使用JWT Token替代每次签名请求，一次认证多次使用。

## 🏗️ 架构对比

### 当前方案（每次签名）
```
每个业务请求：
1. POST /api/generate-signature  ← 50ms
2. GET /api/schools/primary      ← 100ms
总耗时：150ms，2次请求
```

### JWT方案（Token复用）
```
初始化（仅一次）：
1. POST /api/auth/token          ← 50ms，获取Token

后续所有请求：
1. GET /api/schools/primary      ← 100ms（带Token）
总耗时：100ms，1次请求 ✅
```

**性能提升：50%延迟减少，请求数减半！**

## 📁 实现方案

### 1. 后端：Token生成和验证

**安装依赖：**
```bash
pip install PyJWT
```

**创建Token工具：**

```python
# backend/utils/jwt_utils.py
import jwt
import time
from datetime import datetime, timedelta

# JWT密钥（从环境变量读取）
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-jwt-secret-key')
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRE_HOURS = 24  # Token有效期24小时

def generate_token(client_id: str, metadata: dict = None) -> str:
    """
    生成JWT Token
    
    Args:
        client_id: 客户端唯一标识（可以是设备ID或IP）
        metadata: 额外的元数据
    
    Returns:
        JWT token字符串
    """
    payload = {
        'client_id': client_id,
        'iat': datetime.utcnow(),  # 签发时间
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),  # 过期时间
        'metadata': metadata or {}
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str) -> tuple:
    """
    验证JWT Token
    
    Returns:
        (is_valid, payload or error_message)
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, 'Token已过期'
    except jwt.InvalidTokenError:
        return False, 'Token无效'


class TokenManager:
    """Token管理器（可选，用于黑名单等高级功能）"""
    
    def __init__(self):
        self.blacklist = set()  # Token黑名单
    
    def revoke_token(self, token: str):
        """撤销Token"""
        self.blacklist.add(token)
    
    def is_revoked(self, token: str) -> bool:
        """检查Token是否被撤销"""
        return token in self.blacklist


# 全局实例
token_manager = TokenManager()
```

**Token生成API：**

```python
# backend/backend/api/auth_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from utils.jwt_utils import generate_token
from common.logger import loginfo
import json


def _get_client_identifier(request):
    """获取客户端标识"""
    # 优先使用设备指纹
    device_id = request.META.get('HTTP_X_DEVICE_ID')
    if device_id:
        return f"device:{device_id}"
    
    # 使用IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    
    return f"ip:{ip}"


def _verify_client_origin(request):
    """验证请求来源"""
    referer = request.META.get('HTTP_REFERER', '')
    origin = request.META.get('HTTP_ORIGIN', '')
    
    allowed_origins = [
        'https://betterschool.hk',
        'http://localhost:3000',
        'http://localhost:5173',
    ]
    
    for allowed in allowed_origins:
        if referer.startswith(allowed) or origin == allowed:
            return True
    
    return False


@csrf_exempt
@require_http_methods(["POST"])
def get_token(request):
    """
    获取访问Token
    POST /api/auth/token
    
    响应：
    {
        "code": 200,
        "data": {
            "token": "eyJ...",
            "expires_in": 86400
        }
    }
    """
    try:
        # 验证来源
        if not _verify_client_origin(request):
            return JsonResponse({
                'code': 403,
                'message': '请求来源验证失败',
                'success': False
            }, status=403)
        
        # 获取客户端标识
        client_id = _get_client_identifier(request)
        
        # 解析额外信息（可选）
        try:
            data = json.loads(request.body.decode('utf-8'))
            metadata = {
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'platform': data.get('platform', 'web')
            }
        except:
            metadata = {}
        
        # 生成Token
        token = generate_token(client_id, metadata)
        
        loginfo(f"Token生成成功, Client: {client_id}")
        
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
            'success': False
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def refresh_token(request):
    """
    刷新Token（可选）
    GET /api/auth/refresh
    Header: Authorization: Bearer <old_token>
    """
    try:
        # 获取旧Token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'code': 401,
                'message': '缺少Token',
                'success': False
            }, status=401)
        
        old_token = auth_header[7:]  # 移除 "Bearer "
        
        # 验证旧Token
        is_valid, payload = verify_token(old_token)
        if not is_valid:
            return JsonResponse({
                'code': 401,
                'message': payload,  # 错误信息
                'success': False
            }, status=401)
        
        # 生成新Token
        client_id = payload.get('client_id')
        metadata = payload.get('metadata', {})
        new_token = generate_token(client_id, metadata)
        
        return JsonResponse({
            'code': 200,
            'message': '成功',
            'success': True,
            'data': {
                'token': new_token,
                'expires_in': 86400
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'success': False
        }, status=500)
```

**Token验证中间件：**

```python
# backend/backend/middleware/TokenAuthMiddleware.py
from django.http import JsonResponse
from utils.jwt_utils import verify_token, token_manager
from common.logger import loginfo


class TokenAuthMiddleware:
    """
    Token认证中间件
    替代SignatureMiddleware，使用JWT Token验证
    """
    
    # 白名单路径
    WHITELIST_PATHS = [
        '/api/auth/',           # Token获取接口
        '/api/health',
        '/nginx-health',
        '/swagger/',
        '/admin/',
    ]
    
    # 搜索引擎爬虫（继续允许）
    SEARCH_ENGINE_USER_AGENTS = [
        'Googlebot', 'Bingbot', 'Slurp', 'DuckDuckBot',
        'Baiduspider', 'YandexBot', 'Sogou', 'Exabot',
    ]
    
    ENABLE_TOKEN_AUTH = True
    ALLOW_SEARCH_ENGINES = True
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if not self.ENABLE_TOKEN_AUTH:
            return self.get_response(request)
        
        # 白名单
        path = request.path
        for whitelist_path in self.WHITELIST_PATHS:
            if path.startswith(whitelist_path):
                return self.get_response(request)
        
        # 搜索引擎
        if self.ALLOW_SEARCH_ENGINES and self._is_search_engine(request):
            return self.get_response(request)
        
        # 验证Token
        is_valid, error_msg = self._validate_token(request)
        
        if not is_valid:
            loginfo(f"Token验证失败: {error_msg}, Path: {path}")
            return JsonResponse({
                'code': 401,
                'message': f'Token验证失败: {error_msg}',
                'success': False
            }, status=401)
        
        return self.get_response(request)
    
    def _validate_token(self, request):
        """验证Token"""
        # 从Header获取Token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return False, '缺少Token'
        
        token = auth_header[7:]  # 移除 "Bearer "
        
        # 检查是否被撤销
        if token_manager.is_revoked(token):
            return False, 'Token已被撤销'
        
        # 验证Token
        is_valid, payload = verify_token(token)
        if not is_valid:
            return False, payload  # payload是错误信息
        
        # 可以将payload存到request中供后续使用
        request.jwt_payload = payload
        
        return True, None
    
    def _is_search_engine(self, request):
        """检查是否为搜索引擎"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        for bot in self.SEARCH_ENGINE_USER_AGENTS:
            if bot.lower() in user_agent.lower():
                return True
        return False
```

### 2. 前端：Token管理

```typescript
// frontend/src/utils/token.ts

const TOKEN_STORAGE_KEY = 'api_token'
const TOKEN_EXPIRY_KEY = 'api_token_expiry'

export class TokenManager {
  private static instance: TokenManager
  private token: string | null = null
  private tokenExpiry: number = 0
  
  private constructor() {
    this.loadToken()
  }
  
  static getInstance(): TokenManager {
    if (!TokenManager.instance) {
      TokenManager.instance = new TokenManager()
    }
    return TokenManager.instance
  }
  
  /**
   * 从本地存储加载Token
   */
  private loadToken() {
    try {
      this.token = localStorage.getItem(TOKEN_STORAGE_KEY)
      const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY)
      this.tokenExpiry = expiry ? parseInt(expiry) : 0
    } catch (err) {
      console.error('加载Token失败:', err)
    }
  }
  
  /**
   * 保存Token到本地存储
   */
  private saveToken(token: string, expiresIn: number) {
    try {
      this.token = token
      this.tokenExpiry = Date.now() + (expiresIn * 1000)
      
      localStorage.setItem(TOKEN_STORAGE_KEY, token)
      localStorage.setItem(TOKEN_EXPIRY_KEY, String(this.tokenExpiry))
    } catch (err) {
      console.error('保存Token失败:', err)
    }
  }
  
  /**
   * 检查Token是否有效
   */
  isTokenValid(): boolean {
    if (!this.token) return false
    
    // 提前5分钟刷新Token
    return Date.now() < (this.tokenExpiry - 5 * 60 * 1000)
  }
  
  /**
   * 获取Token（自动处理刷新）
   */
  async getToken(): Promise<string> {
    // 如果Token有效，直接返回
    if (this.isTokenValid() && this.token) {
      return this.token
    }
    
    // 否则获取新Token
    return await this.fetchNewToken()
  }
  
  /**
   * 获取新Token
   */
  private async fetchNewToken(): Promise<string> {
    try {
      const response = await fetch('/api/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          platform: 'web'
        })
      })
      
      if (!response.ok) {
        throw new Error(`获取Token失败: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (!result.success || !result.data) {
        throw new Error(result.message || '获取Token失败')
      }
      
      // 保存Token
      this.saveToken(result.data.token, result.data.expires_in)
      
      return result.data.token
    } catch (error) {
      console.error('获取Token失败:', error)
      throw error
    }
  }
  
  /**
   * 清除Token
   */
  clearToken() {
    this.token = null
    this.tokenExpiry = 0
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    localStorage.removeItem(TOKEN_EXPIRY_KEY)
  }
}

// 导出单例
export const tokenManager = TokenManager.getInstance()
```

**更新request.ts：**

```typescript
// frontend/src/api/request.ts
import { tokenManager } from '../utils/token'
import { getDeviceFingerprint } from '../utils/crypto'

async function request<T = any>(
  path: string,
  config: RequestConfig = {},
  params?: Record<string, any>
): Promise<ApiResponse<T>> {
  const {
    method = 'GET',
    headers = {},
    body,
    timeout = API_CONFIG.TIMEOUT,
    skipAuth = false  // 新增：是否跳过认证
  } = config

  const url = buildUrl(path, method === 'GET' ? params : undefined)
  
  const requestHeaders: Record<string, string> = {
    ...API_CONFIG.HEADERS,
    ...headers
  }
  
  // 添加Token（替代签名）
  if (!skipAuth) {
    try {
      const token = await tokenManager.getToken()
      requestHeaders['Authorization'] = `Bearer ${token}`
      requestHeaders['X-Device-Id'] = getDeviceFingerprint()
    } catch (err) {
      console.error('获取Token失败:', err)
      throw new HttpError(0, '无法获取访问凭证，请检查网络连接')
    }
  }
  
  // ... 其余代码不变
}
```

### 3. 配置更新

**路由配置：**

```python
# backend/backend/api/__init__.py
from django.urls import path
from backend.api import auth_views

urls = [
    # ... 其他路由
    
    # Token认证
    path('auth/token', auth_views.get_token, name='get_token'),
    path('auth/refresh', auth_views.refresh_token, name='refresh_token'),
]
```

**中间件配置：**

```python
# backend/backend/basic_settings.py
MIDDLEWARE = [
    # ...
    # 使用Token认证替代签名验证
    "backend.middleware.RateLimitMiddleware.RateLimitMiddleware",
    "backend.middleware.AntiCrawlerMiddleware.AntiCrawlerMiddleware",
    "backend.middleware.TokenAuthMiddleware.TokenAuthMiddleware",  # ← 新的
    # "backend.middleware.SignatureMiddleware.SignatureMiddleware",  # ← 旧的，注释掉
    # ...
]
```

## 📊 性能对比

| 操作 | 签名方案 | Token方案 | 提升 |
|------|---------|----------|------|
| 首次请求 | 150ms (2次) | 150ms (1次Token + 1次业务) | 持平 |
| 后续请求 | 150ms (2次) | 100ms (1次) | **50ms↓ 33%** |
| 总请求数 | 2N | N+1 | **50%↓** |
| 服务器负载 | 2x | 1x | **50%↓** |

## 🎯 Token方案优势

1. ✅ **性能优异** - 后续请求快50%
2. ✅ **服务器友好** - 请求数减半
3. ✅ **用户体验好** - 延迟更低
4. ✅ **可扩展** - 可添加权限、用户信息等
5. ✅ **行业标准** - JWT是公认的最佳实践
6. ✅ **安全性高** - Token有过期时间

## ⚙️ Token配置

### 安全配置

```python
# Token有效期
TOKEN_EXPIRE_HOURS = 24  # 24小时

# 自动刷新阈值（前端）
REFRESH_BEFORE_MINUTES = 5  # 提前5分钟刷新

# Token黑名单（可选，用于撤销）
USE_TOKEN_BLACKLIST = True
```

### 前端Token刷新策略

```typescript
// 方案1：定时检查（推荐）
setInterval(() => {
  tokenManager.getToken() // 自动刷新过期Token
}, 5 * 60 * 1000) // 每5分钟检查

// 方案2：请求失败时刷新
if (response.status === 401) {
  tokenManager.clearToken()
  const newToken = await tokenManager.getToken()
  // 重试请求
}
```

## 🔄 迁移步骤

### 1. 安装依赖
```bash
pip install PyJWT
```

### 2. 创建新文件
- backend/utils/jwt_utils.py
- backend/backend/api/auth_views.py
- backend/backend/middleware/TokenAuthMiddleware.py
- frontend/src/utils/token.ts

### 3. 更新配置
- backend/backend/api/__init.py （添加路由）
- backend/backend/basic_settings.py （切换中间件）
- frontend/src/api/request.ts （使用Token）

### 4. 测试验证
```bash
# 获取Token
curl -X POST http://localhost:8080/api/auth/token

# 使用Token访问API
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/schools/primary
```

### 5. 平滑迁移
```python
# 可以同时支持两种方式，逐步迁移
class HybridAuthMiddleware:
    def __call__(self, request):
        # 优先检查Token
        if 'Authorization' in request.META:
            return self.validate_token(request)
        # 降级到签名验证
        else:
            return self.validate_signature(request)
```

## 📈 监控指标

```python
# 日志记录
loginfo(f"Token使用情况, 有效Token: {valid_tokens}, 过期: {expired}, 刷新: {refreshed}")
```

## 🎉 总结

**JWT Token方案 = 业界最佳实践**

- ⚡ 性能提升50%
- 📦 请求数减半
- 🔒 安全性不降低
- 📊 行业标准方案
- 🚀 易于扩展

---

*推荐立即迁移到Token方案！*

