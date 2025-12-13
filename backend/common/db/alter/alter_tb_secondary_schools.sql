-- ============================================================
-- ALTER TABLE: tb_secondary_schools
-- 新增字段以支持中学详细信息导入
-- 执行前请备份数据库
-- ============================================================

-- ========== 基本信息字段 ==========

-- 学校占地面积
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `school_area` VARCHAR(100) NULL DEFAULT NULL COMMENT '学校占地面积' AFTER `website`;

-- 办学团体
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `school_sponsor` VARCHAR(200) NULL DEFAULT NULL COMMENT '办学团体名称' AFTER `school_area`;

-- 创校年份
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `founded_year` VARCHAR(20) NULL DEFAULT NULL COMMENT '学校创办年份' AFTER `school_sponsor`;

-- 校训
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `school_motto` VARCHAR(500) NULL DEFAULT NULL COMMENT '学校校训' AFTER `founded_year`;

-- ========== 教师信息字段 ==========

-- 教师总人数
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `teacher_count` INT NULL DEFAULT NULL COMMENT '学校教师总人数' AFTER `school_motto`;

-- 教师信息 (JSON格式：学历和经验比例)
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `teacher_info` JSON NULL DEFAULT NULL COMMENT '教师学历和经验比例信息，JSON格式' AFTER `teacher_count`;

-- ========== 班级信息字段 ==========

-- 各年级班数 (JSON格式)
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `classes_by_grade` JSON NULL DEFAULT NULL COMMENT '各年级班级数量，JSON格式' AFTER `teacher_info`;

-- ========== 课程信息字段 ==========

-- 按教学语言分类的科目 (JSON格式)
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `curriculum_by_language` JSON NULL DEFAULT NULL COMMENT '按教学语言分类的开设科目，JSON格式' AFTER `classes_by_grade`;

-- ========== 学校政策与特色字段 ==========

-- 全校语文政策
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `language_policy` TEXT NULL DEFAULT NULL COMMENT '学校的语文政策' AFTER `curriculum_by_language`;

-- 学习和教学策略
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `teaching_strategy` TEXT NULL DEFAULT NULL COMMENT '学校的学习和教学策略' AFTER `language_policy`;

-- 校本课程
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `school_based_curriculum` TEXT NULL DEFAULT NULL COMMENT '学校的校本课程' AFTER `teaching_strategy`;

-- 生涯规划教育
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `career_education` TEXT NULL DEFAULT NULL COMMENT '学校的生涯规划教育' AFTER `school_based_curriculum`;

-- 照顾学生多样性
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `diversity_support` TEXT NULL DEFAULT NULL COMMENT '全校参与照顾学生的多样性措施' AFTER `career_education`;

-- 测考及学习调适措施
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `assessment_adaptation` TEXT NULL DEFAULT NULL COMMENT '学校的测考及学习调适措施' AFTER `diversity_support`;

-- 全方位学习
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `whole_person_learning` TEXT NULL DEFAULT NULL COMMENT '学校的全方位学习活动' AFTER `assessment_adaptation`;

-- ========== 设施与交通字段 ==========

-- 学校设施
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `facilities` TEXT NULL DEFAULT NULL COMMENT '学校的设施介绍' AFTER `whole_person_learning`;

-- 公共交通
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `transportation` TEXT NULL DEFAULT NULL COMMENT '直达学校的公共交通工具' AFTER `facilities`;

-- 备注
ALTER TABLE `tb_secondary_schools` 
ADD COLUMN `remarks` TEXT NULL DEFAULT NULL COMMENT '其他备注信息' AFTER `transportation`;


-- ============================================================
-- 验证新增字段
-- ============================================================
-- SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_COMMENT 
-- FROM INFORMATION_SCHEMA.COLUMNS 
-- WHERE TABLE_NAME = 'tb_secondary_schools' 
-- AND TABLE_SCHEMA = DATABASE()
-- ORDER BY ORDINAL_POSITION;
