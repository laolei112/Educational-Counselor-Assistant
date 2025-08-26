import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { School, SchoolStats } from '@/types/school'
import { schoolApi } from '@/api/school'
import type { PageQuery } from '@/api/types'

export const useSchoolStore = defineStore('school', () => {
  // 状态
  const schools = ref<School[]>([])
  const currentType = ref<'primary' | 'secondary'>('secondary')
  const loading = ref(false)
  const error = ref<string | null>(null)
  const stats = ref<SchoolStats>({ totalSchools: 0, openApplications: 0 })
  
  // 是否启用Mock模式（当后端不可用时使用静态数据）
  const enableMock = ref(import.meta.env.VITE_ENABLE_MOCK === 'true' || false)
  
  // Mock数据（作为后备）
  const mockSchools: School[] = [
    // 中学数据
    {
      id: 1,
      name: '圣保罗男女中学',
      type: 'secondary',
      category: 'elite',
      band1Rate: 94,
      applicationStatus: 'open',
      district: '中西区',
      schoolNet: '校网11',
      tuition: 36800,
      gender: 'coed',
      feederSchools: ['圣保罗书院'],
      linkedUniversities: ['香港大学']
    },
    {
      id: 2,
      name: '喇沙书院',
      type: 'secondary',
      category: 'traditional',
      band1Rate: 88,
      applicationStatus: 'closed',
      district: '九龙城',
      schoolNet: '校网41',
      tuition: 28500,
      gender: 'boys',
      feederSchools: ['喇沙小学'],
      linkedUniversities: ['香港中文大学']
    },
    {
      id: 3,
      name: '拔萃女书院',
      type: 'secondary',
      category: 'direct',
      band1Rate: 96,
      applicationStatus: 'open',
      district: '九龙城',
      schoolNet: '校网41',
      tuition: 42000,
      gender: 'girls',
      feederSchools: ['拔萃女小学'],
      linkedUniversities: ['香港大学', '香港中文大学']
    },
    // 小学数据
    {
      id: 4,
      name: '拔萃女小学',
      type: 'primary',
      category: 'direct',
      band1Rate: 98,
      applicationStatus: 'open',
      district: '九龙城',
      schoolNet: '校网41',
      tuition: 38000,
      gender: 'girls',
      feederSchools: [],
      linkedUniversities: ['拔萃女书院']
    },
    {
      id: 5,
      name: '圣保罗男女中学附属小学',
      type: 'primary',
      category: 'elite',
      band1Rate: 95,
      applicationStatus: 'open',
      district: '南区',
      schoolNet: '校网18',
      tuition: 32000,
      gender: 'coed',
      feederSchools: [],
      linkedUniversities: ['圣保罗男女中学']
    },
    {
      id: 6,
      name: '喇沙小学',
      type: 'primary',
      category: 'traditional',
      band1Rate: 92,
      applicationStatus: 'closed',
      district: '九龙城',
      schoolNet: '校网41',
      tuition: 0,
      gender: 'boys',
      feederSchools: [],
      linkedUniversities: ['喇沙书院']
    }
  ]

  // 计算属性
  const filteredSchools = computed(() => {
    return schools.value.filter(school => school.type === currentType.value)
  })

  const isLoading = computed(() => loading.value)
  const hasError = computed(() => !!error.value)

  // Actions
  
  /**
   * 获取学校列表
   */
  const fetchSchools = async (query: PageQuery = {}) => {
    if (enableMock.value) {
      // Mock模式：使用静态数据
      schools.value = mockSchools
      await updateStats()
      return
    }

    try {
      loading.value = true
      error.value = null

      const response = await schoolApi.getList(query)
      
      if (response.success) {
        schools.value = response.data.list
      } else {
        throw new Error(response.message || '获取学校列表失败')
      }
    } catch (err) {
      console.error('获取学校列表失败:', err)
      error.value = err instanceof Error ? err.message : '获取学校列表失败'
      
      // 失败时回退到Mock数据
      schools.value = mockSchools
      console.warn('已回退到Mock数据')
    } finally {
      loading.value = false
      await updateStats()
    }
  }

  /**
   * 更新统计信息
   */
  const updateStats = async () => {
    if (enableMock.value) {
      // Mock模式：计算本地数据统计
      const filtered = schools.value.filter(school => school.type === currentType.value)
      stats.value = {
        totalSchools: filtered.length,
        openApplications: filtered.filter(school => school.applicationStatus === 'open').length
      }
      return
    }

    try {
      const response = await schoolApi.getStats(currentType.value)
      
      if (response.success) {
        stats.value = response.data
      } else {
        throw new Error(response.message || '获取统计信息失败')
      }
    } catch (err) {
      console.error('获取统计信息失败:', err)
      // 失败时计算本地数据统计
      const filtered = schools.value.filter(school => school.type === currentType.value)
      stats.value = {
        totalSchools: filtered.length,
        openApplications: filtered.filter(school => school.applicationStatus === 'open').length
      }
    }
  }

  /**
   * 设置学校类型并重新获取数据
   */
  const setSchoolType = async (type: 'primary' | 'secondary') => {
    currentType.value = type
    await updateStats()
  }

  /**
   * 搜索学校
   */
  const searchSchools = async (keyword: string, query: PageQuery = {}) => {
    if (enableMock.value) {
      // Mock模式：本地搜索
      const filtered = mockSchools.filter(school => 
        school.name.includes(keyword) || 
        school.district.includes(keyword)
      )
      schools.value = filtered
      return
    }

    try {
      loading.value = true
      error.value = null

      const response = await schoolApi.search(keyword, query)
      
      if (response.success) {
        schools.value = response.data.list
      } else {
        throw new Error(response.message || '搜索失败')
      }
    } catch (err) {
      console.error('搜索学校失败:', err)
      error.value = err instanceof Error ? err.message : '搜索失败'
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置错误状态
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * 切换Mock模式
   */
  const toggleMockMode = async (enabled: boolean) => {
    enableMock.value = enabled
    await fetchSchools()
  }

  return {
    // 状态
    schools,
    currentType,
    loading,
    error,
    stats,
    enableMock,
    
    // 计算属性
    filteredSchools,
    isLoading,
    hasError,
    
    // Actions
    fetchSchools,
    updateStats,
    setSchoolType,
    searchSchools,
    clearError,
    toggleMockMode
  }
}) 