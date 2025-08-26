export interface School {
  id: number
  name: string
  type: 'primary' | 'secondary'
  category: 'elite' | 'traditional' | 'direct' | 'government'
  band1Rate: number
  applicationStatus: 'open' | 'closed' | 'deadline'
  district: string
  schoolNet: string
  tuition: number
  gender: 'coed' | 'boys' | 'girls'
  feederSchools: string[]
  linkedUniversities: string[]
  image?: string
}

export interface SchoolStats {
  totalSchools: number
  openApplications: number
} 