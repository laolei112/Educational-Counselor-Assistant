<template>
  <div class="language-switcher">
    <div class="language-dropdown" :class="{ 'is-open': isOpen }">
      <button 
        class="language-trigger" 
        @click="toggleDropdown"
        :aria-expanded="isOpen"
        aria-haspopup="true"
      >
        <span class="current-language">{{ languageStore.languageLabels[languageStore.currentLanguage] }}</span>
        <svg 
          class="dropdown-icon" 
          :class="{ 'is-open': isOpen }"
          width="12" 
          height="8" 
          viewBox="0 0 12 8" 
          fill="none"
        >
          <path 
            d="M1 1.5L6 6.5L11 1.5" 
            stroke="currentColor" 
            stroke-width="1.5" 
            stroke-linecap="round" 
            stroke-linejoin="round"
          />
        </svg>
      </button>
      
      <div class="language-menu" v-if="isOpen">
        <button
          v-for="lang in languages"
          :key="lang.value"
          class="language-option"
          :class="{ 'is-active': lang.value === languageStore.currentLanguage }"
          @click="selectLanguage(lang.value)"
        >
          <span class="language-name">{{ lang.label }}</span>
          <span class="language-code">{{ lang.code }}</span>
        </button>
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
  { value: 'zh-CN' as Language, label: '简体中文', code: '简' },
  { value: 'zh-TW' as Language, label: '繁體中文', code: '繁' }
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

.language-dropdown {
  position: relative;
}

.language-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
  justify-content: space-between;
}

.language-trigger:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

.language-trigger:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.current-language {
  flex: 1;
  text-align: left;
}

.dropdown-icon {
  transition: transform 0.2s ease;
  color: #6b7280;
}

.dropdown-icon.is-open {
  transform: rotate(180deg);
}

.language-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  z-index: 50;
  margin-top: 4px;
  overflow: hidden;
}

.language-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 10px 12px;
  background: white;
  border: none;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  transition: background-color 0.15s ease;
  text-align: left;
}

.language-option:hover {
  background: #f3f4f6;
}

.language-option.is-active {
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 600;
}

.language-name {
  flex: 1;
}

.language-code {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  margin-left: 8px;
}

.language-option.is-active .language-code {
  color: #1d4ed8;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .language-trigger {
    padding: 6px 10px;
    font-size: 13px;
    min-width: 100px;
  }
  
  .language-option {
    padding: 8px 10px;
    font-size: 13px;
  }
  
  .language-code {
    font-size: 11px;
  }
}
</style>
