-- 将 band1_rate 从生成列改为普通列，支持手工维护
-- 执行时间：2025年
-- 说明：允许手工维护 band1_rate，添加 band1_rate_manual 标志字段

-- 步骤1: 删除 band1_rate 上的索引（如果存在）
-- 注意：如果索引不存在，此语句会报错，但可以安全忽略，继续执行后续步骤
-- 如果确定索引不存在，可以注释掉下面这一行
ALTER TABLE tb_primary_schools DROP INDEX idx_band1_rate;

-- 步骤2: 删除生成列 band1_rate
-- 注意：在MySQL中，删除生成列需要先删除列，然后重新创建
ALTER TABLE tb_primary_schools 
DROP COLUMN band1_rate;

-- 步骤3: 重新创建 band1_rate 为普通列（允许写入）
ALTER TABLE tb_primary_schools 
ADD COLUMN band1_rate DECIMAL(5,2) NULL COMMENT '升Band 1比例';

-- 步骤4: 从 promotion_info JSON 中提取现有数据填充 band1_rate
-- 只更新 band1_rate 为 NULL 的记录，保留已有值
UPDATE tb_primary_schools 
SET band1_rate = CAST(JSON_EXTRACT(promotion_info, '$.band1_rate') AS DECIMAL(5,2))
WHERE promotion_info IS NOT NULL 
  AND JSON_EXTRACT(promotion_info, '$.band1_rate') IS NOT NULL
  AND JSON_EXTRACT(promotion_info, '$.band1_rate') != 'null'
  AND band1_rate IS NULL;

-- 步骤6: 重新创建索引以提高查询性能
CREATE INDEX idx_band1_rate ON tb_primary_schools(band1_rate DESC);

