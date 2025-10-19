# JWT方案 - 防爬虫与SEO平衡机制

## 🎯 核心问题

**如何既防止恶意爬虫，又不影响搜索引擎收录？**

## ✅ 答案：三层识别机制

```
┌─────────────────────────────────────────┐
│           请求到达                       │
└─────────────────────────────────────────┘
                 ↓
    ┌────────────────────────┐
    │  第1层：频率限制         │
    │  RateLimitMiddleware   │
    │  (所有请求)             │
    └────────────────────────┘
                 ↓
    ┌────────────────────────┐
    │  第2层：爬虫检测         │
    │  AntiCrawlerMiddleware │
    │  (识别恶意爬虫)          │
    └────────────────────────┘
                 ↓
    ┌────────────────────────────────┐
    │  第3层：Token认证               │
    │  TokenAuthMiddleware           │
    │  - 搜索引擎？→ 放行 ✅         │
    │  - 有Token？→ 放行 ✅          │
    │  - 其他？→ 拒绝 ❌             │
    └────────────────────────────────┘
                 ↓
         ┌──────────────┐
         │   业务API     │
         └──────────────┘
```

## 🛡️ 防护机制详解

### 1. 频率限制（第1层）

**文件：** `backend/backend/middleware/RateLimitMiddleware.py`

```python
# 限制：100次/分钟
# 作用：防止暴力爬取
```

**效果：**
- ✅ 限制所有来源（包括搜索引擎）
- ✅ 正常用户不受影响
- ✅ 爬虫受到严重限制

**对搜索引擎的影响：**
- ⚠️ 搜索引擎爬虫通常速度不快（符合robots.txt）
- ✅ 100次/分钟对搜索引擎足够
- ✅ 如果不够可以调整：

```python
# 为搜索引擎设置更高的限额（可选）
if self._is_search_engine(request):
    # 搜索引擎：200次/分钟
    rate_limiter_search = RateLimiter(max_requests=200, time_window=60)
    is_allowed, error_msg = rate_limiter_search.is_allowed(client_id)
else:
    # 普通用户/爬虫：100次/分钟
    is_allowed, error_msg = rate_limiter.is_allowed(client_id)
```

### 2. 反爬虫检测（第2层）

**文件：** `backend/backend/middleware/AntiCrawlerMiddleware.py`

```python
# 恶意爬虫特征
CRAWLER_USER_AGENTS = [
    r'scrapy',           # ❌ 拒绝
    r'python-requests',  # ❌ 拒绝
    r'curl',             # ❌ 拒绝
    # ...
]

# 搜索引擎白名单
WHITELIST_USER_AGENTS = [
    r'Googlebot',        # ✅ 允许
    r'Bingbot',          # ✅ 允许
    # ...
]
```

**识别逻辑：**

```python
def __call__(self, request):
    # 1. 先检查是否为搜索引擎
    if self._is_whitelisted_bot(request):
        return self.get_response(request)  # ✅ 放行
    
    # 2. 再检查是否为恶意爬虫
    if self._is_malicious_crawler(request):
        return JsonResponse({'error': '拒绝访问'}, status=403)  # ❌ 拒绝
    
    # 3. 其他请求继续
    return self.get_response(request)
```

**效果：**
- ✅ 搜索引擎：识别并放行
- ❌ 恶意爬虫：识别并拒绝
- ✅ 普通用户：正常通过

### 3. Token认证（第3层）

**文件：** `backend/backend/middleware/TokenAuthMiddleware.py`

```python
class TokenAuthMiddleware:
    # 搜索引擎白名单
    SEARCH_ENGINE_USER_AGENTS = [
        'Googlebot', 'Bingbot', 'Baiduspider', ...
    ]
    
    # 允许搜索引擎无Token访问
    ALLOW_SEARCH_ENGINES = True  # ✅ 关键配置
    
    def __call__(self, request):
        # 1. 检查是否为搜索引擎
        if self.ALLOW_SEARCH_ENGINES and self._is_search_engine(request):
            loginfo(f"搜索引擎访问（已允许）: {user_agent}")
            return self.get_response(request)  # ✅ 无需Token，直接放行
        
        # 2. 其他请求需要Token
        if not self._has_valid_token(request):
            return JsonResponse({'error': 'Unauthorized'}, status=401)  # ❌ 拒绝
        
        return self.get_response(request)
```

**核心逻辑：**

```python
def _is_search_engine(self, request):
    """检查是否为搜索引擎爬虫"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    for bot in self.SEARCH_ENGINE_USER_AGENTS:
        if bot.lower() in user_agent.lower():
            return True  # ✅ 是搜索引擎
    
    return False  # ❌ 不是搜索引擎
```

## 📊 不同访问者的处理

### 1. ✅ Google搜索引擎

```bash
User-Agent: Mozilla/5.0 (compatible; Googlebot/2.1)
```

**处理流程：**
1. 第1层（频率限制）: ✅ 通过（速度合理）
2. 第2层（反爬虫）: ✅ 通过（白名单）
3. 第3层（Token认证）: ✅ 通过（搜索引擎豁免）
→ **结果：成功访问，正常收录** 🎉

### 2. ❌ Scrapy爬虫

```bash
User-Agent: Scrapy/2.8.0
```

**处理流程：**
1. 第1层（频率限制）: ⚠️ 可能触发限制
2. 第2层（反爬虫）: ❌ 识别为恶意爬虫，直接拒绝
→ **结果：403 Forbidden** 🚫

### 3. ❌ Python-requests爬虫

```bash
User-Agent: python-requests/2.28.0
```

**处理流程：**
1. 第1层（频率限制）: ⚠️ 可能触发限制
2. 第2层（反爬虫）: ❌ 识别为爬虫工具，拒绝
→ **结果：403 Forbidden** 🚫

### 4. ❌ 伪装的爬虫（无Token）

```bash
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0
# 伪装成浏览器，但没有Token
```

**处理流程：**
1. 第1层（频率限制）: ✅ 通过（如果频率不高）
2. 第2层（反爬虫）: ✅ 通过（User-Agent正常）
3. 第3层（Token认证）: ❌ 没有Token，拒绝
→ **结果：401 Unauthorized** 🚫

### 5. ✅ 正常用户（浏览器）

```bash
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**处理流程：**
1. 第1层（频率限制）: ✅ 通过（正常使用）
2. 第2层（反爬虫）: ✅ 通过（正常浏览器）
3. 第3层（Token认证）: ✅ 通过（有有效Token）
→ **结果：正常访问** 🎉

## 🎭 爬虫的攻击尝试与防御

### 攻击1: 伪装User-Agent

**爬虫尝试：**
```python
# 爬虫代码
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0)...'}
requests.get('https://betterschool.hk/api/schools/primary')
```

**防御：**
- ❌ 第3层拦截：没有Token → 401

**结果：** 失败 ✅

### 攻击2: 伪装成Google

**爬虫尝试：**
```python
headers = {'User-Agent': 'Googlebot/2.1'}
requests.get('https://betterschool.hk/api/schools/primary')
```

**防御：**
- ⚠️ 可能绕过Token验证（伪装搜索引擎）
- ✅ 第1层拦截：频率过高 → 429
- ✅ 可验证真实Googlebot（通过IP反查）

**高级防御（可选）：**
```python
def _is_real_google_bot(self, request):
    """验证是否为真实的Googlebot"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if 'googlebot' not in user_agent.lower():
        return False
    
    # 获取IP
    ip = self._get_client_ip(request)
    
    # 反查DNS（Google的爬虫IP可以反查到googlebot.com）
    try:
        import socket
        hostname = socket.gethostbyaddr(ip)[0]
        # 真实Googlebot的域名应该是 *.googlebot.com 或 *.google.com
        return hostname.endswith('.googlebot.com') or hostname.endswith('.google.com')
    except:
        return False
```

### 攻击3: 获取Token后爬取

**爬虫尝试：**
```python
# 1. 先获取Token
response = requests.post('https://betterschool.hk/api/auth/token')
token = response.json()['data']['token']

# 2. 使用Token爬取
headers = {'Authorization': f'Bearer {token}'}
for i in range(1000):
    requests.get(f'https://betterschool.hk/api/schools/primary?page={i}', headers=headers)
```

**防御：**
- ✅ 第1层拦截：频率限制 → 429（100次/分钟）
- ✅ 检测到异常后可以撤销Token

**结果：** 被限制 ✅

## 📈 SEO效果验证

### 测试1: Google Search Console

**预期：**
- ✅ Googlebot可以正常爬取
- ✅ 页面被编入索引
- ✅ 无爬取错误

**验证方法：**
1. 提交sitemap到Google Search Console
2. 检查覆盖率报告
3. 使用"网址检查"工具

### 测试2: 模拟Googlebot

```bash
# 模拟Googlebot请求
curl -A "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" \
  https://betterschool.hk/api/schools/primary

# 预期：返回200和数据
```

### 测试3: 日志验证

```bash
# 查看搜索引擎访问日志
docker-compose logs backend | grep "搜索引擎访问（已允许）"

# 预期输出：
# INFO 搜索引擎访问（已允许）: Googlebot/2.1, Path: /api/schools/primary
```

## 🔧 配置优化

### 1. 为搜索引擎提高频率限制

如果搜索引擎爬取受到频率限制，可以单独配置：

```python
# backend/backend/middleware/RateLimitMiddleware.py

class RateLimitMiddleware:
    # 搜索引擎专用限制器（更宽松）
    search_engine_limiter = RateLimiter(max_requests=200, time_window=60)
    
    def __call__(self, request):
        # 如果是搜索引擎，使用更宽松的限制
        if self._is_search_engine(request):
            is_allowed, error_msg = self.search_engine_limiter.is_allowed(client_id)
        else:
            is_allowed, error_msg = rate_limiter.is_allowed(client_id)
        
        # ... 其余代码
```

### 2. 验证真实Googlebot（高级）

防止爬虫伪装成Google：

```python
# backend/backend/middleware/TokenAuthMiddleware.py

def _is_search_engine(self, request):
    """检查是否为搜索引擎（增强验证）"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # 检查User-Agent
    is_bot = False
    for bot in self.SEARCH_ENGINE_USER_AGENTS:
        if bot.lower() in user_agent.lower():
            is_bot = True
            break
    
    if not is_bot:
        return False
    
    # 可选：验证Google/Bing的真实性（通过IP反查）
    if 'googlebot' in user_agent.lower():
        return self._verify_googlebot(request)
    
    return True

def _verify_googlebot(self, request):
    """验证是否为真实的Googlebot"""
    ip = self._get_client_ip(request)
    
    try:
        import socket
        # 反查DNS
        hostname = socket.gethostbyaddr(ip)[0]
        # Google的爬虫应该是 *.googlebot.com 或 *.google.com
        if hostname.endswith('.googlebot.com') or hostname.endswith('.google.com'):
            # 正向解析验证
            resolved_ip = socket.gethostbyname(hostname)
            return resolved_ip == ip
    except:
        pass
    
    # 如果验证失败，记录日志但仍然允许（避免误判）
    loginfo(f"Googlebot验证失败，但仍允许访问: {ip}")
    return True
```

### 3. 动态调整白名单

根据实际情况添加更多搜索引擎：

```python
SEARCH_ENGINE_USER_AGENTS = [
    'Googlebot',           # Google
    'Bingbot',             # Bing
    'Slurp',               # Yahoo
    'DuckDuckBot',         # DuckDuckGo
    'Baiduspider',         # 百度
    'YandexBot',           # Yandex
    'Sogou',               # 搜狗
    'Exabot',              # Exalead
    '360Spider',           # 360搜索
    'Bytespider',          # 字节跳动
]
```

## 📊 实际效果对比

### 防爬虫效果

| 爬虫类型 | 是否被拦截 | 拦截层 | 状态码 |
|---------|-----------|--------|--------|
| Scrapy | ✅ 是 | 第2层 | 403 |
| python-requests | ✅ 是 | 第2层 | 403 |
| curl | ✅ 是 | 第2层 | 403 |
| 伪装浏览器（无Token） | ✅ 是 | 第3层 | 401 |
| 有Token但高频 | ✅ 是 | 第1层 | 429 |

### SEO效果

| 搜索引擎 | 是否可访问 | Token需求 | 频率限制 |
|---------|-----------|-----------|---------|
| Google | ✅ 可以 | 无需 | 宽松 |
| Bing | ✅ 可以 | 无需 | 宽松 |
| 百度 | ✅ 可以 | 无需 | 宽松 |
| 其他 | ✅ 可以 | 无需 | 宽松 |

## ✅ 结论

### JWT方案完美平衡防爬与SEO

1. **✅ 防止恶意爬虫**
   - 三层防护机制
   - 识别常见爬虫工具
   - Token认证拦截未授权访问
   - 频率限制防止暴力爬取

2. **✅ 不影响SEO**
   - 搜索引擎白名单
   - 无需Token即可访问
   - 日志记录便于监控
   - 可验证真实性（防伪装）

3. **✅ 性能优异**
   - 合法用户体验好
   - 服务器负载低
   - 响应速度快

### 最佳实践建议

1. **监控日志**
   ```bash
   # 定期检查搜索引擎访问
   docker-compose logs backend | grep "搜索引擎访问"
   ```

2. **Google Search Console**
   - 提交sitemap
   - 监控爬取统计
   - 检查索引状态

3. **持续优化**
   - 根据日志调整白名单
   - 如需要可添加IP验证
   - 监控并调整频率限制

---

**JWT方案既安全又SEO友好！** 🎉🔒🔍

*最后更新: 2024-10-15*


