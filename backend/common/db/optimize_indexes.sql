-- ========================================
-- 数据库性能优化 - 索引优化脚本
-- ========================================

-- 1. 添加复合索引（针对常见查询组合）
-- 用于 level + application_status 的组合查询
CREATE INDEX IF NOT EXISTS idx_level_status 
ON tb_schools(level, application_status);

-- 用于 level + district 的组合查询
CREATE INDEX IF NOT EXISTS idx_level_district 
ON tb_schools(level, district);

-- 用于 level + category 的组合查询
CREATE INDEX IF NOT EXISTS idx_level_category 
ON tb_schools(level, category);

-- 用于 level + district + application_status 的组合查询
CREATE INDEX IF NOT EXISTS idx_level_district_status 
ON tb_schools(level, district, application_status);

-- 2. 添加name字段的前缀索引（用于搜索优化）
-- 注意：MySQL的LIKE查询只能在前缀匹配时使用索引
CREATE INDEX IF NOT EXISTS idx_name_prefix 
ON tb_schools(name(20));

-- 3. 添加全文索引（用于全文搜索，可选）
-- 注意：全文索引只适用于 MyISAM 和 InnoDB (MySQL 5.6+)
-- 如果MySQL版本支持，取消下面的注释
-- ALTER TABLE tb_schools ADD FULLTEXT INDEX idx_fulltext_name (name);
-- ALTER TABLE tb_schools ADD FULLTEXT INDEX idx_fulltext_district (district);

-- 4. 分析现有索引使用情况
-- 查看表的索引信息
SHOW INDEX FROM tb_schools;

-- 5. 优化表（整理碎片，更新统计信息）
OPTIMIZE TABLE tb_schools;

-- 6. 更新表的统计信息
ANALYZE TABLE tb_schools;

-- 7. 查看表状态
SHOW TABLE STATUS LIKE 'tb_schools';

-- ========================================
-- 针对小学表的优化（如果使用单独的表）
-- ========================================
-- 如果有tb_primary_schools表，执行类似的优化

-- CREATE INDEX IF NOT EXISTS idx_primary_district_status 
-- ON tb_primary_schools(district, application_status);

-- CREATE INDEX IF NOT EXISTS idx_primary_category 
-- ON tb_primary_schools(category);

-- OPTIMIZE TABLE tb_primary_schools;
-- ANALYZE TABLE tb_primary_schools;

-- ========================================
-- 针对中学表的优化（如果使用单独的表）
-- ========================================
-- 如果有tb_secondary_schools表，执行类似的优化

-- CREATE INDEX IF NOT EXISTS idx_secondary_district_status 
-- ON tb_secondary_schools(district, application_status);

-- CREATE INDEX IF NOT EXISTS idx_secondary_category 
-- ON tb_secondary_schools(category);

-- OPTIMIZE TABLE tb_secondary_schools;
-- ANALYZE TABLE tb_secondary_schools;

-- ========================================
-- 性能监控查询
-- ========================================

-- 查看慢查询日志设置
SHOW VARIABLES LIKE 'slow_query%';
SHOW VARIABLES LIKE 'long_query_time';

-- 查看数据库连接数
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Max_used_connections';

-- 查看InnoDB缓冲池状态
SHOW STATUS LIKE 'Innodb_buffer_pool%';

-- 查看查询缓存命中率
SHOW STATUS LIKE 'Qcache%';

-- ========================================
-- 建议的MySQL配置优化
-- ========================================
/*
在MySQL配置文件 (my.cnf 或 my.ini) 中添加：

[mysqld]
# InnoDB缓冲池大小（建议设置为服务器内存的60-70%）
innodb_buffer_pool_size = 1G

# InnoDB日志文件大小
innodb_log_file_size = 256M

# 最大连接数
max_connections = 200

# 查询缓存大小
query_cache_size = 64M
query_cache_type = 1

# 慢查询日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/mysql-slow.log
long_query_time = 1

# 记录未使用索引的查询
log_queries_not_using_indexes = 1

# 临时表大小
tmp_table_size = 64M
max_heap_table_size = 64M

# 排序缓冲区大小
sort_buffer_size = 2M

# 连接缓冲区大小
join_buffer_size = 2M
*/

-- ========================================
-- 使用说明
-- ========================================
/*
1. 在MySQL客户端中执行此脚本：
   mysql -u root -p dev_yundisoft < optimize_indexes.sql

2. 或者在MySQL命令行中：
   source /path/to/optimize_indexes.sql

3. 执行后验证索引创建情况：
   SHOW INDEX FROM tb_schools;

4. 监控查询性能：
   - 使用EXPLAIN分析查询计划
   - 检查慢查询日志
   - 使用Django Debug Toolbar监控SQL查询
*/

