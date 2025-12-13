export interface School {
  id: number
  name: string
  nameTraditional?: string
  nameEnglish?: string
  type: 'primary' | 'secondary'
  category?: 'elite' | 'traditional' | 'direct' | 'government' | 'private'
  band1Rate?: number
  applicationStatus?: 'open' | 'closed' | 'deadline'
  district?: string
  schoolNet?: string | number
  tuition?: number | string
  gender?: 'coed' | 'boys' | 'girls' | string
  feederSchools?: string[]
  linkedUniversities?: string[]
  image?: string
  
  // 小学和中学通用字段
  schoolScale?: {
    classes: number
    students: number
  }
  teachingLanguage?: string
  curriculum?: string[]
  religion?: string
  schoolType?: string
  features?: string[]
  contact?: {
    address?: string
    phone?: string
    email?: string
    website?: string
  }
  applicationDeadline?: string
  secondaryInfo?: {
    through_train?: string
    direct?: string
    associated?: string
  }
  
  // 中学特有字段 (tb_secondary_schools)
  schoolGroup?: string  // 学校组别 (1A, 1B, 2A, 2B等)
  transferOpenTime?: string  // 插班开放时间
  totalClasses?: number  // 全校总班数
  admissionInfo?: string  // 入学信息
  schoolCurriculum?: string  // 课程设置
  transferInfo?: TransferInfo  // 插班信息
  address?: string
  phone?: string
  email?: string
  website?: string
  officialWebsite?: string
  createdAt?: string
  updatedAt?: string
  
  // ========== 中学新增字段 ==========
  // 基本信息
  schoolArea?: string  // 学校占地面积
  schoolSponsor?: string  // 办学团体
  foundedYear?: string  // 创校年份
  schoolMotto?: string  // 校训
  
  // 教师信息
  teacherCount?: number  // 教师总人数
  teacherInfo?: TeacherInfo  // 教师学历和经验比例
  
  // 班级信息
  classesByGrade?: ClassesByGrade  // 各年级班数
  
  // 课程信息（按教学语言分类）
  curriculumByLanguage?: CurriculumByLanguage
  
  // 学校政策与特色
  languagePolicy?: string  // 全校语文政策
  teachingStrategy?: string  // 学习和教学策略
  schoolBasedCurriculum?: string  // 校本课程
  careerEducation?: string  // 生涯规划教育
  diversitySupport?: string  // 照顾学生多样性
  assessmentAdaptation?: string  // 测考及学习调适措施
  wholePersonLearning?: string  // 全方位学习
  
  // 设施与交通
  facilities?: string  // 学校设施
  transportation?: string  // 公共交通
  remarks?: string  // 备注
  
  // 小学特有字段
  classTeachingInfo?: {
    class_teaching_mode?: string  // 班级教学模式
    class_arrangement?: string  // 分班安排
    class_structure_note?: string  // 班级结构备注
  }
  promotionInfo?: any  // 升学信息
}

// 教师信息类型
export interface TeacherInfo {
  bachelor_rate?: string  // 学士学位百分率
  master_phd_rate?: string  // 碩士/博士百分率
  special_education_rate?: string  // 特殊教育培训百分率
  experience_0_4_years?: string  // 0-4年经验百分率
  experience_5_9_years?: string  // 5-9年经验百分率
  experience_10_plus_years?: string  // 10年以上经验百分率
}

// 各年级班数类型
export interface ClassesByGrade {
  S1?: number  // 中一班数
  S2?: number  // 中二班数
  S3?: number  // 中三班数
  S4?: number  // 中四班数
  S5?: number  // 中五班数
  S6?: number  // 中六班数
  total?: number  // 总班数
}

// 按教学语言分类的课程类型
export interface CurriculumByLanguage {
  junior?: {  // 中一至中三
    chinese_medium?: string  // 中文授课科目
    english_medium?: string  // 英文授课科目
    mixed_medium?: string  // 按班别/组别订定教学语言
  }
  senior?: {  // 中四至中六
    chinese_medium?: string
    english_medium?: string
    mixed_medium?: string
  }
}

// 插班信息类型定义
export interface TransferInfo {
  // 中学入学信息
  S1?: {
    入学申请开始时间?: string
    入学申请截至时间?: string
    申请详情地址?: string
  }
  // 小学入学信息
  小一?: {
    小一入学申请开始时间?: string
    小一入学申请截至时间?: string
    小一申请详情地址?: string
  }
  // 插班信息（小学和中学共用）
  插班?: {
    插班申请开始时间1?: string
    插班申请截止时间1?: string
    可插班年级1?: string
    插班申请开始时间2?: string
    插班申请截止时间2?: string
    可插班年级2?: string
    插班详情链接?: string
    插班申请详情链接?: string  // 兼容新格式
  }
  application_status?: 'open' | 'closed' | 'deadline'
  application_deadline?: string
}

export interface SchoolStats {
  totalSchools: number
  openApplications: number
} 