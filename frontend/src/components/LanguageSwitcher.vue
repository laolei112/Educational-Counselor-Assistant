<template>
  <div class="language-switcher" :class="{ 'filter-mode': variant === 'filter', 'mobile-mode': variant === 'mobile' }">
    <!-- Mobile 模式：使用按钮组 -->
    <template v-if="variant === 'mobile'">
      <div
        v-for="lang in languages"
        :key="lang.value"
        :class="['language-trigger', variant, { active: lang.value === languageStore.currentLanguage }]"
        @click="selectLanguage(lang.value)"
      >
        {{ lang.label }}
      </div>
    </template>
    
    <!-- Header 和 Filter 模式：使用下拉菜单 -->
    <template v-else>
      <div 
        :class="['language-trigger', variant]"
        @click="toggleDropdown"
      >
        <span>{{ languageStore.currentLanguage === 'zh-CN' ? '简' : '繁' }}</span>
        <span class="arrow" :class="{ 'is-open': isOpen }">▼</span>
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
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useLanguageStore, type Language } from '@/stores/language'

interface Props {
  variant?: 'header' | 'filter' | 'mobile'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'header'
})

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
  // 移动模式不需要关闭下拉菜单（因为没有下拉菜单）
  if (props.variant !== 'mobile') {
    isOpen.value = false
  }
}

const handleClickOutside = (event: Event) => {
  // 移动模式不需要处理点击外部
  if (props.variant === 'mobile') return
  
  const target = event.target as HTMLElement
  if (!target.closest('.language-switcher')) {
    isOpen.value = false
  }
}

onMounted(() => {
  // 只有 header 和 filter 模式才需要监听点击外部
  if (props.variant !== 'mobile') {
    document.addEventListener('click', handleClickOutside)
  }
})

onUnmounted(() => {
  if (props.variant !== 'mobile') {
    document.removeEventListener('click', handleClickOutside)
  }
})
</script>

<style scoped>
.language-switcher {
  position: relative;
  display: inline-block;
}

/* Header 模式 - 原来在 header 的样式 */
.language-trigger.header {
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

.language-trigger.header:hover {
  color: #374151;
  background-color: rgba(255, 255, 255, 1);
}

/* Filter 模式 - 在筛选区域的样式，与其他筛选器一致 */
.language-switcher.filter-mode .language-trigger.filter {
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

.language-switcher.filter-mode .language-trigger.filter:hover {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.language-switcher.filter-mode .language-trigger.filter span:first-child {
  flex: 1;
  color: #374151;
  white-space: nowrap;
}

.language-switcher.filter-mode .arrow {
  font-size: 10px;
  color: #9ca3af;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.language-switcher.filter-mode .arrow.is-open {
  transform: rotate(180deg);
}

/* Mobile 模式 - 在筛选按钮左侧，与中小学切换按钮同一行 */
.language-switcher.mobile-mode {
  display: flex;
  gap: 4px;
  align-items: center;
}

.language-switcher.mobile-mode .language-trigger.mobile {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  background: white;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  white-space: nowrap;
  min-width: 40px;
}

.language-switcher.mobile-mode .language-trigger.mobile:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background-color: #f3f4f6;
}

.language-switcher.mobile-mode .language-trigger.mobile.active {
  background: #e0e7ff;
  border-color: #4f46e5;
  color: #4f46e5;
}

.language-switcher.mobile-mode .arrow {
  display: none;
}

/* 通用样式 */
.language-trigger span:first-child {
  flex: 1;
}

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
}

.language-switcher.filter-mode .filter-dropdown-menu {
  min-width: 120px;
}

/* Mobile 模式不需要下拉菜单 */

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

/* 移动端适配 */
@media (max-width: 768px) {
  .language-trigger.header {
    padding: 4px 6px;
    font-size: 13px;
  }
  
  .filter-dropdown-item {
    padding: 8px 12px;
    font-size: 13px;
  }
}
</style>
