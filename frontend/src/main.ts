import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { initAntiCopy } from './utils/anti-copy'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 初始化防复制机制
initAntiCopy()

app.mount('#app')
