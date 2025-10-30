// src/composables/useI18n.ts
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { openccManager, type ConversionMode } from '@/utils/opencc'

export type Language = 'zh-CN' | 'zh-TW' | 'en'

export function useAdvancedI18n() {
  const { locale, t, ...i18nApi } = useI18n()
  
  // 当前语言
  const currentLanguage = computed(() => locale.value as Language)
  
  // 是否启用自动转换
  const enableAutoConversion = ref(true)
  
  // 转换缓存
  const conversionCache = new Map<string, string>()

  /**
   * 设置语言
   */
  const setLanguage = async (lang: Language) => {
    locale.value = lang
    localStorage.setItem('preferred-language', lang)
    
    // 触发全局事件
    window.dispatchEvent(new CustomEvent('languageChanged', { 
      detail: { language: lang } 
    }))
  }

  /**
   * 获取翻译文本（支持自动转换）
   */
  const getText = async (key: string, params?: Record<string, any>): Promise<string> => {
    // 首先尝试从 i18n 获取翻译
    let text = t(key, params)
    
    // 如果启用了自动转换且当前是繁体中文
    if (enableAutoConversion.value && currentLanguage.value === 'zh-TW') {
      const cacheKey = `${key}-${JSON.stringify(params || {})}`
      
      // 检查缓存
      if (conversionCache.has(cacheKey)) {
        return conversionCache.get(cacheKey)!
      }
      
      try {
        // 使用 OpenCC 进行转换
        const convertedText = await openccManager.simplifiedToTaiwanTraditional(text)
        conversionCache.set(cacheKey, convertedText)
        return convertedText
      } catch (error) {
        console.warn('OpenCC conversion failed, using original text:', error)
        return text
      }
    }
    
    return text
  }

  /**
   * 获取学校名称（智能选择）
   */
  const getSchoolName = async (school: { 
    name: string
    nameTraditional?: string
    nameEnglish?: string 
  }): Promise<string> => {
    switch (currentLanguage.value) {
      case 'zh-TW':
        if (school.nameTraditional) {
          return school.nameTraditional
        }
        // 如果没有繁体名称，尝试转换
        if (enableAutoConversion.value) {
          try {
            return await openccManager.simplifiedToTaiwanTraditional(school.name)
          } catch (error) {
            console.warn('Failed to convert school name:', error)
            return school.name
          }
        }
        return school.name
      case 'en':
        return school.nameEnglish || school.name
      default:
        return school.name
    }
  }

  /**
   * 批量转换文本
   */
  const convertTexts = async (texts: string[]): Promise<string[]> => {
    if (!enableAutoConversion.value || currentLanguage.value !== 'zh-TW') {
      return texts
    }

    try {
      const promises = texts.map(text => 
        openccManager.simplifiedToTaiwanTraditional(text)
      )
      return await Promise.all(promises)
    } catch (error) {
      console.warn('Batch conversion failed:', error)
      return texts
    }
  }

  /**
   * 检测文本语言
   */
  const detectTextLanguage = async (text: string) => {
    return await openccManager.detectLanguage(text)
  }

  /**
   * 清除转换缓存
   */
  const clearConversionCache = () => {
    conversionCache.clear()
  }

  /**
   * 初始化
   */
  const init = async () => {
    // 初始化 OpenCC
    try {
      await openccManager.init()
    } catch (error) {
      console.warn('OpenCC initialization failed, falling back to manual conversion:', error)
      enableAutoConversion.value = false
    }

    // 从本地存储恢复语言设置
    const saved = localStorage.getItem('preferred-language') as Language
    if (saved && ['zh-CN', 'zh-TW', 'en'].includes(saved)) {
      await setLanguage(saved)
    } else {
      // 根据浏览器语言自动检测
      const browserLang = navigator.language
      if (browserLang.startsWith('zh-TW') || browserLang.startsWith('zh-HK')) {
        await setLanguage('zh-TW')
      } else if (browserLang.startsWith('zh')) {
        await setLanguage('zh-CN')
      } else {
        await setLanguage('en')
      }
    }
  }

  return {
    // 基础 i18n API
    ...i18nApi,
    locale,
    t,
    
    // 扩展功能
    currentLanguage,
    enableAutoConversion,
    setLanguage,
    getText,
    getSchoolName,
    convertTexts,
    detectTextLanguage,
    clearConversionCache,
    init
  }
}
