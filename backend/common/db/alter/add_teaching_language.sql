-- 为 tb_schools 添加 teaching_language 列
ALTER TABLE tb_schools 
ADD COLUMN teaching_language VARCHAR(100) 
COMMENT '授课语言（中文/英文/中英并重/其他）' 
AFTER gender;

-- 为 tb_secondary_schools 添加 teaching_language 列
ALTER TABLE tb_secondary_schools 
ADD COLUMN teaching_language VARCHAR(100) 
COMMENT '授课语言（中文/英文/中英并重/其他）' 
AFTER student_gender;

-- 为 teaching_language 添加索引
CREATE INDEX idx_teaching_language ON tb_schools(teaching_language);
CREATE INDEX idx_sec_teaching_language ON tb_secondary_schools(teaching_language);

