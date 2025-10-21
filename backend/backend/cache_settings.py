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
            'SOCKET_CONNECT_TIMEOUT': 5,  # 连接超时
            'SOCKET_TIMEOUT': 5,  # 读写超时
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',  # 压缩
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True
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

