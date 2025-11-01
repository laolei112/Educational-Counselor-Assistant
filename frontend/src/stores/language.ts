import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { convertTextByLanguage } from '@/utils/textConverter'

export type Language = 'zh-CN' | 'zh-TW'

export const useLanguageStore = defineStore('language', () => {
  // 状态
  const currentLanguage = ref<Language>('zh-CN')
  
  // 计算属性
  const isSimplified = computed(() => currentLanguage.value === 'zh-CN')
  const isTraditional = computed(() => currentLanguage.value === 'zh-TW')
  
  // 语言标签映射
  const languageLabels = {
    'zh-CN': '简体中文',
    'zh-TW': '繁體中文'
  }
  
  // 方法
  const setLanguage = (lang: Language) => {
    currentLanguage.value = lang
    localStorage.setItem('preferred-language', lang)
    
    // 触发全局事件，通知所有组件更新
    window.dispatchEvent(new CustomEvent('languageChanged', { 
      detail: { language: lang } 
    }))
  }
  
  const initLanguage = () => {
    const saved = localStorage.getItem('preferred-language') as Language
    if (saved && ['zh-CN', 'zh-TW'].includes(saved)) {
      currentLanguage.value = saved
    } else {
      // 根据浏览器语言自动检测
      const browserLang = navigator.language
      if (browserLang.startsWith('zh-TW') || browserLang.startsWith('zh-HK')) {
        currentLanguage.value = 'zh-TW'
      } else {
        currentLanguage.value = 'zh-CN'
      }
    }
  }
  
  // 文本转换方法
  const convertText = (text: string): string => {
    if (!text) return text
    return convertTextByLanguage(text, currentLanguage.value)
  }
  
  // 获取学校名称的辅助函数
  const getSchoolName = (school: { name: string; nameTraditional?: string; nameEnglish?: string }) => {
    switch (currentLanguage.value) {
      case 'zh-TW':
        return school.nameTraditional || convertText(school.name)
      case 'zh-CN':
        return school.name
      default:
        return school.name
    }
  }
  
  // 多语言文本映射 - 使用更结构化的方式
  const getText = (key: string): string => {
    const textMap: Record<string, Record<Language, string>> = {
      // 搜索相关
      'search.placeholder': {
        'zh-CN': '搜索学校名称、地区、校网等...',
        'zh-TW': '搜索學校名稱、地區、校網等...'
      },
      
      // 学校类型
      'school.primary': {
        'zh-CN': '小学',
        'zh-TW': '小學'
      },
      'school.secondary': {
        'zh-CN': '中学',
        'zh-TW': '中學'
      },
      'school.schools': {
        'zh-CN': '所学校',
        'zh-TW': '所學校'
      },
      'school.openApplications': {
        'zh-CN': '所开放申请',
        'zh-TW': '所開放申請'
      },
      
      // 学校信息
      'school.tuition': {
        'zh-CN': '学费',
        'zh-TW': '學費'
      },
      'school.deadline': {
        'zh-CN': '截止',
        'zh-TW': '截止'
      },
      'school.details': {
        'zh-CN': '详情',
        'zh-TW': '詳情'
      },
      
      // 申请状态
      'school.applicationStatus.open': {
        'zh-CN': '开放申请',
        'zh-TW': '開放申請'
      },
      'school.applicationStatus.closed': {
        'zh-CN': '申请截止',
        'zh-TW': '申請截止'
      },
      'school.applicationStatus.deadline': {
        'zh-CN': '即将截止',
        'zh-TW': '即將截止'
      },
      
      // 升学信息
      'school.band1Rate': {
        'zh-CN': '升Band 1比例',
        'zh-TW': '升Band 1比例'
      },
      
      // 中学联系
      'school.throughTrain': {
        'zh-CN': '结龙学校',
        'zh-TW': '結龍學校'
      },
      'school.direct': {
        'zh-CN': '直属中学',
        'zh-TW': '直屬中學'
      },
      'school.associated': {
        'zh-CN': '联系中学',
        'zh-TW': '聯繫中學'
      },
      
      // 加载状态
      'loading.loading': {
        'zh-CN': '正在加载学校信息...',
        'zh-TW': '正在加載學校信息...'
      },
      'loading.loadingMore': {
        'zh-CN': '正在加载更多...',
        'zh-TW': '正在加載更多...'
      },
      
      // 错误状态
      'error.loadFailed': {
        'zh-CN': '加载失败',
        'zh-TW': '加載失敗'
      },
      'error.retry': {
        'zh-CN': '重试',
        'zh-TW': '重試'
      },
      
      // 空状态
      'empty.noData': {
        'zh-CN': '暂无数据',
        'zh-TW': '暫無數據'
      },
      'empty.noMoreData': {
        'zh-CN': '已加载全部',
        'zh-TW': '已加載全部'
      },
      
      // 性别
      'school.gender.coed': {
        'zh-CN': '男女校',
        'zh-TW': '男女校'
      },
      'school.gender.boys': {
        'zh-CN': '男校',
        'zh-TW': '男校'
      },
      'school.gender.girls': {
        'zh-CN': '女校',
        'zh-TW': '女校'
      },
      
      // 学校类型
      'school.type.elite': {
        'zh-CN': '名校联盟',
        'zh-TW': '名校聯盟'
      },
      'school.type.traditional': {
        'zh-CN': '传统名校',
        'zh-TW': '傳統名校'
      },
      'school.type.direct': {
        'zh-CN': '直资学校',
        'zh-TW': '直資學校'
      },
      'school.type.government': {
        'zh-CN': '官立学校',
        'zh-TW': '官立學校'
      },
      'school.type.private': {
        'zh-CN': '私立学校',
        'zh-TW': '私立學校'
      },
      'school.type.aided': {
        'zh-CN': '资助学校',
        'zh-TW': '資助學校'
      },
      
      // 筛选器相关
      'filter.all': {
        'zh-CN': '全部',
        'zh-TW': '全部'
      },
      'filter.allDistrict': {
        'zh-CN': '全部片区',
        'zh-TW': '全部片區'
      },
      'filter.allSchoolNet': {
        'zh-CN': '全部校网',
        'zh-TW': '全部校網'
      },
      'filter.allCategory': {
        'zh-CN': '全部类型',
        'zh-TW': '全部類型'
      },
      'filter.allBanding': {
        'zh-CN': '全部Banding',
        'zh-TW': '全部Banding'
      },
      
      // 应用信息
      'app.title': {
        'zh-CN': 'BetterSchool · 香港小学升学数据库',
        'zh-TW': 'BetterSchool · 香港小學升學數據庫'
      },
      'app.subtitle': {
        'zh-CN': '为您智能匹配最适合孩子的升学路径',
        'zh-TW': '為您智能匹配最適合孩子的升學路徑'
      },
      
      // 移动端筛选面板
      'mobileFilter.title': {
        'zh-CN': '筛选',
        'zh-TW': '篩選'
      },
      'mobileFilter.district': {
        'zh-CN': '片区',
        'zh-TW': '片區'
      },
      'mobileFilter.schoolNet': {
        'zh-CN': '校网',
        'zh-TW': '校網'
      },
      'mobileFilter.category': {
        'zh-CN': '学校类别',
        'zh-TW': '學校類別'
      },
      'mobileFilter.banding': {
        'zh-CN': 'Banding',
        'zh-TW': 'Banding'
      },
      'mobileFilter.sort': {
        'zh-CN': '排序',
        'zh-TW': '排序'
      },
      'mobileFilter.sortDefault': {
        'zh-CN': '默认排序',
        'zh-TW': '默認排序'
      },
      'mobileFilter.sortByBand': {
        'zh-CN': '按升Band比例',
        'zh-TW': '按升Band比例'
      },
      'mobileFilter.sortByFee': {
        'zh-CN': '按学费高低',
        'zh-TW': '按學費高低'
      },
      'mobileFilter.sortByDistrict': {
        'zh-CN': '按区域',
        'zh-TW': '按區域'
      },
      'mobileFilter.apply': {
        'zh-CN': '应用筛选',
        'zh-TW': '應用篩選'
      },
      'mobileFilter.filterAndSort': {
        'zh-CN': '筛选与排序',
        'zh-TW': '篩選與排序'
      }
    }
    
    const text = textMap[key]?.[currentLanguage.value]
    return text || key
  }
  
  return {
    currentLanguage,
    isSimplified,
    isTraditional,
    languageLabels,
    setLanguage,
    initLanguage,
    convertText,
    getSchoolName,
    getText
  }
})
