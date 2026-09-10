<template>
  <div class="reader-page" :class="{ 'reader-page--full': kind === 'pdf' && blob && !loading && !error }">
    <header v-if="!(kind === 'pdf' && blob && !loading && !error)" class="reader-bar">
      <button class="reader-back" @click="goBack">返回</button>
      <h1 class="reader-title">{{ title }}</h1>
      <button class="reader-dl" :disabled="!blob" @click="download">下载</button>
    </header>

    <div v-if="loading" class="reader-state">
      <p>{{ loadingText }}</p>
      <div class="reader-progress">
        <div class="reader-progress-bar" :style="{ width: `${Math.max(6, progress * 100)}%` }"></div>
      </div>
      <p class="reader-progress-label">{{ progressLabel }}</p>
    </div>
    <div v-else-if="error" class="reader-state">
      <p>{{ error }}</p>
      <button class="reader-retry" @click="load">重试</button>
    </div>
    <PdfPreview
      v-else-if="kind === 'pdf' && blob"
      :data="blob"
      :title="title"
      @back="goBack"
      @download="download"
    />
    <div v-else-if="kind === 'image' && objectUrl" class="reader-body reader-body--img">
      <img :src="objectUrl" :alt="title" />
    </div>
    <pre v-else-if="kind === 'text' && textBody" class="reader-text">{{ textBody }}</pre>
    <div v-else class="reader-state">
      <p>该格式不支持在线预览，请下载后用 WPS / Excel 打开。</p>
      <button class="reader-retry" @click="download">下载文件</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { materialsApi } from '@/api'
import PdfPreview from '@/components/PdfPreview.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const progress = ref(0.04)
const error = ref('')
const title = ref((route.query.title as string) || '在线阅读')
const blob = ref<Blob | null>(null)
const objectUrl = ref('')
const textBody = ref('')
const kind = ref<'pdf' | 'image' | 'text' | 'other'>('other')
const fileType = ref('')

const loadingText = computed(() =>
  progress.value >= 0.98 ? '正在解码讲义…' : '正在调取云端讲义…'
)
const progressLabel = computed(() => `${Math.round(progress.value * 100)}%`)

const memCache = new Map<string, Blob>()

function sniffKind(buf: Blob, ext: string): 'pdf' | 'image' | 'text' | 'other' {
  const e = (ext || '').toLowerCase()
  const t = (buf.type || '').toLowerCase()
  if (e === 'pdf' || t.includes('pdf')) return 'pdf'
  if (['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(e) || t.startsWith('image/')) return 'image'
  if (['txt', 'md', 'csv', 'json'].includes(e) || t.startsWith('text/')) return 'text'
  return 'other'
}

async function blobLooksLikePdf(buf: Blob) {
  const head = await buf.slice(0, 5).text()
  return head.startsWith('%PDF')
}

async function readCache(id: string) {
  if (memCache.has(id)) return memCache.get(id) || null
  try {
    const cache = await caches.open('rk-materials-v1')
    const hit = await cache.match(`/__rk_mat/${id}`)
    if (!hit) return null
    const stored = await hit.blob()
    memCache.set(id, stored)
    return stored
  } catch {
    return null
  }
}

async function writeCache(id: string, buf: Blob) {
  memCache.set(id, buf)
  try {
    const cache = await caches.open('rk-materials-v1')
    await cache.put(
      `/__rk_mat/${id}`,
      new Response(buf, {
        headers: {
          'Content-Type': buf.type || 'application/pdf',
          'Cache-Control': 'max-age=604800',
        },
      })
    )
  } catch {
    /* private mode */
  }
}

async function load() {
  loading.value = true
  progress.value = 0.06
  error.value = ''
  blob.value = null
  textBody.value = ''
  if (objectUrl.value) {
    URL.revokeObjectURL(objectUrl.value)
    objectUrl.value = ''
  }
  const id = String(route.params.id || '')
  import('pdfjs-dist').catch(() => {})
  try {
    const cached = await readCache(id)
    const buf =
      cached ||
      (await materialsApi.getFileBlob(id, true, (ratio) => {
        progress.value = Math.min(0.96, Math.max(0.08, ratio))
      }))
    progress.value = 0.98
    if (!buf || buf.size === 0) throw new Error('文件为空')
    const looksPdf = await blobLooksLikePdf(buf)
    const mime = (buf.type || '').toLowerCase()
    if (!looksPdf && (mime.includes('json') || mime.includes('html')) && buf.size < 8192) {
      const txt = await buf.text()
      try {
        const parsed = JSON.parse(txt)
        throw new Error(parsed.detail || '讲义加载失败')
      } catch (e: any) {
        if (e instanceof SyntaxError) throw new Error('讲义加载失败，请重新登录后再试')
        throw e
      }
    }
    const ext = String(route.query.type || fileType.value || '')
    let nextKind = sniffKind(buf, ext)
    if (looksPdf) nextKind = 'pdf'
    kind.value = nextKind
    blob.value = buf
    if (!cached) writeCache(id, buf)
    if (nextKind === 'image') objectUrl.value = URL.createObjectURL(buf)
    if (nextKind === 'text') textBody.value = await buf.text()
  } catch (e: any) {
    error.value = e?.message || '无法加载讲义，请改用下载'
  } finally {
    loading.value = false
  }
}

function download() {
  if (!blob.value) return
  const href = URL.createObjectURL(blob.value)
  const a = document.createElement('a')
  a.href = href
  const ext = String(route.query.type || (kind.value === 'pdf' ? 'pdf' : ''))
  a.download = `${title.value}${ext ? '.' + ext : ''}`
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(href), 4000)
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.replace('/materials')
}

onMounted(load)
onUnmounted(() => {
  if (objectUrl.value) URL.revokeObjectURL(objectUrl.value)
})
</script>
