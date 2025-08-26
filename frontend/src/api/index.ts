// 导出所有API相关的模块
export * from './config'
export * from './types'
export * from './request'
export * from './school'

// 统一的API对象，便于使用
import { schoolApi } from './school'

export const api = {
  school: schoolApi
}

// 导出默认API对象
export default api 