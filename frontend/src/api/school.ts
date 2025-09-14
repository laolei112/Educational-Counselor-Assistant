import { http } from './request'
import { API_PATHS } from './config'
import type { School, SchoolStats } from '@/types/school'
import type { PageQuery, PageData } from './types'

// 学校API服务类
export class SchoolApi {
  /**
   * 获取学校列表（通用）
   * @param query 查询参数
   * @returns 学校列表和分页信息
   */
  static async getSchools(query: PageQuery = {}) {
    return http.get<PageData<School>>(API_PATHS.SCHOOLS.LIST, query)
  }

  /**
   * 获取小学列表
   * @param query 查询参数
   * @returns 小学列表和分页信息
   */
  static async getPrimarySchools(query: PageQuery = {}) {
    return http.get<PageData<School>>(API_PATHS.SCHOOLS.PRIMARY, query)
  }

  /**
   * 获取中学列表
   * @param query 查询参数
   * @returns 中学列表和分页信息
   */
  static async getSecondarySchools(query: PageQuery = {}) {
    return http.get<PageData<School>>(API_PATHS.SCHOOLS.SECONDARY, query)
  }

  /**
   * 获取学校详情
   * @param id 学校ID
   * @returns 学校详细信息
   */
  static async getSchoolDetail(id: number) {
    const path = API_PATHS.SCHOOLS.DETAIL.replace(':id', String(id))
    return http.get<School>(path)
  }

  /**
   * 获取学校统计信息
   * @param type 学校类型 (primary | secondary)
   * @returns 统计信息
   */
  static async getSchoolStats(type?: 'primary' | 'secondary') {
    return http.get<SchoolStats>(API_PATHS.SCHOOLS.STATS, { type })
  }

  /**
   * 搜索学校
   * @param keyword 关键词
   * @param query 其他查询参数
   * @returns 搜索结果
   */
  static async searchSchools(keyword: string, query: PageQuery = {}) {
    return http.get<PageData<School>>(API_PATHS.SCHOOLS.LIST, {
      ...query,
      keyword
    })
  }

  /**
   * 搜索小学
   * @param keyword 关键词
   * @param query 其他查询参数
   * @returns 搜索结果
   */
  static async searchPrimarySchools(keyword: string, query: PageQuery = {}) {
    return http.get<PageData<School>>(API_PATHS.SCHOOLS.PRIMARY, {
      ...query,
      keyword
    })
  }

  /**
   * 搜索中学
   * @param keyword 关键词
   * @param query 其他查询参数
   * @returns 搜索结果
   */
  static async searchSecondarySchools(keyword: string, query: PageQuery = {}) {
    return http.get<PageData<School>>(API_PATHS.SCHOOLS.SECONDARY, {
      ...query,
      keyword
    })
  }
}

// 导出便捷的函数接口
export const schoolApi = {
  // 获取学校列表
  getList: SchoolApi.getSchools,
  
  // 获取小学列表
  getPrimaryList: SchoolApi.getPrimarySchools,
  
  // 获取中学列表
  getSecondaryList: SchoolApi.getSecondarySchools,
  
  // 获取学校详情
  getDetail: SchoolApi.getSchoolDetail,
  
  // 获取统计信息
  getStats: SchoolApi.getSchoolStats,
  
  // 搜索学校
  search: SchoolApi.searchSchools,
  
  // 搜索小学
  searchPrimary: SchoolApi.searchPrimarySchools,
  
  // 搜索中学
  searchSecondary: SchoolApi.searchSecondarySchools,
  
  // 按类型获取学校
  getByType: (type: 'primary' | 'secondary', query: Omit<PageQuery, 'type'> = {}) =>
    type === 'primary' ? SchoolApi.getPrimarySchools(query) : SchoolApi.getSecondarySchools(query),
    
  // 按分类获取学校
  getByCategory: (category: string, query: Omit<PageQuery, 'category'> = {}) =>
    SchoolApi.getSchools({ ...query, category }),
    
  // 按地区获取学校
  getByDistrict: (district: string, query: Omit<PageQuery, 'district'> = {}) =>
    SchoolApi.getSchools({ ...query, district })
} 