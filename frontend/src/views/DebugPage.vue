<template>
  <div class="debug-page">
    <h1>分页调试页面</h1>
    
    <div class="debug-info">
      <h2>当前状态</h2>
      <div class="info-item">
        <strong>学校类型:</strong> {{ currentType }}
      </div>
      <div class="info-item">
        <strong>当前页码:</strong> {{ pagination.page }}
      </div>
      <div class="info-item">
        <strong>页面大小:</strong> {{ pagination.pageSize }}
      </div>
      <div class="info-item">
        <strong>总页数:</strong> {{ pagination.totalPages }}
      </div>
      <div class="info-item">
        <strong>总记录数:</strong> {{ pagination.total }}
      </div>
      <div class="info-item">
        <strong>当前页数据量:</strong> {{ currentPageData.length }}
      </div>
      <div class="info-item">
        <strong>搜索关键词:</strong> {{ searchKeyword || '无' }}
      </div>
      <div class="info-item">
        <strong>加载状态:</strong> {{ isLoading ? '加载中' : '已完成' }}
      </div>
    </div>

    <div class="debug-actions">
      <h2>测试操作</h2>
      <button @click="testPage1" :disabled="isLoading">测试第1页</button>
      <button @click="testPage2" :disabled="isLoading">测试第2页</button>
      <button @click="testPage3" :disabled="isLoading">测试第3页</button>
      <button @click="refreshData" :disabled="isLoading">刷新数据</button>
    </div>

    <div class="debug-data">
      <h2>当前页数据</h2>
      <div v-if="currentPageData.length === 0" class="no-data">
        暂无数据
      </div>
      <div v-else class="data-list">
        <div v-for="school in currentPageData" :key="school.id" class="school-item">
          <strong>{{ school.name }}</strong> - {{ school.district }}
        </div>
      </div>
    </div>

    <div class="debug-logs">
      <h2>控制台日志</h2>
      <p>请打开浏览器开发者工具查看控制台日志</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSchoolStore } from '@/stores/school'

const schoolStore = useSchoolStore()
const { 
  currentType, 
  pagination, 
  searchKeyword, 
  isLoading, 
  currentPageData 
} = storeToRefs(schoolStore)
const { goToPage, fetchSchools } = schoolStore

onMounted(async () => {
  console.log('🐛 调试页面已加载')
  await fetchSchools()
})

const testPage1 = async () => {
  console.log('🧪 测试第1页')
  await goToPage(1)
}

const testPage2 = async () => {
  console.log('🧪 测试第2页')
  await goToPage(2)
}

const testPage3 = async () => {
  console.log('🧪 测试第3页')
  await goToPage(3)
}

const refreshData = async () => {
  console.log('🔄 刷新数据')
  await fetchSchools()
}
</script>

<style scoped>
.debug-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.debug-info {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.info-item {
  margin-bottom: 10px;
  padding: 5px 0;
  border-bottom: 1px solid #ddd;
}

.debug-actions {
  background: #e8f4fd;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.debug-actions button {
  margin-right: 10px;
  margin-bottom: 10px;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.debug-actions button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.debug-data {
  background: #fff3cd;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.no-data {
  color: #856404;
  font-style: italic;
}

.data-list {
  max-height: 300px;
  overflow-y: auto;
}

.school-item {
  padding: 8px 0;
  border-bottom: 1px solid #ffeaa7;
}

.debug-logs {
  background: #d1ecf1;
  padding: 20px;
  border-radius: 8px;
  color: #0c5460;
}
</style>
