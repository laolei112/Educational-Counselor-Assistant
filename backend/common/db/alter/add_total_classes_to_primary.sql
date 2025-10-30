-- 为小学表增加 total_classes 字段（整型，可空）
ALTER TABLE `tb_primary_schools`
ADD COLUMN `total_classes` INT NULL COMMENT '总班数或估算数值' AFTER `tuition`;


