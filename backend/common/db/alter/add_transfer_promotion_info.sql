-- =====================================================
-- 添加插班信息和升学信息字段（简化版）
-- 创建时间: 2025-10-19
-- 说明: 为小学和中学表添加插班信息和升学信息的 JSON 字段
-- 注意: 如果字段已存在会报错，请使用 add_transfer_promotion_info.sql
-- =====================================================

-- 为 tb_primary_schools 添加字段
ALTER TABLE tb_primary_schools 
ADD COLUMN transfer_info JSON COMMENT '插班信息' AFTER assessment_info;

ALTER TABLE tb_primary_schools 
ADD COLUMN promotion_info JSON COMMENT '升学信息' AFTER transfer_info;


-- 为 tb_secondary_schools 添加/修改字段
-- 如果原来有 transfer_open_time 字段，改名并修改类型为 JSON
-- 如果没有，请注释掉下面这行，使用后面的 ADD COLUMN
ALTER TABLE tb_secondary_schools 
CHANGE COLUMN transfer_open_time transfer_info JSON COMMENT '插班信息';

-- 如果原来就有 transfer_info 字段，使用这行（需注释掉上面的 CHANGE）
-- ALTER TABLE tb_secondary_schools 
-- ADD COLUMN transfer_info JSON COMMENT '插班信息' AFTER school_group;

-- 添加升学信息字段
ALTER TABLE tb_secondary_schools 
ADD COLUMN promotion_info JSON COMMENT '升学信息' AFTER transfer_info;

