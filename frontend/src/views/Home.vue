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
        <div class="search-bar">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索学校名称、地区、地址、分类、宗教、校网等..."
            class="search-input"
            @keyup.enter="handleSearch"
            @input="handleSearchInput"
          />
          <button 
            class="search-btn"
            @click="handleSearch"
            :disabled="isLoading"
          >
            搜索
          </button>
          <button 
            v-if="hasSearchResults"
            class="clear-btn"
            @click="handleClearSearch"
            :disabled="isLoading"
          >
            清空
          </button>
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
            <span class="results-count">
              共找到 {{ pagination.total }} 所学校
              <span v-if="hasSearchResults">（搜索"{{ searchKeyword }}"）</span>
            </span>
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
          
          <!-- 学校卡片列表 -->
          <div class="schools-grid">
            <SchoolCard 
              v-for="school in currentPageData" 
              :key="school.id"
              :school="school"
            />
          </div>
          
          <!-- 分页组件 -->
          <div v-if="pagination.totalPages > 1" class="pagination">
            <button 
              class="page-btn"
              :disabled="pagination.page === 1 || isLoading"
              @click="handlePageChange(pagination.page - 1)"
            >
              上一页
            </button>
            
            <div class="page-numbers">
              <button
                v-for="page in visiblePages"
                :key="page"
                :class="['page-number', { active: page === pagination.page }]"
                :disabled="isLoading"
                @click="handlePageChange(page)"
              >
                {{ page }}
              </button>
            </div>
            
            <button 
              class="page-btn"
              :disabled="pagination.page === pagination.totalPages || isLoading"
              @click="handlePageChange(pagination.page + 1)"
            >
              下一页
            </button>
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
  currentPageData
} = storeToRefs(schoolStore)
const { 
  setSchoolType, 
  fetchSchools, 
  clearError, 
  searchSchools, 
  clearSearch, 
  goToPage, 
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

// 处理搜索
const handleSearch = async () => {
  if (searchKeyword.value.trim()) {
    await searchSchools(searchKeyword.value.trim())
  } else {
    await clearSearch()
  }
}

// 处理实时搜索输入
let searchTimeout: NodeJS.Timeout | null = null
const handleSearchInput = () => {
  // 清除之前的定时器
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  // 设置新的定时器，延迟500ms执行搜索
  searchTimeout = setTimeout(async () => {
    if (searchKeyword.value.trim()) {
      await searchSchools(searchKeyword.value.trim())
    } else {
      await clearSearch()
    }
  }, 500)
}

// 处理清空搜索
const handleClearSearch = async () => {
  // 清除定时器
  if (searchTimeout) {
    clearTimeout(searchTimeout)
    searchTimeout = null
  }
  await clearSearch()
}

// 处理翻页
const handlePageChange = async (page: number) => {
  if (typeof page === 'number') {
    await goToPage(page)
  }
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

/* 搜索和过滤样式 */
.search-section {
  margin-bottom: 32px;
  padding: 24px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.search-btn, .clear-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn {
  background-color: #3b82f6;
  color: white;
}

.search-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.clear-btn {
  background-color: #6b7280;
  color: white;
}

.clear-btn:hover:not(:disabled) {
  background-color: #4b5563;
}

.search-btn:disabled, .clear-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  font-size: 16px;
  color: #374151;
  font-weight: 500;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-size-selector label {
  font-size: 14px;
  color: #6b7280;
}

.page-size-select {
  padding: 4px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
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

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 32px;
  padding: 20px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-number {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 40px;
  text-align: center;
}

.page-number:hover:not(:disabled) {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.page-number.active {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.page-number:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

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
  
  .search-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .results-info {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .schools-grid {
    grid-template-columns: 1fr;
  }
  
  .pagination {
    flex-wrap: wrap;
    gap: 4px;
  }
}
</style> 