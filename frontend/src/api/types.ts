// API响应通用类型
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  success: boolean
}

// 分页查询参数
export interface PageQuery {
  page?: number
  pageSize?: number
  type?: 'primary' | 'secondary'
  category?: string
  district?: string
  applicationStatus?: string
  keyword?: string
  
  // 中学特有查询参数
  schoolGroup?: string  // 学校组别
  gender?: string  // 学生性别
  religion?: string  // 宗教
}

// 分页响应数据
export interface PageData<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
} 