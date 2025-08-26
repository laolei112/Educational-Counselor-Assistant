# 全局宏定义

import os

# 用户目录
HOMR_DIR = os.path.expandvars('$HOME')
GPT_ENV = os.environ.get("GPT_ENV", "DEV")
# 程序主目录
GPT_HOME_DIR = os.path.join(HOMR_DIR, "gpt/py-gpt/chatgpt-proxy")
# 运行期文件目录，如sock、pid文件
GPT_RUN_DIR   = os.path.join(GPT_HOME_DIR, "run")
# 日志目录
GPT_LOG_DIR   = os.path.join(GPT_RUN_DIR, "log")


_ConfPath = None
def load_confpath_by_env():
    from common.logger import loginfo

    global _ConfPath
    if _ConfPath:
        return _ConfPath

    env_name = GPT_ENV
    if env_name == "PRD":
        confpath = os.path.join(os.getcwd(), "config/config.json")
        loginfo(f"load confpath<{confpath}> from env<{env_name}>")
    elif env_name == "DEV":
        confpath = os.path.join(os.getcwd(), "config/config.json")
        loginfo(f"load confpath<{confpath}> from env<{env_name}>")
    elif env_name == "TEST":
        confpath = os.path.join(os.getcwd(), "config/config.json")
        loginfo(f"load confpath<{confpath}> from env<{env_name}>")

    _ConfPath = confpath
    return confpath