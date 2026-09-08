<template>
  <div class="min-h-[100dvh] px-6 flex flex-col justify-center pb-[calc(var(--sab)+24px)]">
    <div class="text-center">
      <div class="w-14 h-14 bg-ink-800 text-paper-50 rounded-2xl flex items-center justify-center text-lg font-black mx-auto tracking-tight">
        中项
      </div>
      <h2 class="mt-4 text-xl font-black text-ink-800 tracking-tight">软考中项刷题助手</h2>
      <p class="mt-1 text-xs text-muted">系统集成项目管理工程师 · 第3版大纲</p>
    </div>

    <div class="mt-8 rk-card p-5">
      <div class="flex mb-5 bg-paper-100 rounded-xl p-1">
        <button
          @click="isLogin = true"
          class="flex-1 py-2 text-center text-sm font-bold rounded-lg transition-colors"
          :class="isLogin ? 'bg-ink-800 text-paper-50' : 'text-muted'"
        >
          登录
        </button>
        <button
          @click="isLogin = false"
          class="flex-1 py-2 text-center text-sm font-bold rounded-lg transition-colors"
          :class="!isLogin ? 'bg-ink-800 text-paper-50' : 'text-muted'"
        >
          注册
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-[11px] font-bold text-ink-800">账号</label>
          <input
            v-model="form.username"
            type="text"
            required
            class="mt-1.5 block w-full min-h-[44px] px-3 bg-paper-100 border border-paper-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-pine-600 focus:bg-paper-50"
            placeholder="用户名 / 手机号 / 邮箱"
          />
        </div>

        <div>
          <label class="block text-[11px] font-bold text-ink-800">密码</label>
          <input
            v-model="form.password"
            type="password"
            required
            class="mt-1.5 block w-full min-h-[44px] px-3 bg-paper-100 border border-paper-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-pine-600 focus:bg-paper-50"
            placeholder="不少于 6 位"
          />
        </div>

        <div v-if="errorMsg" class="p-3 bg-cinnabar-50 border border-cinnabar-100 text-cinnabar-700 rounded-xl text-xs">
          {{ errorMsg }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full min-h-[48px] mt-1 bg-ink-800 active:bg-ink-900 text-paper-50 font-bold rounded-xl text-sm disabled:opacity-50"
        >
          {{ loading ? '请稍候…' : (isLogin ? '进入备考' : '注册并进入') }}
        </button>
      </form>

      <p class="mt-5 text-center text-[10px] text-muted">首位注册用户将自动成为管理员</p>
      <router-link
        v-if="!inApp"
        to="/download"
        class="mt-3 block text-center text-[12px] font-bold text-pine-600 min-h-[36px] leading-[36px]"
      >
        下载 Android 客户端
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { isNativeApp } from '@/version'

const inApp = isNativeApp()

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLogin = ref(true)
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  username: '',
  password: '',
})

async function handleSubmit() {
  errorMsg.value = ''
  loading.value = true
  try {
    if (isLogin.value) {
      await authStore.login(form)
    } else {
      await authStore.register(form)
    }
    const redirect = (route.query.redirect as string) || '/'
    await router.replace(redirect.startsWith('/') ? redirect : '/')
  } catch (err: any) {
    errorMsg.value = err.message || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
