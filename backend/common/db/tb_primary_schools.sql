-- 创建小学信息表
CREATE TABLE IF NOT EXISTS tb_primary_schools (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    -- 基本信息
    school_name VARCHAR(100) NOT NULL COMMENT '学校名称',
    district VARCHAR(50) COMMENT '区域',
    school_net VARCHAR(20) COMMENT '小一学校网',
    address VARCHAR(300) COMMENT '学校地址',
    phone VARCHAR(20) COMMENT '学校电话',
    fax VARCHAR(20) COMMENT '学校传真',
    email VARCHAR(100) COMMENT '学校电邮',
    website VARCHAR(200) COMMENT '学校网址',
    
    -- 学校分类
    school_category VARCHAR(50) COMMENT '学校类别（资助/直资/私立/官立）',
    student_gender VARCHAR(20) COMMENT '学生性别（男/女/男女）',
    religion VARCHAR(50) COMMENT '宗教',
    teaching_language VARCHAR(100) COMMENT '教学语言',
    school_basic_info JSON COMMENT '学校基础信息',
    -- 中学联系
    secondary_info JSON COMMENT '中学联系信息',
    -- 收费信息
    tuition VARCHAR(200) COMMENT '学费',
    -- 班级结构（本学年）
    total_classes_info JSON COMMENT '总班数信息',
    -- 教学模式
    class_teaching_info JSON COMMENT '班级教学信息',
    -- 评估政策
    assessment_info JSON COMMENT '学习评估信息',

    -- 系统字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引优化
    INDEX idx_school_name (school_name),
    INDEX idx_district (district),
    INDEX idx_school_net (school_net),
    INDEX idx_school_category (school_category),
    INDEX idx_student_gender (student_gender),
    INDEX idx_religion (religion),
    INDEX idx_teaching_language (teaching_language)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='香港小学信息表';

