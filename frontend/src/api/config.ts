// API配置
export const API_CONFIG = {
  // 使用相对路径，自动适配 betterschool.hk 和 www.betterschool.hk
  BASE_URL: '/api',
  
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
    LIST: '/schools/',                    // GET 获取学校列表（通用）
    PRIMARY: '/schools/primary/',         // GET 获取小学列表
    SECONDARY: '/schools/secondary/',     // GET 获取中学列表
    DETAIL: '/schools/:id/',              // GET 获取学校详情
    STATS: '/schools/stats/',             // GET 获取学校统计信息
    PRIMARY_FILTERS: '/schools/primary/filters/',  // GET 获取小学筛选选项
    SECONDARY_FILTERS: '/schools/secondary/filters/',  // GET 获取中学筛选选项
  },
  
  // 其他可能的接口
  DISTRICTS: '/districts/',      // GET 获取地区列表
  CATEGORIES: '/categories/',    // GET 获取学校分类
} 