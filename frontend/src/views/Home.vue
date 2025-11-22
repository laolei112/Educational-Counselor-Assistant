<template>
  <div class="home">
    <!-- Header Section - 渐变背景,带搜索框 -->
    <div class="header-section">
      <div class="header-content">
        <h1 class="header-title">{{ getText('app.title') }}</h1>
        <p class="header-subtitle">{{ getText('app.subtitle') }}</p>
        <div class="header-search-wrapper">
          <div class="header-search-icon">🔍</div>
            <input
              v-model="searchKeyword"
              type="text"
              :placeholder="getText('search.placeholder')"
            class="header-search-input"
              @input="handleSearchInput"
              @focus="handleSearchFocus"
              @blur="handleSearchBlur"
            />
            <div 
              v-if="searchKeyword && !isLoading"
            class="header-clear-icon"
              @click="handleClearSearch"
              title="清空搜索"
            >
              ✕
            </div>
            <div 
              v-if="isLoading"
            class="header-loading-icon"
            >
            <div class="spinner-small"></div>
          </div>
            </div>
          </div>
        </div>
        
    <!-- Filter + Sort Section -->
    <div class="filter-section">
      <div class="filter-container">
        <!-- 学校类型切换 + 筛选和排序 -->
        <div class="filter-row">
          <!-- 学校类型切换 -->
          <div class="school-type-buttons">
            <button
              :class="['type-btn', { active: currentType === 'primary' }]"
              @click="selectSchoolType('primary')"
            >
              {{ getText('school.primary') }}
            </button>
            <button
              :class="['type-btn', { active: currentType === 'secondary' }]"
              @click="selectSchoolType('secondary')"
            >
              {{ getText('school.secondary') }}
            </button>
          </div>
          
          <!-- Desktop Filters -->
          <div class="desktop-filters">
            <!-- 片区筛选 -->
          <div class="filter-select-wrapper" @click="toggleFilterDropdown('district', $event)">
            <span class="filter-select-trigger">
              {{ filters.district ? languageStore.convertText(filters.district) : getText('filter.allDistrict') }}
            </span>
            <span class="filter-arrow" :class="{ 'is-open': activeFilterDropdown === 'district' }">▼</span>
            
            <!-- 下拉菜单直接放在wrapper内 -->
            <div v-if="activeFilterDropdown === 'district'" class="filter-dropdown-menu" @click.stop>
              <div class="filter-dropdown-content">
                 <div
                   class="filter-dropdown-item"
                   :class="{ active: filters.district === '' }"
                   @click.stop="selectFilter('district', '', $event)"
                 >
                   {{ getText('filter.allDistrict') }}
            </div>
                 <div
                   v-for="district in filterOptions.districts"
                   :key="district"
                   class="filter-dropdown-item"
                   :class="{ active: filters.district === district }"
                   @click.stop="selectFilter('district', district, $event)"
                 >
                   {{ languageStore.convertText(district) }}
                 </div>
              </div>
            </div>
          </div>
          
          <!-- 小学筛选:校网和学校类别 -->
            <template v-if="currentType === 'primary'">
            <div class="filter-select-wrapper" @click="toggleFilterDropdown('schoolNet', $event)">
              <span class="filter-select-trigger">
                {{ filters.schoolNet ? languageStore.convertText(filters.schoolNet) : getText('filter.allSchoolNet') }}
              </span>
              <span class="filter-arrow" :class="{ 'is-open': activeFilterDropdown === 'schoolNet' }">▼</span>
              
              <div v-if="activeFilterDropdown === 'schoolNet'" class="filter-dropdown-menu" @click.stop>
                <div class="filter-dropdown-content">
                   <div
                     class="filter-dropdown-item"
                     :class="{ active: filters.schoolNet === '' }"
                     @click.stop="selectFilter('schoolNet', '', $event)"
                   >
                     {{ getText('filter.allSchoolNet') }}
              </div>
              <div
                     v-for="net in filterOptions.schoolNets"
                     :key="net"
                     class="filter-dropdown-item"
                     :class="{ active: filters.schoolNet === net }"
                     @click.stop="selectFilter('schoolNet', net, $event)"
                   >
                     {{ languageStore.convertText(net) }}
                   </div>
                </div>
              </div>
            </div>
            
            <div class="filter-select-wrapper" @click="toggleFilterDropdown('category', $event)">
              <span class="filter-select-trigger">
                {{ filters.category ? languageStore.convertText(filters.category) : getText('filter.allCategory') }}
              </span>
              <span class="filter-arrow" :class="{ 'is-open': activeFilterDropdown === 'category' }">▼</span>
              
              <div v-if="activeFilterDropdown === 'category'" class="filter-dropdown-menu" @click.stop>
                <div class="filter-dropdown-content">
                   <div
                     class="filter-dropdown-item"
                     :class="{ active: filters.category === '' }"
                     @click.stop="selectFilter('category', '', $event)"
                   >
                     {{ getText('filter.allCategory') }}
                   </div>
                   <div
                     v-for="cat in filterOptions.categories"
                     :key="cat"
                     class="filter-dropdown-item"
                     :class="{ active: filters.category === cat }"
                     @click.stop="selectFilter('category', cat, $event)"
                   >
                     {{ languageStore.convertText(cat) }}
                   </div>
                </div>
              </div>
              </div>
            </template>
            
          <!-- 中学筛选:Banding -->
            <template v-else>
            <div class="filter-select-wrapper" @click="toggleFilterDropdown('banding', $event)">
              <span class="filter-select-trigger">
                {{ filters.banding ? languageStore.convertText(filters.banding) : getText('filter.allBanding') }}
              </span>
              <span class="filter-arrow" :class="{ 'is-open': activeFilterDropdown === 'banding' }">▼</span>
              
              <div v-if="activeFilterDropdown === 'banding'" class="filter-dropdown-menu" @click.stop>
                <div class="filter-dropdown-content">
                   <div
                     class="filter-dropdown-item"
                     :class="{ active: filters.banding === '' }"
                     @click.stop="selectFilter('banding', '', $event)"
                   >
                     {{ getText('filter.allBanding') }}
              </div>
                   <div
                     v-for="banding in filterOptions.bandings"
                     :key="banding"
                     class="filter-dropdown-item"
                     :class="{ active: filters.banding === banding }"
                     @click.stop="selectFilter('banding', banding, $event)"
                   >
                     {{ languageStore.convertText(banding) }}
          </div>
                </div>
              </div>
            </div>
          </template>
          
          <!-- 排序选择器 -->
          <!-- <div class="filter-select-wrapper" @click="toggleFilterDropdown('sort', $event)">
            <span class="filter-select-trigger">
              {{ sortBy === 'none' ? getText('mobileFilter.sort') : sortBy === 'fee' ? getText('mobileFilter.sortByFee') : getText('mobileFilter.sortByDistrict') }}
            </span>
            <span class="filter-arrow" :class="{ 'is-open': activeFilterDropdown === 'sort' }">▼</span>
            
            <div v-if="activeFilterDropdown === 'sort'" class="filter-dropdown-menu" @click.stop>
              <div class="filter-dropdown-content">
              <div
                class="filter-dropdown-item"
                   :class="{ active: sortBy === 'none' }"
                   @click.stop="selectSort('none', $event)"
              >
                   {{ getText('mobileFilter.sortDefault') }}
              </div>
                 <div
                   class="filter-dropdown-item"
                   :class="{ active: sortBy === 'fee' }"
                   @click.stop="selectSort('fee', $event)"
                 >
                   {{ getText('mobileFilter.sortByFee') }}
            </div>
              <div
                class="filter-dropdown-item"
                   :class="{ active: sortBy === 'district' }"
                   @click.stop="selectSort('district', $event)"
                 >
                   {{ getText('mobileFilter.sortByDistrict') }}
                 </div>
              </div>
            </div>
          </div> -->
          </div>

          <!-- 移动端语言切换器和筛选按钮 -->
          <div class="mobile-actions">
            <div class="mobile-language-switcher">
              <LanguageSwitcher variant="mobile" />
            </div>
            <div class="mobile-filter-button">
              <button class="mobile-filter-btn" @click="showMobileFilters = !showMobileFilters">
                <span>{{ getText('mobileFilter.filterAndSort') }}</span>
                <span class="filter-icon">⚙</span>
              </button>
            </div>
          </div>

          <!-- 桌面端语言切换器和统计信息 -->
          <div class="desktop-actions">
            <div class="desktop-language-switcher">
              <LanguageSwitcher variant="filter" />
            </div>
            <div class="stats-info">
              <span class="stats-text">共 {{ displaySchoolCount }} 所学校</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 移动端筛选面板 -->
    <div v-if="showMobileFilters" class="mobile-filter-overlay" @click="showMobileFilters = false">
      <div class="mobile-filter-panel" @click.stop>
        <div class="mobile-filter-header">
          <h3 class="mobile-filter-title">{{ getText('mobileFilter.title') }}</h3>
          <button class="mobile-filter-close" @click="showMobileFilters = false">✕</button>
        </div>
        
        <div class="mobile-filter-content">
          <!-- 片区筛选 -->
          <div class="mobile-filter-group">
            <label class="mobile-filter-label">{{ getText('mobileFilter.district') }}</label>
            <div class="mobile-filter-options">
              <button
                :class="['mobile-filter-option', { active: filters.district === '' }]"
                @click="selectFilter('district', '')"
              >
                {{ getText('filter.allDistrict') }}
              </button>
              <button
                v-for="district in filterOptions.districts"
                :key="district"
                :class="['mobile-filter-option', { active: filters.district === district }]"
                @click="selectFilter('district', district)"
              >
                {{ languageStore.convertText(district) }}
              </button>
              </div>
            </div>
            
          <!-- 小学筛选：校网和学校类别 -->
          <template v-if="currentType === 'primary'">
            <div class="mobile-filter-group">
              <label class="mobile-filter-label">{{ getText('mobileFilter.schoolNet') }}</label>
              <div class="mobile-filter-options">
                <button
                  :class="['mobile-filter-option', { active: filters.schoolNet === '' }]"
                @click="selectFilter('schoolNet', '')"
              >
                {{ getText('filter.allSchoolNet') }}
                </button>
                <button
                v-for="net in filterOptions.schoolNets"
                :key="net"
                  :class="['mobile-filter-option', { active: filters.schoolNet === net }]"
                @click="selectFilter('schoolNet', net)"
              >
                {{ languageStore.convertText(net) }}
                </button>
              </div>
            </div>
            
            <div class="mobile-filter-group">
              <label class="mobile-filter-label">{{ getText('mobileFilter.category') }}</label>
              <div class="mobile-filter-options">
                <button
                  :class="['mobile-filter-option', { active: filters.category === '' }]"
                @click="selectFilter('category', '')"
              >
                {{ getText('filter.allCategory') }}
                </button>
                <button
                v-for="cat in filterOptions.categories"
                :key="cat"
                  :class="['mobile-filter-option', { active: filters.category === cat }]"
                @click="selectFilter('category', cat)"
              >
                {{ languageStore.convertText(cat) }}
                </button>
              </div>
            </div>
          </template>
          
          <!-- 中学筛选：Banding -->
          <template v-else>
            <div class="mobile-filter-group">
              <label class="mobile-filter-label">{{ getText('mobileFilter.banding') }}</label>
              <div class="mobile-filter-options">
                <button
                  :class="['mobile-filter-option', { active: filters.banding === '' }]"
                @click="selectFilter('banding', '')"
              >
                {{ getText('filter.allBanding') }}
                </button>
                <button
                v-for="banding in filterOptions.bandings"
                :key="banding"
                  :class="['mobile-filter-option', { active: filters.banding === banding }]"
                @click="selectFilter('banding', banding)"
              >
                {{ languageStore.convertText(banding) }}
                </button>
              </div>
            </div>
          </template>
          
          <!-- 排序 -->
          <!-- <div class="mobile-filter-group">
            <label class="mobile-filter-label">{{ getText('mobileFilter.sort') }}</label>
            <div class="mobile-filter-options">
              <button
                :class="['mobile-filter-option', { active: sortBy === 'none' }]"
                @click="selectSort('none')"
              >
                {{ getText('mobileFilter.sortDefault') }}
              </button>
              <button
                :class="['mobile-filter-option', { active: sortBy === 'fee' }]"
                @click="selectSort('fee')"
              >
                {{ getText('mobileFilter.sortByFee') }}
              </button>
              <button
                :class="['mobile-filter-option', { active: sortBy === 'district' }]"
                @click="selectSort('district')"
              >
                {{ getText('mobileFilter.sortByDistrict') }}
              </button>
            </div>
          </div> -->
        </div>
        
        <div class="mobile-filter-footer">
          <button class="mobile-filter-apply-btn" @click="showMobileFilters = false">
            {{ getText('mobileFilter.apply') }}
          </button>
          </div>
        </div>
      </div>

      <!-- 开发模式指示器 -->
      <div v-if="enableMock" class="mock-indicator">
        <span class="mock-badge">Mock模式</span>
        <span class="mock-text">当前使用模拟数据</span>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在加载学校信息...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="hasError" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="handleRetry">重试</button>
      </div>

      <!-- 学校列表 -->
      <div v-else class="schools-list">
      <div class="schools-container">
        <div v-if="currentPageData.length === 0" class="empty-state">
          <div class="empty-icon">📚</div>
          <h3>暂无学校信息</h3>
          <p>{{ hasSearchResults ? '没有找到匹配的学校' : '当前类型下没找到学校数据' }}</p>
        </div>
        <div v-else class="schools-grid">
            <!-- 使用 a 标签包裹，利于 SEO -->
            <a 
              v-for="school in sortedSchools" 
              :key="school.id"
              :href="`/school/${school.type}/${school.id}`"
              class="school-card-link"
              @click.prevent="handleSchoolClick(school)"
            >
              <SchoolCard 
                :school="school"
                class="school-card-item"
              />
            </a>
          </div>
          
          <!-- 加载状态指示器 -->
          <div v-if="isLoadingMore" class="loading-indicator">
            <div class="loading-spinner-small"></div>
            <span>正在加载更多...</span>
          </div>
          
          <!-- 没有更多数据提示 -->
        <div v-else-if="!hasMoreData && currentPageData.length > 0" class="no-more-data">
          <div class="no-more-icon">📚</div>
            <p>已加载全部 {{ pagination.total }} 所学校</p>
        </div>
      </div>
    </div>
    
    <!-- 学校详情弹窗 -->
    <SchoolDetailModal 
      v-if="selectedSchool" 
      :school="selectedSchool" 
      :visible="showDetailModal" 
      @close="handleCloseModal" 
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, computed, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import { useSchoolStore } from '@/stores/school'
import { useLanguageStore } from '@/stores/language'
import SchoolCard from '@/components/SchoolCard.vue'
import SchoolDetailModal from '@/components/SchoolDetailModal.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import type { School } from '@/types/school'
import { rafThrottle } from '@/utils/throttle'

const route = useRoute()
const router = useRouter()
const schoolStore = useSchoolStore()
const languageStore = useLanguageStore()

// 获取多语言文本
const getText = (key: string) => {
  return languageStore.getText(key)
}

const { 
  currentType, 
  filteredSchools, 
  stats, 
  isLoading, 
  hasError, 
  error,
  enableMock,
  pagination,
  searchKeyword,
  hasSearchResults,
  currentPageData,
  hasMoreData,
  isLoadingMore,
  filters,
  filterOptions
} = storeToRefs(schoolStore)

const { 
  setSchoolType, 
  fetchSchools, 
  clearError, 
  searchSchools, 
  clearSearch, 
  loadMore,
  setFilters,
  clearFilters,
  initFilters
} = schoolStore

// 学校详情弹窗相关
const selectedSchool = ref<School | null>(null)
const showDetailModal = ref(false)

// 计算显示的学校总数
// 使用 pagination.total（服务器返回的总数），这代表符合当前筛选和搜索条件的所有学校数量
const displaySchoolCount = computed(() => {
  return pagination.value.total || 0
})

// 滚动加载相关
let isLoadingMoreData = false

// 缓存窗口高度（不会频繁变化，避免重复查询）
let cachedWindowHeight = window.innerHeight

// 监听窗口大小变化，更新缓存的窗口高度
const updateWindowHeight = () => {
  cachedWindowHeight = window.innerHeight
}

// 滚动检测函数 - 优化版本，避免强制重排
const handleScrollInternal = async () => {
  if (isLoadingMoreData || !hasMoreData.value) return
  
  // 使用 requestAnimationFrame 批量读取几何属性，避免强制重排
  requestAnimationFrame(() => {
    // 批量读取所有需要的几何属性，减少重排次数
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop
    const documentHeight = document.documentElement.scrollHeight
    const windowHeight = cachedWindowHeight
    
    // 当滚动到距离底部100px时触发加载
    if (scrollTop + windowHeight >= documentHeight - 100) {
      isLoadingMoreData = true
      loadMore().finally(() => {
        isLoadingMoreData = false
      })
    }
  })
}

// 使用节流优化滚动事件处理
let throttledHandleScroll: ((...args: any[]) => void) | null = null

// 活动中的下拉菜单
const activeFilterDropdown = ref<string | null>(null)
const showMobileFilters = ref(false)
const sortBy = ref<'none' | 'fee' | 'district'>('none')

// 切换筛选下拉菜单
const toggleFilterDropdown = async (type: string, event?: Event) => {
  // 阻止事件冒泡，防止触发外部点击关闭
  if (event) {
    event.stopPropagation()
  }
  
  // 如果点击的是当前已打开的下拉菜单，则关闭它
  // 如果点击的是其他下拉菜单，则切换过去
  if (activeFilterDropdown.value === type) {
    activeFilterDropdown.value = null
  } else {
    // 在打开下拉菜单时，确保filter选项已加载（懒加载）
    await schoolStore.ensureFilterOptions()
    activeFilterDropdown.value = type
  }
}

// 选择学校类型
const selectSchoolType = async (type: 'primary' | 'secondary') => {
  activeFilterDropdown.value = null
  await handleTypeChange(type)
}

// 选择筛选选项 - 直接关闭菜单
const selectFilter = async (type: keyof typeof filters.value, value: string, event?: Event) => {
  // 阻止事件冒泡
  if (event) {
    event.stopPropagation()
  }
  
  if (type === 'district') {
    filters.value.district = value
  } else if (type === 'schoolNet') {
    filters.value.schoolNet = value
  } else if (type === 'category') {
    filters.value.category = value
  } else if (type === 'banding') {
    filters.value.banding = value
  }
  
  // 关闭下拉菜单
  activeFilterDropdown.value = null
  await handleFilterChange()
  
  // 移动端选择后不立即关闭面板，让用户可以看到所有选项
}

// 处理筛选条件变化
const handleFilterChange = async () => {
  await setFilters({
    district: filters.value.district,
    schoolNet: filters.value.schoolNet,
    category: filters.value.category,
    banding: filters.value.banding
  })
}

// 选择排序方式
const selectSort = (sort: 'none' | 'fee' | 'district', event?: Event) => {
  // 阻止事件冒泡
  if (event) {
    event.stopPropagation()
  }
  
  sortBy.value = sort
  activeFilterDropdown.value = null
}

// 排序后的学校列表
const sortedSchools = computed(() => {
  let schools = [...currentPageData.value]
  
  if (sortBy.value === 'fee') {
    schools.sort((a, b) => {
      const aFee = typeof a.tuition === 'number' ? a.tuition : (typeof a.tuition === 'string' ? parseFloat(a.tuition) || 0 : 0)
      const bFee = typeof b.tuition === 'number' ? b.tuition : (typeof b.tuition === 'string' ? parseFloat(b.tuition) || 0 : 0)
      return bFee - aFee // 降序
    })
  } else if (sortBy.value === 'district') {
    schools.sort((a, b) => {
      const aDistrict = a.district ?? ''
      const bDistrict = b.district ?? ''
      return aDistrict.localeCompare(bDistrict)
    })
  }
  
  return schools
})

// 点击外部关闭下拉菜单
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  // 检查点击是否在下拉菜单相关区域外
  if (activeFilterDropdown.value) {
    const isClickInFilterWrapper = target.closest('.filter-select-wrapper')
    const isClickInDropdown = target.closest('.filter-dropdown-menu')
    if (!isClickInFilterWrapper && !isClickInDropdown) {
    activeFilterDropdown.value = null
    }
  }
}

// 组件挂载时获取数据并添加滚动监听
onMounted(async () => {
  // 语言设置已在 store 初始化时自动从 localStorage 加载，无需再次初始化
  
  // 优先加载学校列表，筛选选项延迟加载
  await fetchSchools()
  
  // 延迟初始化筛选选项，避免阻塞关键渲染路径
  initFilters()
  
  // 检查是否有详情页参数
  const { id, type } = route.params
  if (id && type) {
    showDetailModal.value = true
    try {
      // 直接请求详情，不需要等待列表加载
      const detailData = await schoolStore.fetchSchoolDetail(Number(id), type as any)
      selectedSchool.value = detailData
    } catch (error) {
      console.error('获取学校详情失败:', error)
    }
  }

  // 检查是否有 primary 或 secondary 路由
  if (route.name === 'primary') {
    await setSchoolType('primary')
  } else if (route.name === 'secondary') {
    await setSchoolType('secondary')
  }

  // 使用节流优化滚动事件，避免强制重排
  throttledHandleScroll = rafThrottle(handleScrollInternal)
  window.addEventListener('scroll', throttledHandleScroll, { passive: true })
  window.addEventListener('resize', updateWindowHeight, { passive: true })
  document.addEventListener('click', handleClickOutside)
})

// 组件卸载时移除滚动监听
onUnmounted(() => {
  if (throttledHandleScroll) {
    window.removeEventListener('scroll', throttledHandleScroll)
  }
  window.removeEventListener('resize', updateWindowHeight)
  document.removeEventListener('click', handleClickOutside)
  activeFilterDropdown.value = null
})

// 处理学校类型切换
const handleTypeChange = async (type: 'primary' | 'secondary') => {
  await setSchoolType(type)
}

// 处理学校卡片点击 - 路由跳转（SEO友好）
const handleSchoolClick = (school: School) => {
  router.push({
    name: 'school-detail',
    params: { type: school.type, id: school.id }
  })
}

// 监听路由变化处理弹窗
watch(() => route.params, async (newParams, oldParams) => {
  // 检查路由是否是 school-detail
  if (route.name === 'school-detail') {
    const { id, type } = newParams
    
    // 检查ID是否发生变化
    if (id && type && (id !== oldParams?.id || type !== oldParams?.type)) {
      showDetailModal.value = true
      selectedSchool.value = null // 先清空，显示加载状态（如有）
      
      try {
        const detailData = await schoolStore.fetchSchoolDetail(Number(id), type as any)
        selectedSchool.value = detailData
      } catch (error) {
        console.error('获取学校详情失败:', error)
      }
    }
  } else {
    // 如果不是详情页路由，关闭弹窗
    showDetailModal.value = false
    setTimeout(() => {
      if (!showDetailModal.value) {
        selectedSchool.value = null
      }
    }, 300)
  }
}, { deep: true, immediate: true })

// 处理关闭弹窗
const handleCloseModal = () => {
  // 返回列表页（去除URL中的ID）
  router.push({ name: 'home' })
  // showDetailModal 会通过 watch 自动更新，但手动设置可以让交互更即时
  showDetailModal.value = false
}

// 处理实时搜索输入
let searchTimeout: ReturnType<typeof setTimeout> | null = null
const handleSearchInput = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  searchTimeout = setTimeout(async () => {
    if (searchKeyword.value.trim()) {
      await searchSchools(searchKeyword.value.trim())
    } else {
      await clearSearch()
    }
  }, 800)
}

// 处理搜索框获得焦点
const handleSearchFocus = () => {
  // 可以在这里添加一些焦点状态的逻辑
}

// 处理搜索框失去焦点
const handleSearchBlur = () => {
  // 可以在这里添加一些失去焦点状态的逻辑
}

// 处理清空搜索
const handleClearSearch = async () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
    searchTimeout = null
  }
  searchKeyword.value = ''
  await clearSearch()
}

// 重新加载数据
const handleRetry = async () => {
  clearError()
  await fetchSchools()
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background-color: #f9fafb;
}

/* Header Section */
.header-section {
  background: linear-gradient(to right, #2563eb, #60a5fa);
  color: white;
  padding: 40px 24px 60px 24px;
  text-align: center;
  position: relative;
  min-height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.header-content {
  max-width: 800px;
  margin: 0 auto;
}

.header-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
  color: white;
}

.header-subtitle {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 24px;
  color: white;
}

.header-search-wrapper {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  background: white;
  border-radius: 9999px;
  padding: 0 18px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  position: relative;
}

.header-search-icon {
  color: #9ca3af;
  font-size: 20px;
  margin-right: 8px;
}

.header-search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 13px 8px;
  font-size: 14px;
  color: #1f2937;
  background: transparent;
}

.header-search-input::placeholder {
  color: #9ca3af;
}

.header-clear-icon,
.header-loading-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
  color: #6b7280;
}

.header-clear-icon:hover {
  color: #dc2626;
}

.spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Filter Section */
.filter-section {
  background: white;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  padding: 16px;
  position: sticky;
  top: 0;
  z-index: 50;
}

.filter-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  justify-content: space-between; /* 添加这行 */
  position: relative;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  flex: 1;
}

.school-type-buttons {
  display: flex;
  gap: 8px;
}

.mobile-language-switcher {
  display: none;
}

.mobile-actions {
  display: none;
}

.desktop-actions {
  display: flex;
}

.desktop-language-switcher {
  display: block;
}

.type-btn {
  padding: 7px 18px;
  border-radius: 9999px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #f3f4f6;
  color: #6b7280;
}

.type-btn.active {
  background-color: #e0e7ff;
  color: #3b82f6;
}

.type-btn:hover {
  background-color: #e5e7eb;
}

.desktop-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
  flex: 1;
}

.filter-select-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  background: white;
  min-width: 120px;
  font-size: 14px;
  transition: all 0.2s ease;
  user-select: none;
  z-index: 1;
}

.filter-select-wrapper:hover {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-select-trigger {
  flex: 1;
  color: #374151;
  white-space: nowrap;
}

.filter-arrow {
  font-size: 10px;
  color: #9ca3af;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.filter-arrow.is-open {
  transform: rotate(180deg);
}

.mobile-filter-button {
  display: none;
}

.mobile-filter-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.mobile-filter-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.filter-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.stats-info {
  font-size: 14px;
  color: #6b7280;
  white-space: nowrap;
}

.desktop-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  margin-left: auto;
}

.desktop-language-switcher {
  display: block;
  flex-shrink: 0;
}

/* Filter Dropdown Menu - 关键修复 */
.filter-dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 100%;
  min-width: max-content;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
  margin-top: 4px;
}

.filter-dropdown-content {
  padding: 4px 0;
}

.filter-dropdown-item {
  padding: 10px 16px;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  transition: background-color 0.15s ease;
  white-space: nowrap;
}

.filter-dropdown-item:hover {
  background-color: #f3f4f6;
}

.filter-dropdown-item.active {
  background-color: #eff6ff;
  color: #1d4ed8;
  font-weight: 500;
}

/* Mock Indicator */
.mock-indicator {
  max-width: 1200px;
  margin: 16px auto;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  font-size: 14px;
}

.mock-badge {
  background-color: #f59e0b;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.mock-text {
  color: #92400e;
}

/* Loading State */
.loading-state {
  max-width: 1200px;
  margin: 40px auto;
  padding: 40px 20px;
  text-align: center;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #10b981;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  color: #6b7280;
  font-size: 16px;
}

/* Error State */
.error-state {
  max-width: 1200px;
  margin: 40px auto;
  padding: 40px 20px;
  text-align: center;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-state h3 {
  color: #1f2937;
  font-size: 20px;
  margin-bottom: 8px;
}

.error-state p {
  color: #6b7280;
  font-size: 16px;
  margin-bottom: 20px;
}

.retry-btn {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.retry-btn:hover {
  background-color: #059669;
}

/* Schools List */
.schools-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 16px;
}

.schools-container {
  width: 100%;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  color: #1f2937;
  font-size: 20px;
  margin-bottom: 8px;
}

.empty-state p {
  color: #6b7280;
  font-size: 16px;
}

.schools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.school-card-item {
  transition: transform 0.2s ease;
}

.school-card-item:hover {
  transform: scale(1.02);
}

.school-card-link {
  display: block;
  text-decoration: none;
  color: inherit;
  height: 100%;
}

/* Loading Indicator */
.loading-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin: 20px 0;
  padding: 16px;
  color: #6b7280;
  font-size: 14px;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* No More Data */
.no-more-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 40px 0;
  padding: 40px 20px;
  background-color: #f9fafb;
  border-radius: 12px;
  border: 2px dashed #d1d5db;
}

.no-more-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.no-more-data p {
  color: #6b7280;
  font-size: 16px;
  font-weight: 500;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-section {
    padding: 32px 16px 48px 16px;
    min-height: 240px;
  }

  .header-title {
    font-size: 24px;
  }

  .header-subtitle {
    font-size: 12px;
  }

  .filter-container {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-row {
    width: 100%;
  display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: nowrap;
    justify-content: flex-start;
  }

  .school-type-buttons {
    flex-shrink: 0;
    order: 1;
  }

  .desktop-filters {
    display: none;
  }

  .desktop-actions {
    display: none;
  }

  .mobile-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
    order: 2;
    margin-left: auto;
  }
  
  .mobile-language-switcher {
    display: block;
    flex-shrink: 0;
  }

  .mobile-filter-button {
    display: block;
    flex-shrink: 0;
  }
  
  .stats-info {
    display: none;
  }

  .mobile-filter-btn {
    padding: 8px 12px;
    font-size: 13px;
    white-space: nowrap;
  }

  .mobile-filter-btn span:first-child {
    font-size: 13px;
  }

  .schools-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .filter-dropdown-menu {
    left: 0;
    right: 0;
  }
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from .mobile-filter-panel,
.slide-up-leave-to .mobile-filter-panel {
  transform: translateY(100%);
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
}

/* 移动端筛选面板 */
.mobile-filter-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 2000;
  display: none; /* 默认隐藏，在移动端显示 */
  align-items: flex-end;
  animation: fadeIn 0.2s ease;
}

@media (max-width: 768px) {
  .mobile-filter-overlay {
    display: flex;
  }

  .filter-section {
    padding: 12px 16px; /* 减少内边距 */
  }
  
  .filter-container {
    gap: 8px; /* 减小间距 */
  }
  
  .desktop-filters {
    display: none;
  }

  .mobile-filter-button {
    display: block;
    flex-shrink: 0;
  }
  
  .stats-info {
    display: none;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.mobile-filter-panel {
  width: 100%;
  max-height: 80vh;
  background: white;
  border-radius: 20px 20px 0 0;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
  overflow: hidden;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.mobile-filter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.mobile-filter-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.mobile-filter-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.mobile-filter-close:hover {
  background-color: #f3f4f6;
}

.mobile-filter-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.mobile-filter-group {
  margin-bottom: 24px;
}

.mobile-filter-group:last-child {
  margin-bottom: 0;
}

.mobile-filter-label {
  display: block;
    font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
}

.mobile-filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.mobile-filter-option {
  padding: 8px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  background: white;
    font-size: 14px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mobile-filter-option:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.mobile-filter-option.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.mobile-filter-footer {
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  background: white;
}

.mobile-filter-apply-btn {
    width: 100%;
  padding: 14px;
  background: linear-gradient(to right, #2563eb, #60a5fa);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.mobile-filter-apply-btn:hover {
  opacity: 0.9;
}

.mobile-filter-apply-btn:active {
  opacity: 0.8;
}
</style> 