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
      <!-- 学校类型选择 -->
      <div class="type-selector">
        <button 
          :class="['type-btn', { active: currentType === 'primary' }]"
          :disabled="isLoading"
          @click="handleTypeChange('primary')"
        >
          小学
        </button>
        <button 
          :class="['type-btn', { active: currentType === 'secondary' }]"
          :disabled="isLoading"
          @click="handleTypeChange('secondary')"
        >
          中学
        </button>
      </div>

      <!-- 搜索框 -->
      <div class="search-section">
        <div class="search-container">
          <div class="search-input-wrapper">
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="搜索学校名称、地区、地址、分类、宗教、校网等..."
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
      </div>

      <!-- 开发模式指示器 -->
      <div v-if="enableMock" class="mock-indicator">
        <span class="mock-badge">Mock模式</span>
        <span class="mock-text">当前使用模拟数据</span>
      </div>

      <!-- 统计信息 -->
      <div class="stats-section">
        <div class="stat-item">
          <div class="stat-number">{{ stats.totalSchools }}</div>
          <div class="stat-label">所学校</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ stats.openApplications }}</div>
          <div class="stat-label">所开放申请</div>
        </div>
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
          <!-- 结果统计 -->
          <div class="results-info">
            <div class="results-count">
              <span class="count-number">{{ pagination.total }}</span>
              <span class="count-label">所学校</span>
              <span v-if="hasSearchResults" class="search-keyword">
                搜索"{{ searchKeyword }}"
              </span>
            </div>
            <div class="loaded-count">
              已加载 <span class="loaded-number">{{ currentPageData.length }}</span> 所
            </div>
          </div>
          
          <!-- 学校卡片列表 -->
          <div class="schools-grid">
            <SchoolCard 
              v-for="school in currentPageData" 
              :key="school.id"
              :school="school"
            />
          </div>
          
          <!-- 无限滚动加载更多 -->
          <div v-if="hasMoreData" class="load-more-section">
            <button 
              class="load-more-btn"
              :disabled="isLoadingMore"
              @click="handleLoadMore"
            >
              <span v-if="isLoadingMore" class="loading-spinner-small"></span>
              <span v-else>加载更多</span>
            </button>
          </div>
          
          <!-- 没有更多数据提示 -->
          <div v-else-if="currentPageData.length > 0" class="no-more-data">
            <div class="no-more-icon">📚</div>
            <p>已加载全部 {{ pagination.total }} 所学校</p>
          </div>
          
          <!-- 页面大小选择器 -->
          <div class="page-size-section">
            <div class="page-size-selector">
              <label>每页显示：</label>
              <select v-model="pageSize" @change="handlePageSizeChange" class="page-size-select">
                <option :value="10">10</option>
                <option :value="20">20</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useSchoolStore } from '@/stores/school'
import SchoolCard from '@/components/SchoolCard.vue'

const schoolStore = useSchoolStore()
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
  loadMore, 
  setPageSize
} = schoolStore

// 本地状态
const pageSize = ref(20)

// 计算可见的页码
const visiblePages = computed(() => {
  const current = pagination.value.page
  const total = pagination.value.totalPages
  const delta = 2
  const range = []
  const rangeWithDots = []

  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i)
  }

  if (current - delta > 2) {
    rangeWithDots.push(1, '...')
  } else {
    rangeWithDots.push(1)
  }

  rangeWithDots.push(...range)

  if (current + delta < total - 1) {
    rangeWithDots.push('...', total)
  } else if (total > 1) {
    rangeWithDots.push(total)
  }

  return rangeWithDots
})

// 组件挂载时获取数据
onMounted(async () => {
  await fetchSchools()
})

// 处理学校类型切换
const handleTypeChange = async (type: 'primary' | 'secondary') => {
  await setSchoolType(type)
}

// 处理实时搜索输入
let searchTimeout: NodeJS.Timeout | null = null
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

// 处理加载更多
const handleLoadMore = async () => {
  await loadMore()
}

// 处理页面大小变化
const handlePageSizeChange = async () => {
  await setPageSize(pageSize.value)
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
  gap: 16px;
  margin-bottom: 24px;
  justify-content: center;
}

.type-btn {
  flex: 1;
  max-width: 200px;
  padding: 16px 32px;
  border-radius: 16px;
  border: none;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #e5e7eb;
  color: #6b7280;
}

.type-btn.active {
  background-color: white;
  color: #1f2937;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.type-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.stats-section {
  display: flex;
  justify-content: space-around;
  margin-bottom: 32px;
  padding: 24px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 48px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 16px;
  color: #6b7280;
}

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

/* 搜索样式 */
.search-section {
  margin-bottom: 32px;
  padding: 24px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.search-container {
  display: flex;
  justify-content: center;
}

.search-input-wrapper {
  position: relative;
  width: 100%;
  max-width: 600px;
}

.search-input {
  width: 100%;
  padding: 16px 48px 16px 20px;
  border: 2px solid #e5e7eb;
  border-radius: 25px;
  font-size: 16px;
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
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e5e7eb;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
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
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 16px;
  height: 16px;
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

/* 无限滚动样式 */
.load-more-section {
  display: flex;
  justify-content: center;
  margin: 40px 0;
  padding: 20px;
}

.load-more-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 32px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.load-more-btn:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
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

/* 页面大小选择器样式 */
.page-size-section {
  display: flex;
  justify-content: center;
  margin-top: 16px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-size-selector label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.page-size-select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.page-size-select:focus {
  outline: none;
  border-color: #3b82f6;
}

/* 移除分页相关样式，使用无限滚动 */

@media (max-width: 768px) {
  .container {
    padding: 0 12px;
  }
  
  .type-selector {
    gap: 8px;
  }
  
  .type-btn {
    padding: 12px 24px;
    font-size: 16px;
  }
  
  .stat-number {
    font-size: 36px;
  }
  
  .search-container {
    padding: 0 12px;
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
  
  .page-size-section {
    margin-top: 12px;
    padding: 12px;
  }
  
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