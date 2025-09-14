import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import DebugPage from '../views/DebugPage.vue'
import SearchTest from '../views/SearchTest.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
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
  ]
})

export default router 