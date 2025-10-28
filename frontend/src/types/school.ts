export interface School {
  id: number
  name: string
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
  address?: string
  phone?: string
  email?: string
  website?: string
  officialWebsite?: string
  createdAt?: string
  updatedAt?: string
}

export interface SchoolStats {
  totalSchools: number
  openApplications: number
} 