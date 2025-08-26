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
}

// 分页响应数据
export interface PageData<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
} 