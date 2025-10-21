"""
数据库性能优化配置
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

# 读取MySQL配置
try:
    with open(CONF_PATH, encoding='UTF-8') as f:
        config = json.load(f)
    
    mysql_config = config.get('mysql', {})
    MYSQL_HOST = mysql_config.get('host', 'mysql')
    MYSQL_PORT = mysql_config.get('port', 3306)
    MYSQL_USER = mysql_config.get('user', 'root')
    MYSQL_PASSWORD = mysql_config.get('password', '')
    MYSQL_DB = mysql_config.get('db', 'dev_yundisoft')
    MYSQL_CHARSET = mysql_config.get('charset', 'utf8mb4')
    
    loginfo(f"Loaded MySQL config from {CONF_PATH}: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")
except Exception as e:
    loginfo(f"Failed to load config from {CONF_PATH}, using defaults: {e}")
    # 使用默认值
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'mysql')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'dev_yundisoft')
    MYSQL_CHARSET = 'utf8mb4'

# 数据库连接池配置
DATABASE_POOL_CONFIG = {
    'CONN_MAX_AGE': 600,  # 连接持久化时间（秒）
    'OPTIONS': {
        'connect_timeout': 10,
        'read_timeout': 30,
        'write_timeout': 30,
        'charset': MYSQL_CHARSET,
        'init_command': (
            "SET sql_mode='STRICT_TRANS_TABLES',"
            "SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED"  # 优化事务隔离级别
        ),
    }
}

# 数据库查询优化建议
"""
MySQL性能优化建议：

1. 添加复合索引
   CREATE INDEX idx_level_status ON tb_schools(level, application_status);
   CREATE INDEX idx_level_district ON tb_schools(level, district);
   CREATE INDEX idx_level_category ON tb_schools(level, category);
   
2. 添加全文索引（用于搜索优化）
   ALTER TABLE tb_schools ADD FULLTEXT INDEX idx_name_search (name);
   ALTER TABLE tb_schools ADD FULLTEXT INDEX idx_district_search (district);
   
3. 优化existing表结构
   - 确保JSON字段使用正确的类型
   - 考虑将热点字段从JSON中提取出来作为独立列
   
4. 查询优化
   - 使用EXPLAIN分析慢查询
   - 避免SELECT * ，只查询需要的字段
   - 使用合适的JOIN类型
   
5. 配置MySQL参数
   innodb_buffer_pool_size = 1G  # 根据服务器内存调整
   innodb_log_file_size = 256M
   max_connections = 200
   query_cache_size = 64M
   query_cache_type = 1
   
6. 定期维护
   OPTIMIZE TABLE tb_schools;  # 优化表
   ANALYZE TABLE tb_schools;   # 更新统计信息
"""

# 慢查询日志配置建议
SLOW_QUERY_LOG_CONFIG = """
# 在MySQL配置文件中添加：
[mysqld]
slow_query_log = 1
slow_query_log_file = /var/log/mysql/mysql-slow.log
long_query_time = 1  # 记录超过1秒的查询
log_queries_not_using_indexes = 1
"""

