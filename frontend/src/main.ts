import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 延迟加载非关键功能，避免阻塞初始渲染
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => {
    import('./utils/anti-copy').then(({ initAntiCopy }) => {
      initAntiCopy()
    })
  }, { timeout: 3000 })
} else {
  // 降级方案：延迟执行
  setTimeout(() => {
    import('./utils/anti-copy').then(({ initAntiCopy }) => {
      initAntiCopy()
    })
  }, 500)
}

app.mount('#app')
