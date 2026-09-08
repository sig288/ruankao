<template>
  <div class="rk-page">
    <div class="rk-card p-3.5 flex items-center justify-between">
      <div>
        <h2 class="text-[13px] font-black text-ink-800">Android 客户端</h2>
        <p class="text-[10px] text-muted">第3版大纲 · 官方安装包</p>
      </div>
      <button class="text-[12px] font-bold text-pine-600 min-h-[36px] px-2" @click="goBack">返回</button>
    </div>

    <section class="rk-card overflow-hidden bg-ink-800 text-paper-50 p-4">
      <p class="text-[10px] tracking-widest text-paper-300">v{{ info.latest_version }} · {{ info.release_date }}</p>
      <h1 class="text-lg font-black mt-1 leading-tight">{{ info.title || '下载软考中项助手' }}</h1>
      <p class="text-[11px] text-paper-300 mt-2">安装后可离主屏使用，刷题进度与网页互通。</p>
      <a
        :href="apkUrl"
        class="mt-4 min-h-[48px] rounded-xl bg-paper-50 text-ink-800 font-black text-[13px] flex items-center justify-center"
      >
        下载 APK（{{ info.apk_size_human || '约 15 MB' }}）
      </a>
      <p class="text-[10px] text-paper-300 mt-2 text-center">Android 8.0 及以上 · 如提示未知来源，允许本次安装即可</p>
    </section>

    <section class="rk-card p-4 space-y-2">
      <h3 class="text-[13px] font-black text-ink-800">本版说明</h3>
      <p
        v-for="(note, idx) in info.release_notes || []"
        :key="idx"
        class="text-[12px] text-ink-800 leading-relaxed pl-2 border-l-2 border-pine-500"
      >
        {{ note }}
      </p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appApi } from '@/api'
import { useAuthStore } from '@/store/auth'
import { resolveApkUrl } from '@/version'

const router = useRouter()
const authStore = useAuthStore()
const info = ref<any>({
  latest_version: '3.2.1',
  title: '软考中项助手',
  apk_size_human: '15.3 MB',
  release_date: '2026-09-08',
  release_notes: [],
  download_url: '/api/v1/app/download-apk',
})

const apkUrl = computed(() => resolveApkUrl(info.value.download_url))

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push(authStore.isLoggedIn ? '/' : '/login')
}

onMounted(async () => {
  try {
    const res: any = await appApi.getLatestInfo()
    if (res) info.value = res
  } catch (err) {
    console.warn('获取版本信息失败', err)
  }
})
</script>
