# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import uuid
import redis


# 断线重连
def check_alive(func, *params, **kwargs):
    def redis_execute(obj, *params, **kwargs):
        for i in range(5):
            try:
                return func(obj, *params, **kwargs)
            except (redis.ConnectionError, redis.TimeoutError) as err:
                print("execute redis: %s %s error: '%s'"%(str(func.__name__), str(params), str(err)))
                time.sleep(1)
                continue
            except Exception as err:
                print("execute redis: %s %s error: '%s'"%(str(func.__name__), str(params), str(err)))
                return None
        print("break redis execute by failure max")
        sys.exit(2)
    return redis_execute


class RedisClient(redis.Redis):

    def __init__(self, **kwargs):
        super(RedisClient, self).__init__(**kwargs)

    @check_alive
    def execute_command(self, *args, **kwargs):
        return super(RedisClient, self).execute_command(*args, **kwargs)


g_Redis = None


def init_redis_client(redis_cfg) :
    global g_Redis
    if g_Redis is not None:
        return g_Redis

    # 创建数据库对象
    assert redis_cfg
    g_Redis = RedisClient(
        host     = redis_cfg.get('host'),
        port     = redis_cfg.get('port'),
        db       = int(redis_cfg.get('db', 0)),
        password = redis_cfg.get('password'),
        charset  = 'utf-8',
        socket_timeout = 30,
    )
    return g_Redis
