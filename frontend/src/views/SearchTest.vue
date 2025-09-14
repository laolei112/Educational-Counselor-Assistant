<template>
  <div class="search-test">
    <h1>搜索功能测试</h1>
    
    <div class="test-section">
      <h2>搜索测试</h2>
      <div class="search-bar">
        <input
          v-model="testKeyword"
          type="text"
          placeholder="输入搜索关键词..."
          class="search-input"
          @keyup.enter="testSearch"
        />
        <button @click="testSearch" :disabled="isLoading" class="search-btn">
          搜索
        </button>
        <button @click="clearTest" class="clear-btn">
          清空
        </button>
      </div>
    </div>

    <div class="test-section">
      <h2>快速测试</h2>
      <div class="quick-tests">
        <button @click="testSearchBy('圣保罗')" :disabled="isLoading">搜索"圣保罗"</button>
        <button @click="testSearchBy('中西区')" :disabled="isLoading">搜索"中西区"</button>
        <button @click="testSearchBy('精英')" :disabled="isLoading">搜索"精英"</button>
        <button @click="testSearchBy('天主教')" :disabled="isLoading">搜索"天主教"</button>
        <button @click="testSearchBy('校网11')" :disabled="isLoading">搜索"校网11"</button>
        <button @click="testSearchBy('直资')" :disabled="isLoading">搜索"直资"</button>
      </div>
    </div>

    <div class="test-section">
      <h2>搜索结果</h2>
      <div class="results-info">
        <p><strong>搜索关键词:</strong> {{ testKeyword || '无' }}</p>
        <p><strong>结果数量:</strong> {{ searchResults.length }}</p>
        <p><strong>当前页:</strong> {{ pagination.page }} / {{ pagination.totalPages }}</p>
        <p><strong>总记录数:</strong> {{ pagination.total }}</p>
      </div>
      
      <div v-if="searchResults.length === 0" class="no-results">
        没有找到匹配的结果
      </div>
      <div v-else class="results-list">
        <div v-for="school in searchResults" :key="school.id" class="result-item">
          <h3>{{ school.name }}</h3>
          <p><strong>地区:</strong> {{ school.district }}</p>
          <p><strong>分类:</strong> {{ school.category }}</p>
          <p><strong>宗教:</strong> {{ school.religion || '无' }}</p>
          <p><strong>校网:</strong> {{ school.schoolNet || '无' }}</p>
          <p><strong>地址:</strong> {{ school.address || '无' }}</p>
          <p><strong>备注:</strong> {{ school.remarks || '无' }}</p>
        </div>
      </div>
    </div>

    <div class="test-section">
      <h2>分页测试</h2>
      <div v-if="pagination.totalPages > 1" class="pagination">
        <button 
          @click="handleGoToPage(pagination.page - 1)"
          :disabled="pagination.page === 1 || isLoading"
          class="page-btn"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ pagination.page }} 页，共 {{ pagination.totalPages }} 页
        </span>
        <button 
          @click="handleGoToPage(pagination.page + 1)"
          :disabled="pagination.page === pagination.totalPages || isLoading"
          class="page-btn"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSchoolStore } from '@/stores/school'

const schoolStore = useSchoolStore()
const { 
  pagination, 
  isLoading, 
  currentPageData 
} = storeToRefs(schoolStore)
const { 
  searchSchools, 
  clearSearch, 
  goToPage 
} = schoolStore

const testKeyword = ref('')
const searchResults = ref([])

// 测试搜索
const testSearch = async () => {
  if (testKeyword.value.trim()) {
    console.log(`🔍 测试搜索: "${testKeyword.value}"`)
    await searchSchools(testKeyword.value.trim())
    searchResults.value = currentPageData.value
  } else {
    await clearTest()
  }
}

// 快速测试搜索
const testSearchBy = async (keyword: string) => {
  testKeyword.value = keyword
  await testSearch()
}

// 清空测试
const clearTest = async () => {
  testKeyword.value = ''
  await clearSearch()
  searchResults.value = []
}

// 翻页
const handleGoToPage = async (page: number) => {
  if (typeof page === 'number' && page >= 1 && page <= pagination.value.totalPages) {
    await schoolStore.goToPage(page)
    searchResults.value = currentPageData.value
  }
}

onMounted(() => {
  console.log('🧪 搜索测试页面已加载')
})
</script>

<style scoped>
.search-test {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.test-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
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

.quick-tests {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-tests button {
  padding: 8px 16px;
  background-color: #e9ecef;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-tests button:hover:not(:disabled) {
  background-color: #dee2e6;
}

.quick-tests button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.results-info {
  background: #e8f4fd;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.results-info p {
  margin: 5px 0;
  color: #0c5460;
}

.no-results {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 40px;
}

.results-list {
  max-height: 500px;
  overflow-y: auto;
}

.result-item {
  background: white;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 10px;
  border: 1px solid #dee2e6;
}

.result-item h3 {
  margin: 0 0 10px 0;
  color: #212529;
}

.result-item p {
  margin: 5px 0;
  color: #6c757d;
  font-size: 14px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.page-btn {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.page-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.page-info {
  color: #495057;
  font-weight: 500;
}
</style>
