import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { isNativeApp } from '@/version'

const routes: RouteRecordRaw[] = [
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
    path: '/materials',
    name: 'Materials',
    component: () => import('@/views/MaterialsView.vue'),
    meta: { requiresAuth: true, title: '备考文库' },
  },
  {
    path: '/materials/:id/read',
    name: 'MaterialRead',
    component: () => import('@/views/MaterialReader.vue'),
    meta: { requiresAuth: true, title: '在线阅读' },
  },
  {
    path: '/plan',
    name: 'StudyPlan',
    component: () => import('@/views/StudyPlanView.vue'),
    meta: { requiresAuth: true, title: '备考计划' },
  },
  {
    path: '/learn',
    redirect: '/learn/points',
  },
  {
    path: '/learn/points',
    name: 'KnowledgeTree',
    component: () => import('@/views/KnowledgeTree.vue'),
    meta: { requiresAuth: true, title: '知识点全景树' },
  },
  {
    path: '/learn/points/:id',
    name: 'KnowledgeDetail',
    component: () => import('@/views/KnowledgeDetail.vue'),
    meta: { requiresAuth: true, title: '考点精析与例题' },
  },
  {
    path: '/learn/glossary',
    name: 'GlossaryList',
    component: () => import('@/views/GlossaryList.vue'),
    meta: { requiresAuth: true, title: '高频英语术语词表' },
  },
  {
    path: '/learn/glossary/quiz',
    name: 'GlossaryQuiz',
    component: () => import('@/views/GlossaryQuiz.vue'),
    meta: { requiresAuth: true, title: '英语术语速测' },
  },
  {
    path: '/learn/glossary/:id',
    name: 'GlossaryDetail',
    component: () => import('@/views/GlossaryDetail.vue'),
    meta: { requiresAuth: true, title: '英语词条详情' },
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
  {
    path: '/download',
    name: 'Download',
    component: () => import('@/views/DownloadView.vue'),
    meta: { title: '下载 Android 客户端' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.name === 'Download' && isNativeApp()) {
    next({ name: authStore.isLoggedIn ? 'Home' : 'Login' })
    return
  }
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
