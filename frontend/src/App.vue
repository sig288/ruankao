<template>
  <div class="app-root">
    <div class="app-shell">
      <header v-if="showBar" class="app-header">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2 min-w-0">
            <button
              v-if="canGoPageBack"
              class="w-8 h-8 rounded-full bg-black/5 hover:bg-black/10 active:scale-90 text-slate-800 flex items-center justify-center shrink-0 text-xl font-medium leading-none transition"
              aria-label="返回上一页"
              @click="goPageBack"
            >
              ‹
            </button>
            <div
              v-else
              class="w-8 h-8 rounded-xl bg-[#007AFF] text-white flex items-center justify-center text-[12px] font-bold tracking-tight shrink-0 shadow-sm"
            >
              中项
            </div>
            <div class="min-w-0">
              <h1 class="text-[14px] font-bold leading-none truncate text-slate-900">{{ pageTitle }}</h1>
              <p class="text-[10px] text-slate-400 mt-0.5 truncate font-medium">第3版大纲 · 官方教程</p>
            </div>
          </div>

          <div class="flex items-center gap-1.5 shrink-0">
            <router-link
              v-if="!inApp"
              to="/download"
              class="text-[11px] px-2.5 py-1 rounded-full bg-slate-200/70 hover:bg-slate-300 text-slate-700 font-medium transition"
            >
              下载
            </router-link>
            <button
              class="text-[11px] px-2.5 py-1 rounded-full bg-blue-50 text-blue-600 hover:bg-blue-100 font-semibold transition disabled:opacity-50"
              :disabled="checkingUpdate"
              @click="checkForUpdate(false)"
            >
              {{ checkingUpdate ? '检查中' : '更新' }}
            </button>
            <router-link
              v-if="authStore.isAdmin"
              to="/admin"
              class="text-[11px] px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200/60 font-semibold transition"
            >
              管理
            </router-link>
            <button
              class="text-[11px] px-2 py-1 text-slate-400 hover:text-rose-500 active:text-rose-600 transition font-medium"
              @click="handleLogout"
            >
              退出
            </button>
          </div>
        </div>
      </header>

      <main
        class="app-main"
        :class="{ 'app-main--full': !showBar && route.name !== 'MaterialRead', 'app-main--reader': route.name === 'MaterialRead' }"
      >
        <router-view />
      </main>

      <nav v-if="showBar" class="app-tabbar">
        <router-link to="/" class="tab-item" :class="{ 'is-active': isActive('/') }">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span>首页</span>
        </router-link>

        <router-link to="/learn/points" class="tab-item" :class="{ 'is-active': isLearn }" @click="$router.push('/learn/points')">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <span>学习</span>
        </router-link>

        <router-link to="/practice" class="tab-item" :class="{ 'is-active': $route.path.startsWith('/practice') }">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>刷题</span>
        </router-link>

        <router-link to="/mock-exam" class="tab-item" :class="{ 'is-active': $route.path.startsWith('/mock-exam') }">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>模考</span>
        </router-link>

        <router-link to="/wrong-questions" class="tab-item" :class="{ 'is-active': $route.path.startsWith('/wrong-questions') }">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>错题</span>
        </router-link>
      </nav>
    </div>

    <AppUpdateModal
      :visible="updateVisible"
      :update-info="updateInfo"
      @update:visible="updateVisible = $event"
      @close="updateVisible = false"
    />
    <div v-if="backToast" class="rk-toast">再按一次退出应用</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { appApi } from '@/api'
import AppUpdateModal from '@/components/AppUpdateModal.vue'
import { APP_VERSION, APP_VERSION_CODE, APPLIED_H5_CODE_KEY, isNativeApp } from '@/version'

const inApp = isNativeApp()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const chromeLess = computed(() => route.name === 'Login' || route.name === 'MaterialRead')
const showBar = computed(() => !chromeLess.value && authStore.isLoggedIn)

const pageTitle = computed(() => (route.meta.title as string) || '软考中项')

const isLearn = computed(() => route.path.startsWith('/learn'))

function isActive(path: string) {
  return route.path === path
}

const updateVisible = ref(false)
const updateInfo = ref<any>(null)
const checkingUpdate = ref(false)

function alreadyApplied(latestCode: number) {
  const applied = Number(localStorage.getItem(APPLIED_H5_CODE_KEY) || 0)
  return APP_VERSION_CODE >= latestCode || applied >= latestCode
}

async function checkForUpdate(silent = true) {
  if (checkingUpdate.value) return
  checkingUpdate.value = true
  try {
    const res: any = await appApi.checkUpdate({
      client_version: APP_VERSION,
      client_version_code: APP_VERSION_CODE,
      platform: 'android',
    })
    const latestCode = Number(res?.latest_version_code || 0)
    if (res?.has_update && !alreadyApplied(latestCode)) {
      updateInfo.value = res
      updateVisible.value = true
      return res
    }
    if (!silent) {
      alert(`当前已是最新版本 (v${APP_VERSION})`)
    }
  } catch (err) {
    console.warn('检查更新失败', err)
    if (!silent) alert('检查更新失败，请确认网络后重试')
  } finally {
    checkingUpdate.value = false
  }
}

function handleLogout() {
  if (confirm('确认退出登录吗？')) {
    authStore.logout()
    router.push('/login')
  }
}

const backToast = ref(false)
let lastBackAt = 0
let toastTimer: number | null = null
const rootNames = new Set(['Home', 'Login'])

const canGoPageBack = computed(() => !rootNames.has(String(route.name || '')))

function goPageBack() {
  if (window.history.length > 1) router.back()
  else router.replace('/')
}

function handleSystemBack(): boolean {
  if (updateVisible.value && !updateInfo.value?.is_force_update) {
    updateVisible.value = false
    return true
  }
  if (canGoPageBack.value) {
    goPageBack()
    return true
  }
  const now = Date.now()
  if (now - lastBackAt < 2000) {
    return false
  }
  lastBackAt = now
  backToast.value = true
  if (toastTimer) window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    backToast.value = false
  }, 1800)
  return true
}

function onKeydown(ev: KeyboardEvent) {
  if (ev.key !== 'Escape') return
  if (handleSystemBack()) ev.preventDefault()
}

onMounted(() => {
  checkForUpdate(true)
  ;(window as any).__rkOnBack = handleSystemBack
  document.addEventListener('backbutton', onCordovaBack, false)
  window.addEventListener('keydown', onKeydown)
})

function onCordovaBack(ev: Event) {
  ev.preventDefault()
  handleSystemBack()
}

onUnmounted(() => {
  if ((window as any).__rkOnBack === handleSystemBack) {
    delete (window as any).__rkOnBack
  }
  document.removeEventListener('backbutton', onCordovaBack, false)
  window.removeEventListener('keydown', onKeydown)
  if (toastTimer) window.clearTimeout(toastTimer)
})
</script>
