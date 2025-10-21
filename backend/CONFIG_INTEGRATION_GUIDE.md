# 配置集成说明

## 📋 配置文件结构

Redis和数据库配置已更新为从配置文件读取，而不是硬编码。

### 配置文件路径

- **开发环境**: `config/conf/dev/backend/settings.json`
- **生产环境**: `config/conf/prd/backend/settings.json`

### 配置文件格式

```json
{
    "mysql": {
        "user": "root",
        "password": "your_password",
        "host": "mysql_host",
        "port": 3306,
        "db": "database_name",
        "charset": "utf8mb4",
        "timezone": "asia/shanghai",
        "init_command": ""
    },
    "redis": {
        "host": "redis_host",
        "port": 6380,
        "db": 0,
        "password": "redis_password"
    }
}
```

## 🔧 环境切换

通过环境变量`EDU_ENV`控制使用哪个配置文件：

```bash
# 开发环境（默认）
export EDU_ENV=DEV

# 生产环境
export EDU_ENV=PRD
```

在Docker Compose中设置：

```yaml
services:
  backend:
    environment:
      - EDU_ENV=DEV  # 或 PRD
```

## 📁 更新的文件

### 1. backend/backend/cache_settings.py

**功能**: 从配置文件读取Redis配置

```python
# 读取配置文件
if EDU_ENV == "PRD":
    CONF_PATH = "config/conf/prd/backend/settings.json"
elif EDU_ENV == "DEV":
    CONF_PATH = "config/conf/dev/backend/settings.json"

# 读取Redis配置
redis_config = config.get('redis', {})
REDIS_HOST = redis_config.get('host', 'redis')
REDIS_PORT = redis_config.get('port', 6380)
REDIS_PASSWORD = redis_config.get('password', '')
REDIS_DB = redis_config.get('db', 0)
```

**缓存配置**:
- KEY_PREFIX: `edu`
- 默认超时: 300秒（5分钟）
- 压缩: ZLib
- 异常处理: 忽略缓存异常，不影响主业务

### 2. backend/backend/database_settings.py

**功能**: 从配置文件读取MySQL配置

```python
# 读取MySQL配置
mysql_config = config.get('mysql', {})
MYSQL_HOST = mysql_config.get('host', 'mysql')
MYSQL_PORT = mysql_config.get('port', 3306)
MYSQL_USER = mysql_config.get('user', 'root')
MYSQL_PASSWORD = mysql_config.get('password', '')
MYSQL_DB = mysql_config.get('db', 'dev_yundisoft')
```

**连接池配置**:
- CONN_MAX_AGE: 600秒
- connect_timeout: 10秒
- read_timeout: 30秒
- write_timeout: 30秒

## 🔄 配置加载流程

```
1. 读取环境变量 EDU_ENV
   ↓
2. 根据环境选择配置文件路径
   - DEV: config/conf/dev/backend/settings.json
   - PRD: config/conf/prd/backend/settings.json
   ↓
3. 加载JSON配置文件
   ↓
4. 解析Redis和MySQL配置
   ↓
5. 构建Django配置对象
   ↓
6. 应用到应用程序
```

## ⚙️ 在settings.py中使用

由于`backend/backend/settings.py`已经有了完整的配置加载逻辑，优化后的配置会自动集成：

### 方式1：使用现有settings.py中的配置（推荐）

`settings.py`已经配置了CACHES：

```python
# backend/backend/settings.py (第73-83行)
RedisConfig = Config.redis
REDIS_HOST = RedisConfig["host"]
REDIS_PORT = RedisConfig["port"]
REDIS_DB = RedisConfig["db"]
REDIS_PWD = RedisConfig["password"]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "OPTIONS": {
            "PASSWORD": REDIS_PWD,
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "cache",
    }
}
```

**如果使用现有配置，需要修改KEY_PREFIX为'edu'以匹配缓存工具类**：

```python
# 修改settings.py中的KEY_PREFIX
"KEY_PREFIX": "edu",  # 改为edu以匹配CacheManager
```

### 方式2：使用优化后的cache_settings.py

在`settings.py`中导入并覆盖：

```python
# 在backend/backend/settings.py末尾添加
from .cache_settings import CACHES  # 导入优化后的CACHES配置

# 如果需要连接池配置
from .database_settings import DATABASE_POOL_CONFIG
DATABASES['default'].update(DATABASE_POOL_CONFIG)
```

## 🚀 部署步骤

### 1. 确认配置文件正确

**开发环境**:
```bash
cat config/conf/dev/backend/settings.json
```

**生产环境**:
```bash
cat config/conf/prd/backend/settings.json
```

### 2. 设置环境变量

在`docker-compose.yml`中：

```yaml
services:
  backend:
    environment:
      - EDU_ENV=DEV  # 开发环境
      # - EDU_ENV=PRD  # 生产环境使用这行
```

或在服务器上导出：

```bash
export EDU_ENV=PRD
```

### 3. 验证配置加载

```bash
# 启动Django shell
python manage.py shell

# 测试Redis连接
>>> from django.core.cache import cache
>>> cache.set('test_key', 'test_value', 60)
>>> print(cache.get('test_key'))
test_value

# 查看配置
>>> from django.conf import settings
>>> print(settings.CACHES['default']['LOCATION'])
redis://redis_host:6380/0
```

### 4. 测试缓存功能

```bash
# 使用缓存工具类
python manage.py shell

>>> from backend.utils.cache import CacheManager
>>> 
>>> # 设置缓存
>>> CacheManager.set('test', 'value', 60)
>>> 
>>> # 获取缓存
>>> print(CacheManager.get('test'))
value
>>> 
>>> # 生成缓存key
>>> key = CacheManager.generate_cache_key('prefix:', param1='value1')
>>> print(key)
prefix:xxxxx
```

## 🔍 故障排查

### 问题1: 配置文件找不到

**错误信息**: `FileNotFoundError: config/conf/dev/backend/settings.json`

**解决方案**:
```bash
# 确认当前工作目录
pwd

# 确认配置文件存在
ls -la config/conf/dev/backend/settings.json
ls -la config/conf/prd/backend/settings.json

# 检查环境变量
echo $EDU_ENV
```

### 问题2: Redis连接失败

**错误信息**: `redis.exceptions.ConnectionError`

**排查步骤**:
```bash
# 1. 检查配置文件中的Redis配置
cat config/conf/dev/backend/settings.json | grep -A 5 redis

# 2. 测试Redis连接
docker exec -it edu_redis redis-cli -p 6380 -a password PING

# 3. 检查Redis日志
docker logs edu_redis
```

### 问题3: MySQL连接失败

**错误信息**: `django.db.utils.OperationalError`

**排查步骤**:
```bash
# 1. 检查配置文件中的MySQL配置
cat config/conf/dev/backend/settings.json | grep -A 7 mysql

# 2. 测试MySQL连接
docker exec -it edu_mysql mysql -u root -p -e "SELECT 1"

# 3. 检查MySQL日志
docker logs edu_mysql
```

## 📊 配置对比

### 开发环境 vs 生产环境

| 配置项 | 开发环境 | 生产环境 |
|--------|---------|---------|
| MySQL Host | mysql (Docker容器) | 10.0.0.2 |
| MySQL Port | 3306 | 3306 |
| MySQL DB | dev_yundisoft | prd_yundisoft |
| Redis Host | redis (Docker容器) | 10.0.0.12 |
| Redis Port | 6380 | 6380 |
| Redis DB | 0 | 0 |

## ✅ 检查清单

部署前请确认：

- [ ] 配置文件存在且格式正确
- [ ] EDU_ENV环境变量已设置
- [ ] Redis配置正确（host、port、password）
- [ ] MySQL配置正确（host、port、user、password、db）
- [ ] Docker容器已启动（redis、mysql）
- [ ] settings.py中的KEY_PREFIX已修改为'edu'（如果使用现有配置）
- [ ] 缓存连接测试通过
- [ ] 数据库连接测试通过

## 🎯 最佳实践

1. **不要硬编码敏感信息**
   - 所有密码、host等信息都在配置文件中
   - 配置文件不要提交到git（已在.gitignore中）

2. **使用环境变量区分环境**
   - EDU_ENV=DEV 用于开发
   - EDU_ENV=PRD 用于生产

3. **配置验证**
   - 启动时会打印配置加载日志
   - 检查日志确认配置正确加载

4. **异常处理**
   - 配置加载失败会使用默认值
   - 不会导致应用无法启动

## 📚 相关文档

- `DEPLOYMENT_GUIDE_UPDATED.md` - 完整部署指南
- `PERFORMANCE_UPDATE_README.md` - 性能优化说明
- `backend/backend/settings.py` - Django主配置文件

---

**更新日期**: 2025-10-21  
**版本**: 2.1（添加配置文件集成）

