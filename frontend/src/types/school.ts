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
  
  // 小学特有字段
  classTeachingInfo?: {
    class_teaching_mode?: string  // 班级教学模式
    class_arrangement?: string  // 分班安排
    class_structure_note?: string  // 班级结构备注
  }
  promotionInfo?: any  // 升学信息
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