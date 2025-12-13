-- 添加小学详情字段
-- 执行前请备份数据库
-- 如果字段已存在会报错，可忽略继续执行

-- 学校类别2（全日/半日）
ALTER TABLE tb_primary_schools ADD COLUMN school_category_2 VARCHAR(50) NULL;

-- 基本信息
ALTER TABLE tb_primary_schools ADD COLUMN school_sponsor VARCHAR(200) NULL;
ALTER TABLE tb_primary_schools ADD COLUMN founded_year VARCHAR(20) NULL;
ALTER TABLE tb_primary_schools ADD COLUMN school_motto VARCHAR(500) NULL;
ALTER TABLE tb_primary_schools ADD COLUMN school_area VARCHAR(100) NULL;

-- 教师信息
ALTER TABLE tb_primary_schools ADD COLUMN teacher_count INT NULL;
ALTER TABLE tb_primary_schools ADD COLUMN teacher_info JSON NULL;

-- 设施信息
ALTER TABLE tb_primary_schools ADD COLUMN classroom_count INT NULL;
ALTER TABLE tb_primary_schools ADD COLUMN hall_count INT NULL;
ALTER TABLE tb_primary_schools ADD COLUMN playground_count INT NULL;
ALTER TABLE tb_primary_schools ADD COLUMN library_count INT NULL;
ALTER TABLE tb_primary_schools ADD COLUMN special_rooms TEXT NULL;

-- 交通信息
ALTER TABLE tb_primary_schools ADD COLUMN school_bus VARCHAR(100) NULL;
ALTER TABLE tb_primary_schools ADD COLUMN nanny_bus VARCHAR(100) NULL;

-- 班级信息
ALTER TABLE tb_primary_schools ADD COLUMN classes_by_grade JSON NULL;
ALTER TABLE tb_primary_schools ADD COLUMN class_teaching_mode TEXT NULL;

-- 评估信息
ALTER TABLE tb_primary_schools ADD COLUMN multi_assessment TEXT NULL;
ALTER TABLE tb_primary_schools ADD COLUMN class_arrangement TEXT NULL;

-- 学校生活
ALTER TABLE tb_primary_schools ADD COLUMN lunch_arrangement TEXT NULL;
ALTER TABLE tb_primary_schools ADD COLUMN school_life_notes TEXT NULL;

-- 学校特色
ALTER TABLE tb_primary_schools ADD COLUMN whole_person_learning TEXT NULL;
ALTER TABLE tb_primary_schools ADD COLUMN school_mission TEXT NULL;
ALTER TABLE tb_primary_schools ADD COLUMN diversity_support TEXT NULL;
