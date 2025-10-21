-- ========================================
-- 小学和中学表性能优化 - 索引优化脚本
-- ========================================

-- ========================================
-- 小学表 (tb_primary_schools) 优化
-- ========================================

-- 1. 添加常用查询字段的索引
CREATE INDEX IF NOT EXISTS idx_primary_district 
ON tb_primary_schools(district);

CREATE INDEX IF NOT EXISTS idx_primary_category 
ON tb_primary_schools(school_category);

CREATE INDEX IF NOT EXISTS idx_primary_school_net 
ON tb_primary_schools(school_net);

CREATE INDEX IF NOT EXISTS idx_primary_gender 
ON tb_primary_schools(student_gender);

CREATE INDEX IF NOT EXISTS idx_primary_religion 
ON tb_primary_schools(religion);

CREATE INDEX IF NOT EXISTS idx_primary_teaching_language 
ON tb_primary_schools(teaching_language);

-- 2. 添加复合索引（针对常见组合查询）
CREATE INDEX IF NOT EXISTS idx_primary_district_category 
ON tb_primary_schools(district, school_category);

CREATE INDEX IF NOT EXISTS idx_primary_district_net 
ON tb_primary_schools(district, school_net);

CREATE INDEX IF NOT EXISTS idx_primary_category_gender 
ON tb_primary_schools(school_category, student_gender);

-- 3. 添加school_name的前缀索引（用于搜索）
CREATE INDEX IF NOT EXISTS idx_primary_name_prefix 
ON tb_primary_schools(school_name(20));

-- 4. 优化表
OPTIMIZE TABLE tb_primary_schools;

-- 5. 更新统计信息
ANALYZE TABLE tb_primary_schools;

-- 查看小学表索引
SHOW INDEX FROM tb_primary_schools;

-- ========================================
-- 中学表 (tb_secondary_schools) 优化
-- ========================================

-- 1. 添加常用查询字段的索引
CREATE INDEX IF NOT EXISTS idx_secondary_district 
ON tb_secondary_schools(district);

CREATE INDEX IF NOT EXISTS idx_secondary_category 
ON tb_secondary_schools(school_category);

CREATE INDEX IF NOT EXISTS idx_secondary_group 
ON tb_secondary_schools(school_group);

CREATE INDEX IF NOT EXISTS idx_secondary_gender 
ON tb_secondary_schools(student_gender);

CREATE INDEX IF NOT EXISTS idx_secondary_religion 
ON tb_secondary_schools(religion);

-- 2. 添加复合索引（针对常见组合查询）
CREATE INDEX IF NOT EXISTS idx_secondary_district_category 
ON tb_secondary_schools(district, school_category);

CREATE INDEX IF NOT EXISTS idx_secondary_district_group 
ON tb_secondary_schools(district, school_group);

CREATE INDEX IF NOT EXISTS idx_secondary_category_group 
ON tb_secondary_schools(school_category, school_group);

CREATE INDEX IF NOT EXISTS idx_secondary_group_gender 
ON tb_secondary_schools(school_group, student_gender);

-- 3. 添加school_name的前缀索引（用于搜索）
CREATE INDEX IF NOT EXISTS idx_secondary_name_prefix 
ON tb_secondary_schools(school_name(20));

-- 4. 优化表
OPTIMIZE TABLE tb_secondary_schools;

-- 5. 更新统计信息
ANALYZE TABLE tb_secondary_schools;

-- 查看中学表索引
SHOW INDEX FROM tb_secondary_schools;

-- ========================================
-- 性能监控查询
-- ========================================

-- 查看表大小和行数
SELECT 
    TABLE_NAME,
    TABLE_ROWS,
    ROUND(DATA_LENGTH / 1024 / 1024, 2) AS 'Data Size (MB)',
    ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS 'Index Size (MB)',
    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS 'Total Size (MB)'
FROM 
    information_schema.TABLES 
WHERE 
    TABLE_SCHEMA = 'dev_yundisoft' 
    AND TABLE_NAME IN ('tb_primary_schools', 'tb_secondary_schools');

-- 查看索引使用情况
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    CARDINALITY,
    SEQ_IN_INDEX
FROM 
    information_schema.STATISTICS
WHERE 
    TABLE_SCHEMA = 'dev_yundisoft'
    AND TABLE_NAME IN ('tb_primary_schools', 'tb_secondary_schools')
ORDER BY 
    TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- ========================================
-- 查询性能测试
-- ========================================

-- 测试小学表查询
EXPLAIN SELECT * FROM tb_primary_schools WHERE district = '中西区' LIMIT 20;
EXPLAIN SELECT * FROM tb_primary_schools WHERE school_category = '官立' LIMIT 20;
EXPLAIN SELECT * FROM tb_primary_schools WHERE school_name LIKE '圣%' LIMIT 20;

-- 测试中学表查询
EXPLAIN SELECT * FROM tb_secondary_schools WHERE district = '中西区' LIMIT 20;
EXPLAIN SELECT * FROM tb_secondary_schools WHERE school_group = 'Band 1' LIMIT 20;
EXPLAIN SELECT * FROM tb_secondary_schools WHERE school_name LIKE '圣%' LIMIT 20;

-- ========================================
-- 使用说明
-- ========================================
/*
1. 在MySQL客户端中执行此脚本：
   docker exec -i edu_mysql mysql -u root -pfgdTv@4629uGdY dev_yundisoft < backend/common/db/optimize_primary_secondary_indexes.sql

2. 或者在MySQL命令行中：
   source /path/to/optimize_primary_secondary_indexes.sql

3. 验证索引创建：
   SHOW INDEX FROM tb_primary_schools;
   SHOW INDEX FROM tb_secondary_schools;

4. 监控查询性能：
   - 使用EXPLAIN分析查询计划
   - 检查慢查询日志
*/

