import { createRouter, createWebHistory } from 'vue-router'
import SchoolList from '../views/SchoolList.vue'
import SchoolDetail from '../views/SchoolDetail.vue'
// 使用动态import延迟加载非关键页面
const DebugPage = () => import('../views/DebugPage.vue')
const SearchTest = () => import('../views/SearchTest.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: SchoolList
    },
    {
      path: '/primary',
      name: 'primary',
      component: SchoolList,
      beforeEnter: (to, from, next) => {
        // 可以在这里做一些初始化，比如设置 store 的 currentType
        next()
      }
    },
    {
      path: '/secondary',
      name: 'secondary',
      component: SchoolList,
      beforeEnter: (to, from, next) => {
        next()
      }
    },
    {
      // 新增：学校详情页路由
      // 这对 SEO 至关重要，让每个学校都有独立的 URL
      path: '/school/:type/:id',
      name: 'school-detail',
      component: SchoolDetail, // 现在使用独立的详情页组件
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
    // 如果有保存的位置（比如浏览器后退），使用它
    if (savedPosition) {
      return savedPosition
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
