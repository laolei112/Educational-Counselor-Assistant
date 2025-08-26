// API配置
export const API_CONFIG = {
  // 开发环境API地址，您可以根据需要调整
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api',
  
  // 请求超时时间
  TIMEOUT: 10000,
  
  // 请求头
  HEADERS: {
    'Content-Type': 'application/json',
  }
}

// API路径常量
export const API_PATHS = {
  // 学校相关接口
  SCHOOLS: {
    LIST: '/schools',           // GET 获取学校列表
    DETAIL: '/schools/:id',     // GET 获取学校详情
    STATS: '/schools/stats',    // GET 获取学校统计信息
  },
  
  // 其他可能的接口
  DISTRICTS: '/districts',      // GET 获取地区列表
  CATEGORIES: '/categories',    // GET 获取学校分类
} 