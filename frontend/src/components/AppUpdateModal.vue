<template>
  <div v-if="visible && updateInfo" class="fixed inset-0 z-[80] flex items-end sm:items-center justify-center p-4 bg-ink-900/55">
    <div class="w-full max-w-sm rk-card overflow-hidden">
      <div class="bg-ink-800 text-paper-50 p-4">
        <p class="text-[10px] tracking-widest text-paper-300">发现新版本 v{{ updateInfo.latest_version }}</p>
        <h3 class="text-[15px] font-black mt-1 leading-snug">{{ updateInfo.title || '软考助手新版发布' }}</h3>
        <p class="text-[10px] text-paper-300 mt-1">
          {{ updateInfo.release_date }} · {{ updateInfo.apk_size_human }}
        </p>
      </div>

      <ul class="p-4 space-y-2 max-h-[32vh] overflow-y-auto">
        <li
          v-for="(note, idx) in updateInfo.release_notes || []"
          :key="idx"
          class="text-[12px] text-ink-800 leading-relaxed pl-2 border-l-2 border-pine-500"
        >
          {{ note }}
        </li>
      </ul>

      <p v-if="statusText" class="px-4 pb-2 text-[11px] text-pine-700">{{ statusText }}</p>
      <div v-if="downloading" class="px-4 pb-2">
        <div class="h-1.5 bg-paper-200 rounded-full overflow-hidden">
          <div class="h-full bg-pine-600" :style="{ width: `${progress}%` }"></div>
        </div>
        <p class="text-[10px] text-muted mt-1">{{ progressLabel }}</p>
      </div>

      <div class="p-3 border-t border-paper-200 flex flex-col gap-2">
        <button
          class="min-h-[44px] rounded-xl bg-ink-800 text-paper-50 text-[13px] font-bold disabled:opacity-60"
          :disabled="busy"
          @click="hotUpdate"
        >
          {{ hotUpdating ? '正在更新…' : '应用内热更新' }}
        </button>
        <button
          v-if="!inApp"
          class="min-h-[40px] rounded-xl bg-paper-100 text-ink-800 text-[12px] font-bold disabled:opacity-60"
          :disabled="busy"
          @click="downloadApk"
        >
          {{ downloading ? '下载中…' : '下载 APK 安装包' }}
        </button>
        <button
          v-if="!updateInfo.is_force_update"
          class="min-h-[36px] text-[11px] text-muted"
          :disabled="busy"
          @click="dismiss"
        >
          稍后再说
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { applyHotUpdate, isNativeApp, resolveApkUrl } from '@/version'

const inApp = isNativeApp()

const props = defineProps<{
  visible: boolean
  updateInfo: any
}>()

const emit = defineEmits(['update:visible', 'close'])

const hotUpdating = ref(false)
const downloading = ref(false)
const progress = ref(0)
const progressLabel = ref('')
const statusText = ref('')

const busy = computed(() => hotUpdating.value || downloading.value)

function dismiss() {
  if (props.updateInfo?.is_force_update || busy.value) return
  emit('update:visible', false)
  emit('close')
}

async function hotUpdate() {
  hotUpdating.value = true
  statusText.value = '正在拉取服务器最新页面…'
  try {
    await applyHotUpdate(Number(props.updateInfo?.latest_version_code || 0))
  } catch (err) {
    console.warn('热更新失败，回退刷新', err)
    window.location.reload()
  }
}

function downloadApk() {
  if (!props.updateInfo) return
  downloading.value = true
  statusText.value = '正在建立下载连接…'
  const url = resolveApkUrl(props.updateInfo.download_url)
  const xhr = new XMLHttpRequest()
  xhr.open('GET', url, true)
  xhr.responseType = 'blob'
  const expected = props.updateInfo.apk_size_bytes || 16 * 1024 * 1024
  xhr.onprogress = (ev) => {
    const loaded = ev.loaded
    const total = ev.lengthComputable ? ev.total : expected
    progress.value = Math.min(100, Math.round((loaded / total) * 100))
    progressLabel.value = `${(loaded / 1024 / 1024).toFixed(1)} MB / ${(total / 1024 / 1024).toFixed(1)} MB`
  }
  xhr.onload = () => {
    if (xhr.status !== 200 && xhr.status !== 206) {
      downloading.value = false
      statusText.value = '下载失败，请稍后重试'
      return
    }
    progress.value = 100
    statusText.value = '下载完成，正在打开安装…'
    const blob = xhr.response
    const href = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = href
    a.download = `ruankao-v${props.updateInfo.latest_version || 'latest'}.apk`
    document.body.appendChild(a)
    a.click()
    a.remove()
    setTimeout(() => URL.revokeObjectURL(href), 4000)
    downloading.value = false
  }
  xhr.onerror = () => {
    downloading.value = false
    statusText.value = '下载失败，已改为浏览器打开'
    window.open(url, '_blank')
  }
  xhr.send()
}
</script>
