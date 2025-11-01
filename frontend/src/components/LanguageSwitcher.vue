<template>
  <div class="language-switcher">
    <div 
      class="category-filter-item"
      @click="toggleDropdown"
    >
      <span>{{ languageStore.currentLanguage === 'zh-CN' ? '简' : '繁' }}</span>
      <img
        v-show="isOpen"
        src="https://i.gsxcdn.com/1691866251_48o2a31n.png"
        alt="箭头"
        class="arrow reverse"
      />
      <img
        v-show="!isOpen"
        src="https://i.gsxcdn.com/1691866252_ce958mjj.png"
        alt="箭头"
        class="arrow"
      />
    </div>
    
    <div class="filter-dropdown-menu" v-if="isOpen">
      <div class="filter-dropdown-content">
        <div
          v-for="lang in languages"
          :key="lang.value"
          class="filter-dropdown-item"
          :class="{ active: lang.value === languageStore.currentLanguage }"
          @click="selectLanguage(lang.value)"
        >
          {{ lang.label }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useLanguageStore, type Language } from '@/stores/language'

const languageStore = useLanguageStore()
const isOpen = ref(false)

const languages = [
  { value: 'zh-CN' as Language, label: '简' },
  { value: 'zh-TW' as Language, label: '繁' }
]

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const selectLanguage = (lang: Language) => {
  languageStore.setLanguage(lang)
  isOpen.value = false
}

const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.language-switcher')) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.language-switcher {
  position: relative;
  display: inline-block;
}

.category-filter-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  border: none;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  user-select: none;
  border-radius: 4px;
}

.category-filter-item:hover {
  color: #374151;
  background-color: rgba(255, 255, 255, 1);
}

.category-filter-item span {
  flex: 1;
}

.category-filter-item .arrow {
  width: 12px;
  height: 8px;
  transition: all 0.2s ease;
}

.category-filter-item .arrow.reverse {
  transform: rotate(180deg);
}

.filter-dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  z-index: 50;
  min-width: 80px;
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

/* 移动端适配 */
@media (max-width: 768px) {
  .category-filter-item {
    padding: 4px 6px;
    font-size: 13px;
  }
  
  .filter-dropdown-item {
    padding: 8px 12px;
    font-size: 13px;
  }
}
</style>
