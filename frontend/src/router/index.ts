import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true, title: '首页' },
  },
  {
    path: '/practice',
    name: 'Practice',
    component: () => import('@/views/ChapterPractice.vue'),
    meta: { requiresAuth: true, title: '章节刷题' },
  },
  {
    path: '/mock-exam',
    name: 'MockExam',
    component: () => import('@/views/MockExam.vue'),
    meta: { requiresAuth: true, title: '全真机考' },
  },
  {
    path: '/case-exam',
    name: 'CaseExam',
    component: () => import('@/views/CaseExam.vue'),
    meta: { requiresAuth: true, title: '案例分析' },
  },
  {
    path: '/wrong-questions',
    name: 'WrongQuestions',
    component: () => import('@/views/WrongQuestions.vue'),
    meta: { requiresAuth: true, title: '错题本' },
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('@/views/Favorites.vue'),
    meta: { requiresAuth: true, title: '我的收藏' },
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/views/Statistics.vue'),
    meta: { requiresAuth: true, title: '掌握度统计' },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, title: '管理后台' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginRegister.vue'),
    meta: { title: '登录与注册' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
