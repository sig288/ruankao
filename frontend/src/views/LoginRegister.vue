<template>
  <div class="min-h-screen bg-slate-50 flex flex-col justify-center px-6 py-12">
    <div class="sm:mx-auto sm:w-full sm:max-w-md text-center">
      <div class="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center text-white font-black text-2xl mx-auto shadow-md">
        RK
      </div>
      <h2 class="mt-4 text-2xl font-black text-slate-900 tracking-tight">软考中项刷题助手</h2>
      <p class="mt-1 text-sm text-slate-500">系统集成项目管理工程师（第3版新大纲）</p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-6 shadow-sm border border-slate-200 rounded-2xl">
        <!-- Tabs -->
        <div class="flex border-b border-slate-200 mb-6">
          <button
            @click="isLogin = true"
            class="flex-1 pb-3 text-center text-sm font-semibold border-b-2 transition-colors"
            :class="isLogin ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-400 hover:text-slate-600'"
          >
            考生登录
          </button>
          <button
            @click="isLogin = false"
            class="flex-1 pb-3 text-center text-sm font-semibold border-b-2 transition-colors"
            :class="!isLogin ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-400 hover:text-slate-600'"
          >
            快速注册
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-700">用户名 / 手机号 / 邮箱</label>
            <input
              v-model="form.username"
              type="text"
              required
              class="mt-1 block w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
              placeholder="请输入账号或用户名"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700">密码</label>
            <input
              v-model="form.password"
              type="password"
              required
              class="mt-1 block w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
              placeholder="请输入密码（不少于6位）"
            />
          </div>

          <div v-if="errorMsg" class="p-3 bg-red-50 border border-red-200 text-red-600 rounded-xl text-xs">
            {{ errorMsg }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full mt-2 py-3 px-4 bg-blue-600 hover:bg-blue-700 active:scale-[0.99] text-white font-bold rounded-xl text-sm shadow-md transition duration-150 disabled:opacity-50"
          >
            {{ loading ? '提交中...' : (isLogin ? '立即进入刷题' : '注册并登录') }}
          </button>
        </form>

        <div class="mt-6 text-center text-xs text-slate-400">
          首位注册用户将自动升级为系统管理员
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'

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
    router.push(redirect)
  } catch (err: any) {
    errorMsg.value = err.message || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
