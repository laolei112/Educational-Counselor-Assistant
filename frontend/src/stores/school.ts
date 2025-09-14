import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { School, SchoolStats } from '@/types/school'
import { schoolApi } from '@/api/school'
import type { PageQuery, PageData } from '@/api/types'

export const useSchoolStore = defineStore('school', () => {
  // 状态
  const schools = ref<School[]>([])
  const currentType = ref<'primary' | 'secondary'>('secondary')
  const loading = ref(false)
  const error = ref<string | null>(null)
  const stats = ref<SchoolStats>({ totalSchools: 0, openApplications: 0 })
  
  // 分页状态
  const pagination = ref({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  })
  
  // 搜索状态
  const searchKeyword = ref('')
  const searchFilters = ref({
    category: '',
    district: '',
    applicationStatus: ''
  })
  
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
  
  // 是否有搜索结果
  const hasSearchResults = computed(() => searchKeyword.value.length > 0)
  
  // 当前页面数据 - 直接使用 schools.value，因为 API 已经返回了分页后的数据
  const currentPageData = computed(() => {
    return schools.value
  })

  // Actions
  
  /**
   * 获取学校列表
   */
  const fetchSchools = async (query: PageQuery = {}) => {
    if (enableMock.value) {
      // Mock模式：使用静态数据
      schools.value = mockSchools
      pagination.value = {
        page: 1,
        pageSize: 20,
        total: mockSchools.filter(school => school.type === currentType.value).length,
        totalPages: Math.ceil(mockSchools.filter(school => school.type === currentType.value).length / 20)
      }
      await updateStats()
      return
    }

    try {
      loading.value = true
      error.value = null

      // 根据学校类型选择不同的API
      const apiQuery = {
        ...query,
        page: pagination.value.page,
        pageSize: pagination.value.pageSize,
        ...searchFilters.value
      }

      console.log(`📡 API 查询参数:`, apiQuery)

      let response: { success: boolean; data: PageData<School>; message?: string }
      
      if (currentType.value === 'primary') {
        console.log(`🏫 调用小学 API`)
        response = await schoolApi.getPrimaryList(apiQuery)
      } else {
        console.log(`🏫 调用中学 API`)
        response = await schoolApi.getSecondaryList(apiQuery)
      }
      
      if (response.success) {
        console.log(`✅ API 响应成功:`, {
          listLength: response.data.list.length,
          page: response.data.page,
          total: response.data.total,
          totalPages: response.data.totalPages
        })
        schools.value = response.data.list
        pagination.value = {
          page: response.data.page,
          pageSize: response.data.pageSize,
          total: response.data.total,
          totalPages: response.data.totalPages
        }
      } else {
        throw new Error(response.message || '获取学校列表失败')
      }
    } catch (err) {
      console.error('获取学校列表失败:', err)
      error.value = err instanceof Error ? err.message : '获取学校列表失败'
      
      // 失败时回退到Mock数据
      schools.value = mockSchools
      pagination.value = {
        page: 1,
        pageSize: 20,
        total: mockSchools.filter(school => school.type === currentType.value).length,
        totalPages: Math.ceil(mockSchools.filter(school => school.type === currentType.value).length / 20)
      }
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
    pagination.value.page = 1 // 重置到第一页
    searchKeyword.value = '' // 清空搜索
    await fetchSchools()
  }

  /**
   * 搜索学校
   */
  const searchSchools = async (keyword: string, query: PageQuery = {}) => {
    searchKeyword.value = keyword
    pagination.value.page = 1 // 重置到第一页

    if (enableMock.value) {
      // Mock模式：本地搜索
      const filtered = mockSchools.filter(school => 
        school.type === currentType.value && (
          school.name.includes(keyword) || 
          school.district.includes(keyword) ||
          school.address?.includes(keyword)
        )
      )
      schools.value = filtered
      pagination.value = {
        page: 1,
        pageSize: 20,
        total: filtered.length,
        totalPages: Math.ceil(filtered.length / 20)
      }
      return
    }

    try {
      loading.value = true
      error.value = null

      const apiQuery = {
        ...query,
        keyword,
        page: pagination.value.page,
        pageSize: pagination.value.pageSize,
        ...searchFilters.value
      }

      let response: { success: boolean; data: PageData<School>; message?: string }
      
      if (currentType.value === 'primary') {
        response = await schoolApi.searchPrimary(keyword, apiQuery)
      } else {
        response = await schoolApi.searchSecondary(keyword, apiQuery)
      }
      
      if (response.success) {
        schools.value = response.data.list
        pagination.value = {
          page: response.data.page,
          pageSize: response.data.pageSize,
          total: response.data.total,
          totalPages: response.data.totalPages
        }
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
   * 设置搜索过滤器
   */
  const setSearchFilters = (filters: Partial<typeof searchFilters.value>) => {
    searchFilters.value = { ...searchFilters.value, ...filters }
    pagination.value.page = 1 // 重置到第一页
  }

  /**
   * 清空搜索
   */
  const clearSearch = async () => {
    searchKeyword.value = ''
    searchFilters.value = {
      category: '',
      district: '',
      applicationStatus: ''
    }
    pagination.value.page = 1
    await fetchSchools()
  }

  /**
   * 翻页
   */
  const goToPage = async (page: number) => {
    if (page < 1 || page > pagination.value.totalPages) return
    
    console.log(`🔄 翻页到第 ${page} 页`)
    pagination.value.page = page
    
    if (searchKeyword.value) {
      console.log(`🔍 搜索模式：搜索关键词 "${searchKeyword.value}"`)
      await searchSchools(searchKeyword.value)
    } else {
      console.log(`📋 列表模式：获取学校列表`)
      await fetchSchools()
    }
  }

  /**
   * 设置页面大小
   */
  const setPageSize = async (pageSize: number) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1 // 重置到第一页
    
    if (searchKeyword.value) {
      await searchSchools(searchKeyword.value)
    } else {
      await fetchSchools()
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
    pagination,
    searchKeyword,
    searchFilters,
    
    // 计算属性
    filteredSchools,
    isLoading,
    hasError,
    hasSearchResults,
    currentPageData,
    
    // Actions
    fetchSchools,
    updateStats,
    setSchoolType,
    searchSchools,
    setSearchFilters,
    clearSearch,
    goToPage,
    setPageSize,
    clearError,
    toggleMockMode
  }
}) 