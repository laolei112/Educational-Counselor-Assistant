"""
缓存配置
支持Redis和本地内存缓存
从config/conf/{env}/backend/settings.json中读取配置
"""
import os
import json
from common.logger import loginfo

# 获取环境变量
EDU_ENV = os.environ.get("EDU_ENV", "DEV")

# 加载配置文件
if EDU_ENV == "PRD":
    CONF_PATH = os.path.join(os.getcwd(), "config/conf/prd/backend/settings.json")
elif EDU_ENV == "DEV":
    CONF_PATH = os.path.join(os.getcwd(), "config/conf/dev/backend/settings.json")
else:
    CONF_PATH = os.path.join(os.getcwd(), "config/conf/dev/backend/settings.json")

# 读取Redis配置
try:
    with open(CONF_PATH, encoding='UTF-8') as f:
        config = json.load(f)
    
    redis_config = config.get('redis', {})
    REDIS_HOST = redis_config.get('host', 'redis')
    REDIS_PORT = redis_config.get('port', 6380)
    REDIS_PASSWORD = redis_config.get('password', '')
    REDIS_DB = redis_config.get('db', 0)
    
    loginfo(f"Loaded Redis config from {CONF_PATH}: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
except Exception as e:
    loginfo(f"Failed to load config from {CONF_PATH}, using defaults: {e}")
    # 使用默认值
    REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6380))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # 🔥 优化超时设置：降低超时时间，快速失败而不是长时间等待
            'SOCKET_CONNECT_TIMEOUT': 1,  # 连接超时1秒（快速失败）
            'SOCKET_TIMEOUT': 1,  # 读写超时1秒（避免长时间阻塞）
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',  # 压缩
            'CONNECTION_POOL_KWARGS': {
                # 🔥 优化连接池：增加连接数，减少等待时间
                'max_connections': 100,  # 增加最大连接数（从50增加到100）
                'retry_on_timeout': False,  # 🔥 关键：关闭超时重试，避免重复等待
                'socket_keepalive': True,  # 保持连接活跃，减少连接重建
                'socket_keepalive_options': {
                    'TCP_KEEPIDLE': 1,  # 1秒后开始发送keepalive
                    'TCP_KEEPINTVL': 3,  # keepalive间隔3秒
                    'TCP_KEEPCNT': 5,  # 最多5次keepalive失败后断开
                },
            },
            'IGNORE_EXCEPTIONS': True,  # 缓存异常时不影响主业务
        },
        'KEY_PREFIX': 'edu',  # 缓存key前缀
        'VERSION': 1,
        'TIMEOUT': 300,  # 默认超时时间（秒）
    },
    
    # 本地内存缓存（作为备用）
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# 会话缓存配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# 缓存中间件配置
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'middleware'

