<template>
  <div class="book" :class="{ 'is-chrome': chrome }">
    <header class="book-bar book-bar--top">
      <button class="book-btn" @click="emit('back')">返回</button>
      <h1 class="book-title">{{ title }}</h1>
      <button class="book-btn" @click="emit('download')">下载</button>
    </header>

    <div
      ref="stageRef"
      class="book-stage"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
    >
      <div v-if="status" class="book-status">{{ status }}</div>
      <div class="book-track" :class="{ 'is-animating': animating }" :style="trackStyle">
        <div class="book-slide">
          <canvas ref="prevRef" class="book-canvas"></canvas>
        </div>
        <div class="book-slide">
          <canvas ref="currRef" class="book-canvas"></canvas>
        </div>
        <div class="book-slide">
          <canvas ref="nextRef" class="book-canvas"></canvas>
        </div>
      </div>
    </div>

    <footer class="book-bar book-bar--bottom">
      <button class="book-btn" :disabled="page <= 1 || busy" @click="turn(-1)">上一页</button>
      <span class="book-page">{{ page }} / {{ pageCount || '…' }}</span>
      <button class="book-btn" :disabled="!pageCount || page >= pageCount || busy" @click="turn(1)">下一页</button>
    </footer>
    <div class="book-progress"><i :style="{ width: progressWidth }"></i></div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = defineProps<{ data: Blob; title?: string }>()
const emit = defineEmits(['back', 'download'])

const stageRef = ref<HTMLElement | null>(null)
const prevRef = ref<HTMLCanvasElement | null>(null)
const currRef = ref<HTMLCanvasElement | null>(null)
const nextRef = ref<HTMLCanvasElement | null>(null)

const page = ref(1)
const pageCount = ref(0)
const status = ref('正在打开讲义…')
const chrome = ref(true)
const animating = ref(false)
const busy = ref(false)
const dragX = ref(0)

const progressWidth = computed(() => {
  if (!pageCount.value) return '0%'
  return `${(page.value / pageCount.value) * 100}%`
})

const trackStyle = computed(() => {
  const w = stageWidth()
  return { transform: `translate3d(${-w + dragX.value}px, 0, 0)` }
})

let pdfDoc: any = null
let loadingTask: any = null
const pageCache = new Map<number, HTMLCanvasElement>()
const baking = new Set<number>()
let chromeTimer: number | null = null
let stageW = 360

function stageWidth() {
  return stageRef.value?.clientWidth || stageW || 360
}

function loadScript(src: string) {
  return new Promise<void>((resolve, reject) => {
    const existed = document.querySelector(`script[data-rk-pdf="${src}"]`)
    if (existed) {
      resolve()
      return
    }
    const el = document.createElement('script')
    el.src = src
    el.async = true
    el.dataset.rkPdf = src
    el.onload = () => resolve()
    el.onerror = () => reject(new Error('脚本加载失败'))
    document.head.appendChild(el)
  })
}

async function workerAsJsBlob(url: string) {
  const res = await fetch(url)
  if (!res.ok) throw new Error('阅读器组件下载失败')
  const buf = await res.arrayBuffer()
  return URL.createObjectURL(new Blob([buf], { type: 'text/javascript' }))
}

async function loadPdfJs() {
  try {
    const mod: any = await import('pdfjs-dist')
    const worker: any = await import('pdfjs-dist/build/pdf.worker.min.mjs?url')
    const lib = mod.default || mod
    const raw = String(worker.default || worker)
    try {
      lib.GlobalWorkerOptions.workerSrc = await workerAsJsBlob(raw)
    } catch {
      lib.GlobalWorkerOptions.workerSrc = raw
    }
    return lib
  } catch {
    await loadScript('https://cdn.bootcdn.net/ajax/libs/pdf.js/3.11.174/pdf.min.js').catch(() =>
      loadScript('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js')
    )
    const lib = (window as any).pdfjsLib
    if (!lib) throw new Error('阅读器引擎加载失败')
    lib.GlobalWorkerOptions.workerSrc =
      'https://cdn.bootcdn.net/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js'
    return lib
  }
}

function fitScale(pdfPage: any) {
  const stage = stageRef.value
  const vw = Math.max(stage?.clientWidth || 320, 280)
  const vh = Math.max(stage?.clientHeight || 480, 360)
  const unscaled = pdfPage.getViewport({ scale: 1 })
  const dpr = Math.min(window.devicePixelRatio || 1, 1.7)
  return Math.min(vw / unscaled.width, vh / unscaled.height) * dpr
}

function blit(target: HTMLCanvasElement | null, src: HTMLCanvasElement | null) {
  if (!target) return
  const ctx = target.getContext('2d')
  if (!ctx) return
  if (!src) {
    ctx.clearRect(0, 0, target.width, target.height)
    return
  }
  target.width = src.width
  target.height = src.height
  ctx.drawImage(src, 0, 0)
}

async function bakePage(num: number) {
  if (!pdfDoc || num < 1 || (pageCount.value && num > pageCount.value)) return
  if (pageCache.has(num) || baking.has(num)) return
  baking.add(num)
  try {
    const pdfPage = await pdfDoc.getPage(num)
    const scale = fitScale(pdfPage)
    const viewport = pdfPage.getViewport({ scale })
    const off = document.createElement('canvas')
    off.width = Math.max(1, Math.floor(viewport.width))
    off.height = Math.max(1, Math.floor(viewport.height))
    const ctx = off.getContext('2d', { alpha: false })
    if (!ctx) return
    ctx.fillStyle = '#fff'
    ctx.fillRect(0, 0, off.width, off.height)
    await pdfPage.render({ canvasContext: ctx, viewport, canvas: off }).promise
    pageCache.set(num, off)
    for (const key of [...pageCache.keys()]) {
      if (Math.abs(key - page.value) > 2) pageCache.delete(key)
    }
  } catch {
    /* ignore */
  } finally {
    baking.delete(num)
  }
}

async function paintSlots() {
  const n = page.value
  await Promise.all([bakePage(n), bakePage(n - 1), bakePage(n + 1)])
  blit(currRef.value, pageCache.get(n) || null)
  blit(prevRef.value, n > 1 ? pageCache.get(n - 1) || null : null)
  blit(nextRef.value, n < pageCount.value ? pageCache.get(n + 1) || null : null)
  bakePage(n + 2)
  bakePage(n - 2)
}

function showChrome(ms = 2800) {
  chrome.value = true
  if (chromeTimer) window.clearTimeout(chromeTimer)
  chromeTimer = window.setTimeout(() => {
    chrome.value = false
  }, ms)
}

function turn(delta: number) {
  if (busy.value || animating.value) return
  const next = Math.min(pageCount.value || 1, Math.max(1, page.value + delta))
  if (next === page.value) {
    bounce(0)
    return
  }
  animateTo(delta)
}

function bounce(toX: number) {
  animating.value = true
  dragX.value = toX
  window.setTimeout(() => {
    animating.value = false
    dragX.value = 0
  }, 280)
}

function animateTo(delta: number) {
  const w = stageWidth()
  animating.value = true
  busy.value = true
  dragX.value = delta > 0 ? -w : w
  window.setTimeout(async () => {
    page.value = Math.min(pageCount.value, Math.max(1, page.value + delta))
    await paintSlots()
    animating.value = false
    dragX.value = 0
    busy.value = false
    status.value = ''
  }, 300)
}

let pointerId: number | null = null
let startX = 0
let startY = 0
let startT = 0
let lastX = 0
let lastT = 0
let dragging = false
let locked: 'x' | 'y' | null = null

function onPointerDown(ev: PointerEvent) {
  if (animating.value || busy.value) return
  pointerId = ev.pointerId
  startX = lastX = ev.clientX
  startY = ev.clientY
  startT = lastT = Date.now()
  dragging = true
  locked = null
  animating.value = false
  stageRef.value?.setPointerCapture?.(ev.pointerId)
}

function onPointerMove(ev: PointerEvent) {
  if (!dragging || ev.pointerId !== pointerId) return
  const dx = ev.clientX - startX
  const dy = ev.clientY - startY
  if (!locked && Math.hypot(dx, dy) > 8) {
    locked = Math.abs(dx) > Math.abs(dy) * 1.05 ? 'x' : 'y'
  }
  if (locked !== 'x') return
  lastX = ev.clientX
  lastT = Date.now()
  let x = dx
  if ((page.value <= 1 && x > 0) || (page.value >= pageCount.value && x < 0)) {
    x *= 0.28
  }
  dragX.value = x
}

function onPointerUp(ev: PointerEvent) {
  if (!dragging || ev.pointerId !== pointerId) return
  dragging = false
  pointerId = null
  const dx = ev.clientX - startX
  const dy = ev.clientY - startY
  const dt = Math.max(1, Date.now() - startT)
  const vx = dx / dt
  if (!locked && Math.hypot(dx, dy) < 10 && dt < 280) {
    chrome.value = !chrome.value
    if (chrome.value) showChrome()
    bounce(0)
    return
  }
  if (locked !== 'x') {
    bounce(0)
    return
  }
  const w = stageWidth()
  const goNext = dx < 0 && (Math.abs(dx) > w * 0.14 || vx < -0.5) && page.value < pageCount.value
  const goPrev = dx > 0 && (Math.abs(dx) > w * 0.14 || vx > 0.5) && page.value > 1
  if (goNext) animateTo(1)
  else if (goPrev) animateTo(-1)
  else bounce(0)
}

function onKey(ev: KeyboardEvent) {
  if (ev.key === 'ArrowRight' || ev.key === 'PageDown') turn(1)
  else if (ev.key === 'ArrowLeft' || ev.key === 'PageUp') turn(-1)
}

onMounted(async () => {
  window.addEventListener('keydown', onKey)
  showChrome(3600)
  try {
    const [lib, buf] = await Promise.all([loadPdfJs(), props.data.arrayBuffer()])
    loadingTask = lib.getDocument({
      data: new Uint8Array(buf),
      disableAutoFetch: true,
      disableStream: true,
      disableRange: true,
      cMapPacked: true,
    })
    pdfDoc = await loadingTask.promise
    pageCount.value = pdfDoc.numPages || 1
    stageW = stageWidth()
    await paintSlots()
    status.value = ''
  } catch (err: any) {
    status.value = err?.message || '讲义打开失败'
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  if (chromeTimer) window.clearTimeout(chromeTimer)
  try {
    loadingTask?.destroy?.()
  } catch {}
  pdfDoc = null
  pageCache.clear()
})
</script>
