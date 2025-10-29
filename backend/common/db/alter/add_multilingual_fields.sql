-- 添加多语言字段到小学和中学表
-- 执行时间：2024年
-- 说明：为学校名称添加繁体和英文字段支持

-- 为小学表添加多语言字段
ALTER TABLE tb_primary_schools 
ADD COLUMN school_name_traditional VARCHAR(100) NULL COMMENT '学校名称（繁体）',
ADD COLUMN school_name_english VARCHAR(100) NULL COMMENT '学校名称（英文）';

-- 为中学表添加多语言字段
ALTER TABLE tb_secondary_schools 
ADD COLUMN school_name_traditional VARCHAR(100) NULL COMMENT '学校名称（繁体）',
ADD COLUMN school_name_english VARCHAR(100) NULL COMMENT '学校名称（英文）';

-- 添加索引以提高查询性能
ALTER TABLE tb_primary_schools 
ADD INDEX idx_pri_name_traditional (school_name_traditional),
ADD INDEX idx_pri_name_english (school_name_english);

ALTER TABLE tb_secondary_schools 
ADD INDEX idx_sec_name_traditional (school_name_traditional),
ADD INDEX idx_sec_name_english (school_name_english);

-- 更新现有数据（可选）
-- 如果现有数据需要设置繁体或英文名称，可以在这里添加UPDATE语句
-- 例如：
-- UPDATE tb_primary_schools SET school_name_traditional = school_name WHERE school_name_traditional IS NULL;
-- UPDATE tb_primary_schools SET school_name_english = school_name WHERE school_name_english IS NULL;
