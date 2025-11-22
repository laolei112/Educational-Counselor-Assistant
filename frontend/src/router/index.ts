import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
// 使用动态import延迟加载非关键页面
const DebugPage = () => import('../views/DebugPage.vue')
const SearchTest = () => import('../views/SearchTest.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/primary',
      name: 'primary',
      component: Home,
      beforeEnter: (to, from, next) => {
        // 可以在这里做一些初始化，比如设置 store 的 currentType
        next()
      }
    },
    {
      path: '/secondary',
      name: 'secondary',
      component: Home,
      beforeEnter: (to, from, next) => {
        next()
      }
    },
    {
      // 新增：学校详情页路由
      // 这对 SEO 至关重要，让每个学校都有独立的 URL
      path: '/school/:type/:id',
      name: 'school-detail',
      component: Home, // 仍然复用 Home 组件，在内部通过路由参数控制弹窗
      props: true
    },
    {
      path: '/debug',
      name: 'debug',
      component: DebugPage
    },
    {
      path: '/search-test',
      name: 'search-test',
      component: SearchTest
    }
  ],
  // 滚动行为控制 - 优化版本，避免不必要的滚动导致重排
  scrollBehavior(to, from, savedPosition) {
    // 如果是同一页面的弹窗打开/关闭，保持位置
    if (to.name === 'school-detail' && from.name === 'home') {
      // 如果有保存的位置，使用它；否则不滚动（避免强制重排）
      return savedPosition || null
    }
    if (to.name === 'home' && from.name === 'school-detail') {
      // 如果有保存的位置，使用它；否则不滚动（避免强制重排）
      return savedPosition || null
    }
    // 只有在真正需要滚动到顶部时才滚动
    // 使用 Promise + requestAnimationFrame 延迟执行，避免强制重排
    if (to.hash) {
      // 如果有锚点，滚动到锚点
      return { el: to.hash, behavior: 'smooth' }
    }
    // 否则延迟滚动到顶部，避免强制重排
    return new Promise((resolve) => {
      requestAnimationFrame(() => {
        resolve({ top: 0, behavior: 'smooth' })
      })
    })
  }
})

export default router
