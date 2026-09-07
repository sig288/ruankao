<template>
  <div class="min-h-screen bg-slate-100 flex flex-col items-center">
    <!-- Mobile shell container: optimal for vivo X300 Pro (430px) and responsive -->
    <div class="w-full max-w-lg min-h-screen bg-slate-50 flex flex-col shadow-xl relative pb-20">
      
      <!-- Top App Bar -->
      <header v-if="showBar" class="sticky top-0 z-30 bg-white/90 backdrop-blur border-b border-slate-200 px-4 py-3 flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
            RK
          </div>
          <div>
            <h1 class="text-sm font-bold text-slate-800 leading-none">软考中项刷题</h1>
            <span class="text-[10px] text-slate-500">第3版教程 · 系统集成</span>
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <router-link
            v-if="authStore.isAdmin"
            to="/admin"
            class="text-xs px-2 py-1 bg-amber-50 text-amber-700 rounded border border-amber-200 font-medium hover:bg-amber-100"
          >
            管理后台
          </router-link>
          <span class="text-xs text-slate-600 font-medium">{{ authStore.username }}</span>
          <button
            @click="handleLogout"
            class="text-xs text-slate-400 hover:text-red-500 transition-colors"
            title="退出登录"
          >
            退出
          </button>
        </div>
      </header>

      <!-- Main Content Router View -->
      <main class="flex-1 overflow-y-auto">
        <router-view />
      </main>

      <!-- Bottom Navigation Bar for Mobile -->
      <nav v-if="showBar" class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-lg bg-white/95 backdrop-blur border-t border-slate-200 z-40 py-1.5 px-3 flex justify-around items-center shadow-lg">
        <router-link
          to="/"
          class="flex flex-col items-center py-1 px-3 rounded-lg transition-colors"
          :class="$route.path === '/' ? 'text-blue-600 font-semibold' : 'text-slate-500 hover:text-slate-700'"
        >
          <svg class="w-5 h-5 mb-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span class="text-[11px]">首页</span>
        </router-link>

        <router-link
          to="/practice"
          class="flex flex-col items-center py-1 px-3 rounded-lg transition-colors"
          :class="$route.path.startsWith('/practice') ? 'text-blue-600 font-semibold' : 'text-slate-500 hover:text-slate-700'"
        >
          <svg class="w-5 h-5 mb-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <span class="text-[11px]">章节练</span>
        </router-link>

        <router-link
          to="/mock-exam"
          class="flex flex-col items-center py-1 px-3 rounded-lg transition-colors"
          :class="$route.path.startsWith('/mock-exam') ? 'text-blue-600 font-semibold' : 'text-slate-500 hover:text-slate-700'"
        >
          <svg class="w-5 h-5 mb-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
          <span class="text-[11px]">模考</span>
        </router-link>

        <router-link
          to="/wrong-questions"
          class="flex flex-col items-center py-1 px-3 rounded-lg transition-colors"
          :class="$route.path.startsWith('/wrong-questions') ? 'text-blue-600 font-semibold' : 'text-slate-500 hover:text-slate-700'"
        >
          <svg class="w-5 h-5 mb-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span class="text-[11px]">错题本</span>
        </router-link>

        <router-link
          to="/statistics"
          class="flex flex-col items-center py-1 px-3 rounded-lg transition-colors"
          :class="$route.path.startsWith('/statistics') ? 'text-blue-600 font-semibold' : 'text-slate-500 hover:text-slate-700'"
        >
          <svg class="w-5 h-5 mb-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span class="text-[11px]">掌握度</span>
        </router-link>
      </nav>

    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const showBar = computed(() => {
  return route.name !== 'Login' && authStore.isLoggedIn
})

function handleLogout() {
  if (confirm('确认退出登录吗？')) {
    authStore.logout()
    router.push('/login')
  }
}
</script>
