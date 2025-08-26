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
          <p>当前类型下没有找到学校数据</p>
        </div>
        <SchoolCard 
          v-else
          v-for="school in filteredSchools" 
          :key="school.id"
          :school="school"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
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
  enableMock 
} = storeToRefs(schoolStore)
const { setSchoolType, fetchSchools, clearError } = schoolStore

// 组件挂载时获取数据
onMounted(async () => {
  await fetchSchools()
})

// 处理学校类型切换
const handleTypeChange = async (type: 'primary' | 'secondary') => {
  await setSchoolType(type)
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

.schools-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
}
</style> 