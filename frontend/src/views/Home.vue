<template>
  <div class="home">
    <!-- 顶部横幅图片 -->
    <div class="hero-section">
      <img 
        src="https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=800&h=300&fit=crop" 
        alt="香港学校建筑" 
        class="hero-image"
      />
    </div>

    <div class="container">
      <!-- 顶部工具栏 -->
      <div class="top-toolbar">
        <div class="toolbar-left">
          <!-- 语言切换器 -->
          <LanguageSwitcher />
        </div>
        <div class="toolbar-right">
          <!-- 可以添加其他工具按钮 -->
        </div>
      </div>

      <!-- 搜索和类型选择统一区域 -->
      <div class="search-type-section">
        <!-- 搜索框 -->
        <div class="search-container">
          <div class="search-input-wrapper">
            <input
              v-model="searchKeyword"
              type="text"
              :placeholder="getText('search.placeholder')"
              class="search-input"
              @input="handleSearchInput"
              @focus="handleSearchFocus"
              @blur="handleSearchBlur"
            />
            <div 
              v-if="searchKeyword && !isLoading"
              class="clear-icon"
              @click="handleClearSearch"
              title="清空搜索"
            >
              ✕
            </div>
            <div 
              v-if="isLoading"
              class="loading-icon"
            >
              <div class="spinner"></div>
            </div>
          </div>
        </div>

        <!-- 学校类型选择和统计信息 -->
        <div class="type-selector">
          <div class="type-buttons">
            <button 
              :class="['type-btn', { active: currentType === 'primary' }]"
              :disabled="isLoading"
              @click="handleTypeChange('primary')"
            >
              {{ getText('school.primary') }}
            </button>
            <button 
              :class="['type-btn', { active: currentType === 'secondary' }]"
              :disabled="isLoading"
              @click="handleTypeChange('secondary')"
            >
              {{ getText('school.secondary') }}
            </button>
          </div>
          <!-- 统计信息 -->
          <div class="stats-text">
            <span class="stats-item">
              <span class="stats-number">{{ stats.totalSchools }}</span>
              <span class="stats-label">{{ getText('school.schools') }}</span>
            </span>
            <span class="stats-divider">|</span>
            <span class="stats-item">
              <span class="stats-number">{{ stats.openApplications }}</span>
              <span class="stats-label">{{ getText('school.openApplications') }}</span>
            </span>
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
        <div v-if="filteredSchools.length === 0" class="empty-state">
          <div class="empty-icon">📚</div>
          <h3>暂无学校信息</h3>
          <p>{{ hasSearchResults ? '没有找到匹配的学校' : '当前类型下没有找到学校数据' }}</p>
        </div>
        <div v-else>          
          <!-- 学校卡片列表 -->
          <div class="schools-grid">
            <SchoolCard 
              v-for="school in currentPageData" 
              :key="school.id"
              :school="school"
              @click="handleSchoolClick"
            />
          </div>
          
          <!-- 加载状态指示器 -->
          <div v-if="isLoadingMore" class="loading-indicator">
            <div class="loading-spinner-small"></div>
            <span>正在加载更多...</span>
          </div>
          
          <!-- 没有更多数据提示 -->
          <div v-else-if="!hasMoreData && currentPageData.length > 0">
            <div>📚</div>
            <p>已加载全部 {{ pagination.total }} 所学校</p>
          </div>
          
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
  isLoadingMore
} = storeToRefs(schoolStore)
const { 
  setSchoolType, 
  fetchSchools, 
  clearError, 
  searchSchools, 
  clearSearch, 
  loadMore
} = schoolStore

// 移除本地状态，使用store中的固定页面大小

// 移除分页相关计算属性，使用无限滚动

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

// 组件挂载时获取数据并添加滚动监听
onMounted(async () => {
  // 初始化语言设置
  languageStore.initLanguage()
  
  await fetchSchools()
  window.addEventListener('scroll', handleScroll)
})

// 组件卸载时移除滚动监听
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
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
  }, 300) // 延迟清空，让动画完成
}

// 处理实时搜索输入
let searchTimeout: ReturnType<typeof setTimeout> | null = null
const handleSearchInput = () => {
  // 清除之前的定时器
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  // 设置新的定时器，延迟800ms执行搜索（增加延迟，避免频繁搜索）
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
  // 清除定时器
  if (searchTimeout) {
    clearTimeout(searchTimeout)
    searchTimeout = null
  }
  searchKeyword.value = ''
  await clearSearch()
}

// 移除手动加载更多方法，改为自动滚动加载

// 移除页面大小变化处理，使用固定页面大小

// 重新加载数据
const handleRetry = async () => {
  clearError()
  await fetchSchools()
}
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.top-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  margin-bottom: 20px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.hero-section {
  width: 100%;
  height: 200px;
  overflow: hidden;
  margin-bottom: 20px;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.type-selector {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
  background-color: transparent;
  border-radius: 0;
  box-shadow: none;
}

.type-buttons {
  display: flex;
  gap: 12px;
  position: relative;
}

.type-btn {
  padding: 8px 20px;
  border: 2px solid #e5e7eb;
  background-color: white;
  color: #6b7280;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 600;
  position: relative;
  z-index: 1;
}

.type-btn:hover:not(:disabled) {
  border-color: #3b82f6;
  color: #3b82f6;
  background-color: #f8fafc;
}

.type-btn.active {
  background-color: white;
  color: #3b82f6;
  border-color: #3b82f6;
  z-index: 2;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.type-btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.type-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 统计信息样式 */
.stats-text {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #6b7280;
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stats-number {
  font-weight: 700;
  color: #1f2937;
  font-size: 16px;
}

.stats-label {
  color: #6b7280;
  font-size: 14px;
}

.stats-divider {
  color: #d1d5db;
  font-weight: 300;
}


/* 移除统计模块样式，统计信息已移到类型选择器内 */

.mock-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
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

.loading-state {
  text-align: center;
  padding: 40px 20px;
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

.error-state {
  text-align: center;
  padding: 40px 20px;
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

/* 搜索和类型选择统一区域样式 */
.search-type-section {
  margin-bottom: 24px;
  padding: 20px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-container {
  display: flex;
  justify-content: center;
}

.search-input-wrapper {
  position: relative;
  width: 100%;
  max-width: 500px;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  font-size: 14px;
  background-color: #f9fafb;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  background-color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  transform: translateY(-1px);
}

.search-input::placeholder {
  color: #9ca3af;
  font-weight: 400;
}

.clear-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e5e7eb;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  font-weight: bold;
  color: #6b7280;
}

.clear-icon:hover {
  background-color: #dc2626;
  color: white;
  transform: translateY(-50%) scale(1.1);
}

.loading-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 移除过滤样式，因为不再需要 */

/* 结果信息样式 */
.results-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background-color: #f9fafb;
  border-radius: 8px;
}

.results-count {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  color: #374151;
  font-weight: 500;
}

.count-number {
  font-weight: 700;
  color: #1f2937;
  font-size: 20px;
}

.count-label {
  color: #6b7280;
}

.search-keyword {
  padding: 4px 8px;
  background-color: #dbeafe;
  color: #1e40af;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
}

.loaded-count {
  font-size: 14px;
  color: #6b7280;
}

.loaded-number {
  font-weight: 600;
  color: #3b82f6;
}

/* 学校网格样式 */
.schools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.schools-list {
  margin-bottom: 40px;
}

/* 自动滚动加载样式 */
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

/* 移除页面大小选择器样式 */

/* 移除分页相关样式，使用无限滚动 */

@media (max-width: 768px) {
  .container {
    padding: 0 12px;
  }
  
  .type-selector {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .type-buttons {
    justify-content: center;
    gap: 8px;
  }
  
  .type-btn {
    flex: 1;
    padding: 10px 16px;
    font-size: 14px;
    min-width: 0;
  }
  
  .stats-text {
    justify-content: center;
    font-size: 13px;
  }
  
  .stats-number {
    font-size: 15px;
  }
  
  .search-type-section {
    padding: 16px;
    gap: 12px;
  }
  
  .search-container {
    padding: 0;
  }
  
  .search-input-wrapper {
    max-width: 100%;
  }
  
  .search-input {
    padding: 14px 44px 14px 18px;
    font-size: 16px; /* 防止iOS缩放 */
  }
  
  .clear-icon {
    right: 14px;
    width: 22px;
    height: 22px;
    font-size: 12px;
  }
  
  .loading-icon {
    right: 14px;
  }
  
  .spinner {
    width: 14px;
    height: 14px;
  }
  
  .results-info {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  /* 移除页面大小选择器移动端样式 */
  
  .schools-grid {
    grid-template-columns: 1fr;
  }
  
  .load-more-btn {
    padding: 10px 24px;
    font-size: 14px;
  }
  
  .no-more-data {
    padding: 30px 16px;
  }
  
  .no-more-icon {
    font-size: 36px;
  }
  
  .no-more-data p {
    font-size: 14px;
  }
}
</style> 