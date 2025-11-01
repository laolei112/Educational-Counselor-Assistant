<template>
  <div class="language-switcher" :class="{ 'filter-mode': variant === 'filter', 'mobile-mode': variant === 'mobile', 'header-mode': variant === 'header' }">
    <!-- Toggle 开关实现 -->
    <div 
      class="language-toggle"
      @click="toggleLanguage"
    >
      <div class="toggle-track">
        <div 
          class="toggle-slider"
          :class="{ 'is-traditional': languageStore.currentLanguage === 'zh-TW' }"
        ></div>
        <div class="toggle-options">
          <span 
            class="toggle-option"
            :class="{ active: languageStore.currentLanguage === 'zh-CN' }"
          >简</span>
          <span 
            class="toggle-option"
            :class="{ active: languageStore.currentLanguage === 'zh-TW' }"
          >繁</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useLanguageStore, type Language } from '@/stores/language'

interface Props {
  variant?: 'header' | 'filter' | 'mobile'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'header'
})

const languageStore = useLanguageStore()

const toggleLanguage = () => {
  const newLang: Language = languageStore.currentLanguage === 'zh-CN' ? 'zh-TW' : 'zh-CN'
  languageStore.setLanguage(newLang)
}
</script>

<style scoped>
.language-switcher {
  position: relative;
  display: inline-block;
}

/* Toggle 开关基础样式 */
.language-toggle {
  cursor: pointer;
  user-select: none;
}

.toggle-track {
  position: relative;
  display: flex;
  align-items: center;
  border-radius: 20px;
  background: #e5e7eb;
  transition: all 0.3s ease;
  overflow: hidden;
}

.toggle-slider {
  position: absolute;
  left: 2px;
  width: calc(50% - 4px);
  height: calc(100% - 4px);
  background: white;
  border-radius: 18px;
  transition: transform 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1;
}

.toggle-slider.is-traditional {
  transform: translateX(100%);
}

.toggle-options {
  position: relative;
  display: flex;
  width: 100%;
  z-index: 2;
}

.toggle-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
  transition: color 0.3s ease;
  position: relative;
}

.toggle-option.active {
  color: #374151;
  font-weight: 600;
}

/* Header 模式 */
.language-switcher.header-mode .toggle-track {
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 80px;
  height: 28px;
}

.language-switcher.header-mode .toggle-slider {
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}

.language-switcher.header-mode .toggle-option {
  font-size: 12px;
  padding: 5px 10px;
}

/* Filter 模式 - 桌面版筛选区域 */
.language-switcher.filter-mode .toggle-track {
  border: 1px solid #d1d5db;
  width: 100px;
  height: 32px;
  background: white;
}

.language-switcher.filter-mode .toggle-track:hover {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.language-switcher.filter-mode .toggle-slider {
  background: #e0e7ff;
  border: 1px solid #4f46e5;
}

.language-switcher.filter-mode .toggle-option {
  font-size: 14px;
  padding: 7px 12px;
}

/* Mobile 模式 - 移动端，紧挨筛选按钮 */
.language-switcher.mobile-mode .toggle-track {
  border: 1px solid #e5e7eb;
  width: 90px;
  height: 32px;
  background: white;
}

.language-switcher.mobile-mode .toggle-slider {
  background: #e0e7ff;
  border: 1px solid #4f46e5;
}

.language-switcher.mobile-mode .toggle-option {
  font-size: 14px;
  padding: 7px 12px;
  font-weight: 600;
}

.language-switcher.mobile-mode .toggle-track:hover {
  border-color: #3b82f6;
}
</style>
