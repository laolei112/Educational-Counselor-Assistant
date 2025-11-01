<template>
  <div class="home">
    <!-- Header Section - 渐变背景，带搜索框 -->
    <div class="header-section">
      <div class="header-language-switcher">
        <LanguageSwitcher />
      </div>
      <div class="header-content">
        <h1 class="header-title">{{ getText('app.title') || 'BetterSchool · 香港小学升学数据库' }}</h1>
        <p class="header-subtitle">{{ getText('app.subtitle') || '为您智能匹配最适合孩子的升学路径' }}</p>
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
          <div class="filter-select-wrapper" @click="toggleFilterDropdown('district')">
            <span class="filter-select-trigger">
              {{ filters.district ? languageStore.convertText(filters.district) : getText('filter.allDistrict') }}
            </span>
            <span class="filter-arrow" :class="{ 'is-open': activeFilterDropdown === 'district' }">▼</span>
          </div>
          
          <!-- 小学筛选：校网和学校类别 -->
          <template v-if="currentType === 'primary'">
            <div class="filter-select-wrapper" @click="toggleFilterDropdown('schoolNet')">
              <span class="filter-select-trigger">
                {{ filters.schoolNet ? languageStore.convertText(filters.schoolNet) : getText('filter.allSchoolNet') }}
              </span>
              <span class="filter-arrow" :class="{ 'is-open': activeFilterDropdown === 'schoolNet' }">▼</span>
            </div>
            <div class="filter-select-wrapper" @click="toggleFilterDropdown('category')">
              <span class="filter-select-trigger">
                {{ filters.category ? languageStore.convertText(filters.category) : getText('filter.allCategory') }}
              </span>
              <span class="filter-arrow" :class="{ 'is-open': activeFilterDropdown === 'category' }">▼</span>
            </div>
          </template>
          
          <!-- 中学筛选：Banding -->
          <template v-else>
            <div class="filter-select-wrapper" @click="toggleFilterDropdown('banding')">
              <span class="filter-select-trigger">
                {{ filters.banding ? languageStore.convertText(filters.banding) : getText('filter.allBanding') }}
              </span>
              <span class="filter-arrow" :class="{ 'is-open': activeFilterDropdown === 'banding' }">▼</span>
            </div>
          </template>
        </div>

        <!-- Mobile Filter Button -->
        <div class="mobile-filter-button">
          <button class="mobile-filter-btn" @click="showMobileFilters = !showMobileFilters">
            <span>筛选与排序</span>
            <span class="filter-icon">⚙</span>
          </button>
        </div>

        <!-- 统计信息 -->
        <div class="stats-info">
          <span class="stats-text">共 {{ filteredSchools.length }} 所学校</span>
        </div>
      </div>

      <!-- 下拉菜单 -->
      <div v-if="activeFilterDropdown" class="filter-dropdown-menu" :class="{ 'is-open': activeFilterDropdown }">
        <!-- 片区下拉 -->
        <div v-if="activeFilterDropdown === 'district'" class="filter-dropdown-content">
          <div
            class="filter-dropdown-item"
            :class="{ active: filters.district === '' }"
            @click="selectFilter('district', '')"
          >
            {{ getText('filter.allDistrict') }}
          </div>
          <div
            v-for="district in filterOptions.districts"
            :key="district"
            class="filter-dropdown-item"
            :class="{ active: filters.district === district }"
            @click="selectFilter('district', district)"
          >
            {{ languageStore.convertText(district) }}
          </div>
        </div>
        
        <!-- 校网下拉（仅小学） -->
        <div v-if="activeFilterDropdown === 'schoolNet' && currentType === 'primary'" class="filter-dropdown-content">
          <div
            class="filter-dropdown-item"
            :class="{ active: filters.schoolNet === '' }"
            @click="selectFilter('schoolNet', '')"
          >
            {{ getText('filter.allSchoolNet') }}
          </div>
          <div
            v-for="net in filterOptions.schoolNets"
            :key="net"
            class="filter-dropdown-item"
            :class="{ active: filters.schoolNet === net }"
            @click="selectFilter('schoolNet', net)"
          >
            {{ languageStore.convertText(net) }}
          </div>
        </div>
        
        <!-- 学校类别下拉（仅小学） -->
        <div v-if="activeFilterDropdown === 'category' && currentType === 'primary'" class="filter-dropdown-content">
          <div
            class="filter-dropdown-item"
            :class="{ active: filters.category === '' }"
            @click="selectFilter('category', '')"
          >
            {{ getText('filter.allCategory') }}
          </div>
          <div
            v-for="cat in filterOptions.categories"
            :key="cat"
            class="filter-dropdown-item"
            :class="{ active: filters.category === cat }"
            @click="selectFilter('category', cat)"
          >
            {{ languageStore.convertText(cat) }}
          </div>
        </div>
        
        <!-- Banding下拉（仅中学） -->
        <div v-if="activeFilterDropdown === 'banding' && currentType === 'secondary'" class="filter-dropdown-content">
          <div
            class="filter-dropdown-item"
            :class="{ active: filters.banding === '' }"
            @click="selectFilter('banding', '')"
          >
            {{ getText('filter.allBanding') }}
          </div>
          <div
            v-for="banding in filterOptions.bandings"
            :key="banding"
            class="filter-dropdown-item"
            :class="{ active: filters.banding === banding }"
            @click="selectFilter('banding', banding)"
          >
            {{ languageStore.convertText(banding) }}
          </div>
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
        <div v-if="filteredSchools.length === 0" class="empty-state">
          <div class="empty-icon">📚</div>
          <h3>暂无学校信息</h3>
          <p>{{ hasSearchResults ? '没有找到匹配的学校' : '当前类型下没有找到学校数据' }}</p>
        </div>
        <div v-else class="schools-grid">
          <SchoolCard 
            v-for="school in currentPageData" 
            :key="school.id"
            :school="school"
            @click="handleSchoolClick"
            class="school-card-item"
          />
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
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useSchoolStore } from '@/stores/school'
import { useLanguageStore } from '@/stores/language'
import SchoolCard from '@/components/SchoolCard.vue'
import SchoolDetailModal from '@/components/SchoolDetailModal.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import type { School } from '@/types/school'

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

// 滚动加载相关
let isLoadingMoreData = false

// 滚动检测函数
const handleScroll = async () => {
  if (isLoadingMoreData || !hasMoreData.value) return
  
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const windowHeight = window.innerHeight
  const documentHeight = document.documentElement.scrollHeight
  
  // 当滚动到距离底部100px时触发加载
  if (scrollTop + windowHeight >= documentHeight - 100) {
    isLoadingMoreData = true
    try {
      await loadMore()
    } finally {
      isLoadingMoreData = false
    }
  }
}

// 活动中的下拉菜单
const activeFilterDropdown = ref<string | null>(null)
const showMobileFilters = ref(false)

// 切换筛选下拉菜单
const toggleFilterDropdown = (type: string) => {
  if (activeFilterDropdown.value === type) {
    activeFilterDropdown.value = null
  } else {
    activeFilterDropdown.value = type
  }
}

// 选择学校类型
const selectSchoolType = async (type: 'primary' | 'secondary') => {
  activeFilterDropdown.value = null
  await handleTypeChange(type)
}

// 选择筛选选项
const selectFilter = async (type: keyof typeof filters.value, value: string) => {
  if (type === 'district') {
    filters.value.district = value
  } else if (type === 'schoolNet') {
    filters.value.schoolNet = value
  } else if (type === 'category') {
    filters.value.category = value
  } else if (type === 'banding') {
    filters.value.banding = value
  }
  
  activeFilterDropdown.value = null
  await handleFilterChange()
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

// 点击外部关闭下拉菜单
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.filter-select-wrapper') && !target.closest('.filter-dropdown-menu') && !target.closest('.header-language-switcher')) {
    activeFilterDropdown.value = null
  }
}

// 组件挂载时获取数据并添加滚动监听
onMounted(async () => {
  // 初始化语言设置
  languageStore.initLanguage()
  
  // 初始化筛选选项
  await initFilters()
  
  await fetchSchools()
  window.addEventListener('scroll', handleScroll)
  document.addEventListener('click', handleClickOutside)
})

// 组件卸载时移除滚动监听
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.removeEventListener('click', handleClickOutside)
  activeFilterDropdown.value = null
})

// 处理学校类型切换
const handleTypeChange = async (type: 'primary' | 'secondary') => {
  await setSchoolType(type)
}

// 处理学校卡片点击
const handleSchoolClick = (school: School) => {
  selectedSchool.value = school
  showDetailModal.value = true
}

// 处理关闭弹窗
const handleCloseModal = () => {
  showDetailModal.value = false
  setTimeout(() => {
    selectedSchool.value = null
  }, 300)
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
  padding: 40px 24px;
  text-align: center;
  position: relative;
}

.header-language-switcher {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
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
  padding: 0 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
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
  padding: 12px 8px;
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
  position: relative;
}

.filter-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.school-type-buttons {
  display: flex;
  gap: 8px;
}

.type-btn {
  padding: 8px 16px;
  border-radius: 9999px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #f3f4f6;
  color: #6b7280;
}

.type-btn.active {
  background-color: #e5e7eb;
  color: #1f2937;
}

.type-btn:hover {
  background-color: #e5e7eb;
}

.desktop-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-select-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  background: white;
  min-width: 120px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.filter-select-wrapper:hover {
  border-color: #3b82f6;
}

.filter-select-trigger {
  flex: 1;
  color: #374151;
}

.filter-arrow {
  font-size: 10px;
  color: #9ca3af;
  transition: transform 0.2s ease;
}

.filter-arrow.is-open {
  transform: rotate(180deg);
}

.mobile-filter-button {
  display: none;
}

.mobile-filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  cursor: pointer;
}

.filter-icon {
  font-size: 16px;
}

.stats-info {
  font-size: 14px;
  color: #6b7280;
}

/* Filter Dropdown Menu */
.filter-dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 16px;
  right: 16px;
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  z-index: 50;
  max-height: 300px;
  overflow-y: auto;
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
    padding: 32px 16px;
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

  .desktop-filters {
    display: none;
  }

  .mobile-filter-button {
    display: block;
    width: 100%;
  }

  .mobile-filter-btn {
    width: 100%;
    justify-content: center;
  }

  .schools-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .filter-dropdown-menu {
    left: 8px;
    right: 8px;
  }
}
</style>
