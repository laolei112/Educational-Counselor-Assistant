# -*- coding: utf-8 -*-

"""
日志处理模块
"""

import os
import sys
import time
import logging
import logging.handlers

LOG_LEVEL       = "INFO"
LOG_TO_CONSOLE  = True      # 输出到控制台
LOG_TO_FILE     = True      # 输出到文件
LOG_BACKUP      = 31        # 保留X天日志

from .env import GPT_LOG_DIR

# ========================  目录和日志配置结束 ===================================

# ========================  SQL日志调试开始  ========================================

DEBUG_PRINT_SQL     = False  # 是否打印SQL
DEBUG_SLOW_SQL_TIME = 0      # 慢查询打印阈值，0代表不打印

if DEBUG_PRINT_SQL or DEBUG_SLOW_SQL_TIME > 0:
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement,
                            parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        if DEBUG_PRINT_SQL:
            logdebug("query: '{0}' params: '{1}'".format(statement, parameters))

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement,
                            parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        if DEBUG_SLOW_SQL_TIME > 0 and total >= DEBUG_SLOW_SQL_TIME:
            logerror("query '{0}' params '{1}' cost time: {2}".format(statement, parameters, total))

# ========================  SQL日志调试结束  ========================================


def _make_logname(logname):
    logname = os.path.basename(logname)
    logname = logname.split(".")[0]
    return logname


def _create_file_handle(level, logname):
    logname = _make_logname(logname)
    os.makedirs(GPT_LOG_DIR, exist_ok=True)
    filepath = os.path.join(GPT_LOG_DIR, f"{logname}.log")
    # 添加TimedRotatingFileHandler
    # 定义一个1天换一次log文件的handler
    # 保留LOG_BACKUP个旧log文件
    fh = logging.handlers.TimedRotatingFileHandler(filepath, when='midnight', interval=1, backupCount=LOG_BACKUP)
    fh.setLevel(level)
    date_format  = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', date_format)
    fh.setFormatter(formatter)
    return fh


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.ERROR):
        self.logger  = logger
        self.level   = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())
            print(line.rstrip())

    def flush(self):
        pass


def redirect_stderr() :
    stderr_logger = logging.getLogger('STDERR')
    sys.stderr = StreamToLogger(stderr_logger, logging.ERROR)


log_program  = None


def init_logger(program=None):
    if program:
        globals()["log_program"] = _make_logname(f"{program}_info")

    if not os.path.exists(GPT_LOG_DIR):
        print("create dir: {}".format(GPT_LOG_DIR))
        os.makedirs(GPT_LOG_DIR, exist_ok=True)

    log_error = f"{program}_err"
    if log_error in loggers:
        return

    logger = logging.getLogger(log_error)
    err_file = os.path.join(GPT_LOG_DIR, f"{log_error}.log")
    err_fd   = _create_file_handle(logging.ERROR, err_file)
    logging.root.addHandler(err_fd)
    loggers[log_error] = logger


def get_logger(logname):
    logname = _make_logname(logname)
    if logname in loggers:
        return loggers.get(logname)

    logger = logging.getLogger(logname)
    logger.propagate = False
    logger.setLevel(LOG_LEVEL)

    #file_handler = _create_file_handle(LOG_LEVEL, logname)
    #logger.addHandler(file_handler)

    if LOG_TO_CONSOLE:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level=LOG_LEVEL)
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', date_format)

        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    loggers[logname] = logger
    return logger


loggers = {}


def _prepare_logger():
    if log_program:
        logger = get_logger(log_program)
    else:
        logger = get_logger("aovtools")
    return logger


def _prepare_error_logger():
    logname = "error"
    if logname in loggers:
        logger = loggers.get(logname)
    else:
        logger = logging.getLogger(logname)
        logger.propagate = False
        logger.setLevel(logging.ERROR)
        err_file = os.path.join(AOVTOOLS_LOG_DIR, f"{logname}.log")
        err_fd   = _create_file_handle(logging.ERROR, err_file)
        logging.root.addHandler(err_fd)
        loggers[logname] = logger
    return logger


def loginfo(msg):
    logger = _prepare_logger()
    logger.info(msg)


def logerror(msg):
    logger = _prepare_logger()
    logger.error(msg)


def logdebug(msg):
    logger = _prepare_logger()
    logger.debug(msg)
