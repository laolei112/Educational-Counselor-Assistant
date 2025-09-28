export interface School {
  id: number
  name: string
  type: 'primary' | 'secondary'
  category: 'elite' | 'traditional' | 'direct' | 'government' | 'private'
  band1Rate: number
  applicationStatus: 'open' | 'closed' | 'deadline'
  district: string
  schoolNet: string | number
  tuition: number
  gender: 'coed' | 'boys' | 'girls'
  feederSchools: string[]
  linkedUniversities: string[]
  image?: string
  
  // 新增字段
  schoolScale?: {
    classes: number
    students: number
  }
  teachingLanguage?: string
  curriculum?: string[]
  religion?: string
  schoolType?: 'government' | 'aided' | 'direct' | 'private'
  features?: string[]
  contact?: {
    address?: string
    phone?: string
    email?: string
    website?: string
  }
  applicationDeadline?: string
  linkedSchools?: string[]
}

export interface SchoolStats {
  totalSchools: number
  openApplications: number
} 