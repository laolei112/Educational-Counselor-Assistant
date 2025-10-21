# 🚀 性能优化部署指南

## 概述

本指南介绍如何部署和启用后端性能优化方案，可以将接口响应时间从1秒降低到100ms以内。

## 优化内容

### ✅ 已实现的优化

1. **Redis缓存层**
   - 列表数据缓存（5分钟）
   - 详情数据缓存（30分钟）
   - 统计数据缓存（1小时）

2. **数据库查询优化**
   - 简化搜索逻辑
   - 添加复合索引
   - 减少COUNT查询
   - 优化排序字段

3. **缓存失效策略**
   - 基于时间的自动过期
   - 支持手动清除缓存
   - 缓存key哈希优化

4. **性能监控**
   - 请求耗时监控
   - SQL查询统计
   - 慢查询日志

## 📦 依赖安装

### 1. 安装Python依赖

```bash
cd backend
pip install django-redis
```

### 2. 更新requirements.txt

在`backend/requirements.txt`中添加：
```
django-redis==5.4.0
redis==5.0.0
```

## ⚙️ 配置步骤

### 步骤1：更新Django settings

在`backend/backend/settings.py`或`backend/backend/basic_settings.py`中添加：

```python
# 导入缓存配置
from .cache_settings import CACHES

# 导入数据库优化配置
from .database_settings import DATABASE_POOL_CONFIG

# 更新DATABASES配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_yundisoft',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'mysql',
        'PORT': '3306',
        **DATABASE_POOL_CONFIG  # 添加连接池配置
    }
}

# 添加性能监控中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'backend.middleware.performance.PerformanceMonitorMiddleware',  # 添加这行
    'django.middleware.common.CommonMiddleware',
    # ... 其他中间件
]

# 日志配置（用于记录慢查询）
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/performance.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'performance': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
```

### 步骤2：执行数据库索引优化

在服务器上执行SQL脚本：

```bash
# 进入MySQL容器
docker exec -it edu_mysql mysql -u root -p

# 选择数据库
USE dev_yundisoft;

# 执行索引优化脚本
SOURCE /docker-entrypoint-initdb.d/optimize_indexes.sql;

# 或者直接从宿主机执行
docker exec -i edu_mysql mysql -u root -pfgdTv@4629uGdY dev_yundisoft < backend/common/db/optimize_indexes.sql
```

### 步骤3：验证Redis连接

```bash
# 测试Redis连接
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj

# 在Redis CLI中测试
PING
# 应该返回 PONG

# 查看缓存keys
KEYS edu:*

# 退出
exit
```

### 步骤4：重启后端服务

```bash
# 在项目根目录
docker-compose restart backend

# 查看日志
docker-compose logs -f backend
```

## 🧪 性能测试

### 测试1：基准测试

```bash
# 测试优化前
time curl "http://9.135.78.24/api/schools/?type=primary&page=1&pageSize=20"

# 测试优化后（第一次请求，未命中缓存）
time curl "http://9.135.78.24/api/schools/?type=primary&page=1&pageSize=20"

# 测试优化后（第二次请求，命中缓存）
time curl "http://9.135.78.24/api/schools/?type=primary&page=1&pageSize=20"
```

### 测试2：压力测试

使用Apache Bench进行压力测试：

```bash
# 安装ab工具
sudo apt-get install apache2-utils

# 并发测试（100个请求，10个并发）
ab -n 100 -c 10 "http://9.135.78.24/api/schools/?type=primary"

# 查看响应时间分布
# 关注 Time per request 和 Requests per second
```

### 测试3：监控缓存命中率

```bash
# 查看Redis统计信息
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj INFO stats

# 关注以下指标：
# - keyspace_hits: 缓存命中次数
# - keyspace_misses: 缓存未命中次数
# 命中率 = hits / (hits + misses)
```

## 📊 性能指标

### 优化前

- **首次请求**: 800-1200ms
- **后续请求**: 600-1000ms
- **数据库查询**: 5-10次/请求
- **并发能力**: 10-20 req/s

### 优化后（预期）

- **首次请求**: 100-300ms（未命中缓存）
- **缓存命中**: 10-50ms
- **数据库查询**: 0-2次/请求（缓存命中时为0）
- **并发能力**: 100-200 req/s

## 🔧 高级优化

### 1. 增加Redis内存

在`docker-compose.yml`中调整Redis配置：

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --port 6380 --requirepass HaWSD*9265tZYj --maxmemory 512mb --maxmemory-policy allkeys-lru
```

### 2. MySQL查询缓存

在MySQL配置中启用查询缓存（仅适用于MySQL 5.7及以下）：

```sql
SET GLOBAL query_cache_size = 67108864;  -- 64MB
SET GLOBAL query_cache_type = 1;
```

### 3. 使用连接池

安装`django-mysql`：

```bash
pip install django-mysql
```

更新数据库配置：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'CONN_MAX_AGE': 600,  # 连接持久化
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}
```

### 4. 启用HTTP缓存

在nginx配置中添加缓存：

```nginx
# 在nginx.conf中
location /api/schools/ {
    proxy_cache_valid 200 5m;  # 缓存成功响应5分钟
    proxy_cache_key "$request_uri";
    add_header X-Cache-Status $upstream_cache_status;
    
    proxy_pass http://backend;
}
```

## 🐛 故障排查

### 问题1：Redis连接失败

**症状**: 日志显示Redis连接错误

**解决方案**:
```bash
# 检查Redis是否运行
docker ps | grep redis

# 检查Redis日志
docker logs edu_redis

# 测试连接
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj PING
```

### 问题2：缓存不生效

**症状**: 每次请求都很慢

**解决方案**:
```python
# 在Django shell中测试缓存
python manage.py shell

from django.core.cache import cache
cache.set('test_key', 'test_value', 60)
print(cache.get('test_key'))  # 应该输出: test_value
```

### 问题3：内存不足

**症状**: Redis或MySQL内存溢出

**解决方案**:
```bash
# 清除所有缓存
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj FLUSHDB

# 或在Python中
from backend.utils.cache import CacheManager
CacheManager.clear_school_cache()
```

### 问题4：查询仍然很慢

**检查清单**:
1. 确认索引已创建: `SHOW INDEX FROM tb_schools;`
2. 查看慢查询日志: `docker logs edu_mysql | grep "Query"`
3. 使用EXPLAIN分析查询: `EXPLAIN SELECT * FROM tb_schools WHERE ...`
4. 检查表统计信息是否更新: `ANALYZE TABLE tb_schools;`

## 📈 监控和维护

### 日常监控

```bash
# 查看性能日志
tail -f backend/logs/performance.log

# 查看Redis内存使用
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj INFO memory

# 查看MySQL连接数
docker exec -it edu_mysql mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
```

### 定期维护

```bash
# 每周优化表（在低峰期执行）
docker exec -it edu_mysql mysql -u root -p -e "OPTIMIZE TABLE dev_yundisoft.tb_schools;"

# 每月清理过期缓存
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj FLUSHDB
```

## 📚 扩展阅读

- [Django缓存框架文档](https://docs.djangoproject.com/en/stable/topics/cache/)
- [MySQL性能优化指南](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- [Redis最佳实践](https://redis.io/docs/management/optimization/)

## 🎯 性能优化检查清单

- [ ] 安装django-redis
- [ ] 配置CACHES设置
- [ ] 创建数据库索引
- [ ] 更新URL配置使用优化视图
- [ ] 添加性能监控中间件
- [ ] 测试Redis连接
- [ ] 执行性能基准测试
- [ ] 监控缓存命中率
- [ ] 检查慢查询日志
- [ ] 优化MySQL配置

## ⚡ 快速启动

```bash
# 1. 安装依赖
pip install django-redis

# 2. 执行数据库优化
docker exec -i edu_mysql mysql -u root -pfgdTv@4629uGdY dev_yundisoft < backend/common/db/optimize_indexes.sql

# 3. 重启服务
docker-compose restart backend

# 4. 测试性能
time curl "http://9.135.78.24/api/schools/?type=primary"
```

完成这些步骤后，你的API性能应该会有显著提升！

