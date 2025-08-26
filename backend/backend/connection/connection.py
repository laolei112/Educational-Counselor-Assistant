"""
    连接初始化
"""
from contextlib import contextmanager
from django.conf import settings
from utils.redis_utils import init_redis_client




def get_redis_client():
    redis_cfg = {
        "db"       : settings.REDIS_DB,
        "host"     : settings.REDIS_HOST,
        "port"     : settings.REDIS_PORT,
        "password" : settings.REDIS_PWD,
    }
    redis_cli = init_redis_client(redis_cfg)
    return redis_cli
