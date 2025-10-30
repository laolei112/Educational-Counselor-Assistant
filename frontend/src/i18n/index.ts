// src/i18n/index.ts
import { createI18n } from 'vue-i18n'
import type { App } from 'vue'

// 导入语言资源
import zhCN from './locales/zh-CN'
import zhTW from './locales/zh-TW'

const messages = {
  'zh-CN': zhCN,
  'zh-TW': zhTW
}

const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: 'zh-CN', // 默认语言
  fallbackLocale: 'zh-CN', // 回退语言
  messages,
  globalInjection: true, // 全局注入 $t 函数
})

export default i18n

// 导出安装函数
export function setupI18n(app: App) {
  app.use(i18n)
}

// 导出 i18n 实例供组件使用
export { i18n }
