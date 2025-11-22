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
  // 滚动行为控制
  scrollBehavior(to, from, savedPosition) {
    // 如果是同一页面的弹窗打开/关闭，保持位置
    if (to.name === 'school-detail' && from.name === 'home') {
      return savedPosition || { top: 0 }
    }
    if (to.name === 'home' && from.name === 'school-detail') {
      return savedPosition || { top: 0 }
    }
    return { top: 0 }
  }
})

export default router
