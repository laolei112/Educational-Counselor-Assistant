# -*- coding: utf-8 -*-

"""
time_utils.py
时间相关的函数
"""

import re
import time

from typing import Union
from typing import Tuple
from datetime import datetime
from datetime import timedelta


def print_time_cost(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kws):
        start = time.time()
        ret = func(*args, **kws)
        end = time.time()
        costs = round(end-start, 2)
        if costs >= 1:
            args_str = str(args)[:128]
            print(f"[{func.__name__}][{args_str}] costs: {costs}")
        return ret
    return wrapper


def time_str_to_seconds(time_str: str) -> Union[int, float]:
    """
    把用 : 符号组成的时间长度转换为秒，比如 1:0:0 等于 3600 秒。输入格式应该为：hour:minute:second.fract_part
    """

    pattern = re.compile(r'[:]')
    parts = re.split(pattern, time_str)
    if len(parts) != 3:
        raise ValueError("unexpected time_str format, should be 'hour:minute:second.fract_part'")

    hour = int(parts[0])
    minute = int(parts[1])
    second = float(parts[2])
    seconds = hour * 3600 + minute * 60 + second

    return seconds


def seconds_to_time_str(seconds):
    if seconds <= 0:
        return ""
    # hours
    hours = seconds // 3600
    # remaining seconds
    seconds = seconds - (hours * 3600)
    # minutes
    minutes = seconds // 60
    # remaining seconds
    seconds = seconds - (minutes * 60)
    # total time
    time_str = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
    return time_str


def get_utc8_datetime() -> datetime:
    """
    强制返回 utc8。
    为什么不用 datetime.now()? datetime.now() 受操作系统时区的影响。
    """
    utc_now = datetime.utcnow()
    delta = timedelta(hours=8)
    return utc_now + delta


def get_date_time_str() -> Tuple[str, str]:
    """
    返回当前日期和时间的字符串，
    """
    utc8 = get_utc8_datetime()
    date_str = utc8.strftime("%Y%m%d")
    time_str = utc8.strftime("%H%M%S")
    return date_str, time_str


def get_current_5_minute(recorded_at):
    """
    获取 recorded_at 的前一个5分钟
    """
    recorded_at = recorded_at.replace(second=0, microsecond=0)
    mod = recorded_at.minute % 5
    if mod == 0:
        return recorded_at
    else:
        recorded_at = recorded_at - timedelta(minutes=mod)
        return recorded_at


def timestamp_to_str(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


def datetime_to_str(dt):
    if isinstance(dt, str):
        return dt
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def str_to_datetime(dt):
    if isinstance(dt, datetime):
        return dt
    return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":
    print(seconds_to_time_str(110844))
