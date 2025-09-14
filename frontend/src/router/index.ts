import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import DebugPage from '../views/DebugPage.vue'

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
    }
  ]
})

export default router 