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
  
  // 无限滚动状态
  const hasMore = ref(true)
  const loadingMore = ref(false)
  const allSchools = ref<School[]>([]) // 存储所有已加载的学校数据
  
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
  
  // 当前页面数据 - 使用 allSchools.value 显示所有已加载的数据
  const currentPageData = computed(() => {
    return allSchools.value
  })
  
  // 是否还有更多数据
  const hasMoreData = computed(() => hasMore.value)
  
  // 是否正在加载更多
  const isLoadingMore = computed(() => loadingMore.value)

  // Actions
  
  /**
   * 获取学校列表（支持无限滚动）
   */
  const fetchSchools = async (query: PageQuery = {}, append: boolean = false) => {
    if (enableMock.value) {
      // Mock模式：使用静态数据
      const filteredSchools = mockSchools.filter(school => school.type === currentType.value)
      if (append) {
        allSchools.value = [...allSchools.value, ...filteredSchools]
      } else {
        allSchools.value = filteredSchools
        schools.value = filteredSchools
      }
      pagination.value = {
        page: 1,
        pageSize: 20,
        total: filteredSchools.length,
        totalPages: Math.ceil(filteredSchools.length / 20)
      }
      hasMore.value = false // Mock模式下没有更多数据
      await updateStats()
      return
    }

    try {
      if (append) {
        loadingMore.value = true
      } else {
        loading.value = true
      }
      error.value = null

      // 根据学校类型选择不同的API
      const apiQuery = {
        ...query,
        page: append ? pagination.value.page + 1 : pagination.value.page,
        pageSize: pagination.value.pageSize
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
        
        if (append) {
          // 追加数据
          allSchools.value = [...allSchools.value, ...response.data.list]
          pagination.value.page = response.data.page
        } else {
          // 重置数据
          allSchools.value = response.data.list
          schools.value = response.data.list
          pagination.value = {
            page: response.data.page,
            pageSize: response.data.pageSize,
            total: response.data.total,
            totalPages: response.data.totalPages
          }
        }
        
        // 检查是否还有更多数据
        hasMore.value = response.data.page < response.data.totalPages
      } else {
        throw new Error(response.message || '获取学校列表失败')
      }
    } catch (err) {
      console.error('获取学校列表失败:', err)
      error.value = err instanceof Error ? err.message : '获取学校列表失败'
      
      // 失败时回退到Mock数据
      const filteredSchools = mockSchools.filter(school => school.type === currentType.value)
      if (append) {
        allSchools.value = [...allSchools.value, ...filteredSchools]
      } else {
        allSchools.value = filteredSchools
        schools.value = filteredSchools
      }
      pagination.value = {
        page: 1,
        pageSize: 20,
        total: filteredSchools.length,
        totalPages: Math.ceil(filteredSchools.length / 20)
      }
      hasMore.value = false
      console.warn('已回退到Mock数据')
    } finally {
      loading.value = false
      loadingMore.value = false
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
    allSchools.value = [] // 清空所有学校数据
    hasMore.value = true // 重置更多数据状态
    await fetchSchools()
  }

  /**
   * 搜索学校（支持无限滚动）
   */
  const searchSchools = async (keyword: string, query: PageQuery = {}, append: boolean = false) => {
    searchKeyword.value = keyword
    // 只有在没有传入页码参数时才重置到第一页
    if (!query.page && !append) {
      pagination.value.page = 1
      allSchools.value = [] // 清空搜索结果
    }

    if (enableMock.value) {
      // Mock模式：本地搜索
      const filtered = mockSchools.filter(school => 
        school.type === currentType.value && (
          school.name.includes(keyword) || 
          school.district.includes(keyword) ||
          school.address?.includes(keyword)
        )
      )
      
      if (append) {
        allSchools.value = [...allSchools.value, ...filtered]
      } else {
        allSchools.value = filtered
        schools.value = filtered
      }
      
      pagination.value = {
        page: 1,
        pageSize: 20,
        total: filtered.length,
        totalPages: Math.ceil(filtered.length / 20)
      }
      hasMore.value = false // Mock模式下没有更多数据
      return
    }

    try {
      if (append) {
        loadingMore.value = true
      } else {
        loading.value = true
      }
      error.value = null

      const apiQuery = {
        ...query,
        keyword,
        page: append ? pagination.value.page + 1 : pagination.value.page,
        pageSize: pagination.value.pageSize
      }

      let response: { success: boolean; data: PageData<School>; message?: string }
      
      if (currentType.value === 'primary') {
        response = await schoolApi.searchPrimary(keyword, apiQuery)
      } else {
        response = await schoolApi.searchSecondary(keyword, apiQuery)
      }
      
      if (response.success) {
        if (append) {
          // 追加搜索结果
          allSchools.value = [...allSchools.value, ...response.data.list]
          pagination.value.page = response.data.page
        } else {
          // 重置搜索结果
          allSchools.value = response.data.list
          schools.value = response.data.list
          pagination.value = {
            page: response.data.page,
            pageSize: response.data.pageSize,
            total: response.data.total,
            totalPages: response.data.totalPages
          }
        }
        
        // 检查是否还有更多数据
        hasMore.value = response.data.page < response.data.totalPages
      } else {
        throw new Error(response.message || '搜索失败')
      }
    } catch (err) {
      console.error('搜索学校失败:', err)
      error.value = err instanceof Error ? err.message : '搜索失败'
    } finally {
      loading.value = false
      loadingMore.value = false
    }
  }

  /**
   * 清空搜索
   */
  const clearSearch = async () => {
    searchKeyword.value = ''
    pagination.value.page = 1
    allSchools.value = [] // 清空所有学校数据
    hasMore.value = true // 重置更多数据状态
    await fetchSchools()
  }

  /**
   * 加载更多数据（无限滚动）
   */
  const loadMore = async () => {
    if (!hasMore.value || loadingMore.value) return
    
    console.log(`📄 加载更多数据，当前页: ${pagination.value.page}`)
    
    if (searchKeyword.value) {
      console.log(`🔍 搜索模式：加载更多搜索结果`)
      await searchSchools(searchKeyword.value, {}, true)
    } else {
      console.log(`📋 列表模式：加载更多学校列表`)
      await fetchSchools({}, true)
    }
  }

  // 移除setPageSize方法，使用固定的页面大小20

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
    allSchools,
    hasMore,
    loadingMore,
    
    // 计算属性
    filteredSchools,
    isLoading,
    hasError,
    hasSearchResults,
    currentPageData,
    hasMoreData,
    isLoadingMore,
    
    // Actions
    fetchSchools,
    updateStats,
    setSchoolType,
    searchSchools,
    clearSearch,
    loadMore,
    clearError,
    toggleMockMode
  }
}) 