<template>
  <div class="rk-page">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-[15px] font-black text-ink-800">备考文库中心</h2>
        <p class="text-[10px] text-muted mt-0.5">官方精选讲义 · 即点即阅</p>
      </div>
      <button
        v-if="scope === 'private'"
        class="text-[11px] font-bold px-3 py-1.5 rounded-xl bg-ink-800 text-paper-50 min-h-[36px]"
        @click="showUploadModal = true"
      >
        + 上传
      </button>
    </div>

    <div class="rk-card p-1 flex">
      <button
        class="flex-1 py-2 text-[11px] font-bold rounded-[14px]"
        :class="scope === 'public' ? 'bg-ink-800 text-paper-50' : 'text-muted'"
        @click="switchScope('public')"
      >
        官方精选 {{ publicList.length ? publicList.length : '' }}
      </button>
      <button
        class="flex-1 py-2 text-[11px] font-bold rounded-[14px]"
        :class="scope === 'private' ? 'bg-ink-800 text-paper-50' : 'text-muted'"
        @click="switchScope('private')"
      >
        我的资料 {{ privateList.length ? privateList.length : '' }}
      </button>
    </div>

    <section v-if="scope === 'public'" class="rk-card overflow-hidden bg-ink-800 text-paper-50 p-3.5">
      <p class="text-[10px] tracking-widest text-paper-300">2026 最新大纲</p>
      <h3 class="text-[13px] font-black mt-1">三色笔记 · 导图口诀 · 机考指南 · 真题详解</h3>
      <p class="text-[10px] text-paper-300 mt-1">
        {{ stats?.total_files ? `资料图谱 ${stats.total_files} 份` : '精品讲义可在线阅读' }}
      </p>
    </section>

    <div class="flex space-x-2 overflow-x-auto pb-1 no-scrollbar">
      <button
        v-for="cat in currentCats"
        :key="cat"
        class="px-3 py-1.5 rounded-full text-[11px] whitespace-nowrap font-bold"
        :class="selectedCategory === cat ? 'bg-ink-800 text-paper-50' : 'rk-card text-ink-700'"
        @click="selectedCategory = cat"
      >
        {{ cat }}
      </button>
    </div>

    <div v-if="loading" class="py-12 text-center text-[12px] text-muted">正在整理资料清单…</div>

    <div v-else-if="filtered.length === 0" class="rk-card p-8 text-center">
      <div class="text-3xl mb-2">📂</div>
      <h3 class="text-[13px] font-black text-ink-800">暂无该分类资料</h3>
      <p class="text-[11px] text-muted mt-1">
        {{ scope === 'public' ? '可切换其他分类查看' : '还没有上传私有资料' }}
      </p>
    </div>

    <div v-else class="space-y-2.5">
      <div v-for="item in filtered" :key="item.id" class="rk-card p-3.5 space-y-2.5">
        <div class="flex items-start justify-between gap-2">
          <div class="flex items-start gap-2.5 min-w-0">
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center text-[10px] font-black uppercase shrink-0"
              :class="typeClass(item.file_type)"
            >
              {{ item.file_type }}
            </div>
            <div class="min-w-0">
              <div class="flex flex-wrap gap-1 mb-1">
                <span v-if="item.is_recommended" class="rk-chip bg-cinnabar-50 text-cinnabar-700">精选</span>
                <span v-if="item.year" class="rk-chip bg-paper-100 text-ink-700">{{ item.year }}</span>
                <span class="rk-chip bg-pine-100 text-pine-700">{{ item.category }}</span>
              </div>
              <h4 class="text-[13px] font-black text-ink-800 leading-snug">{{ item.title }}</h4>
              <p v-if="item.description" class="text-[10px] text-muted mt-0.5 leading-relaxed">{{ item.description }}</p>
            </div>
          </div>
          <button
            v-if="!item.is_public"
            class="text-muted text-xs p-1 shrink-0"
            @click="deleteItem(item.id)"
          >
            删
          </button>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-paper-200">
          <span class="text-[10px] text-muted">{{ formatSize(item.file_size) }}</span>
          <div class="flex items-center gap-1.5">
            <button
              v-if="canPreview(item.file_type)"
              class="px-2.5 py-1.5 rounded-xl bg-pine-100 text-pine-700 text-[11px] font-bold min-h-[36px]"
              @click="openRead(item)"
            >
              在线阅读
            </button>
            <button
              class="px-2.5 py-1.5 rounded-xl bg-paper-100 text-ink-800 text-[11px] font-bold min-h-[36px]"
              @click="downloadItem(item)"
            >
              下载
            </button>
            <button
              v-if="!item.is_public && (item.file_type === 'csv' || item.file_type === 'json')"
              class="px-2.5 py-1.5 rounded-xl bg-paper-100 text-ink-800 text-[11px] font-bold min-h-[36px]"
              :disabled="convertingId === item.id"
              @click="convertQuestions(item.id)"
            >
              {{ convertingId === item.id ? '转化中' : '转为刷题' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showUploadModal" class="fixed inset-0 bg-ink-900/55 z-50 flex items-center justify-center p-4">
      <div class="rk-card w-full max-w-sm p-5 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-[13px] font-black text-ink-800">上传私有学习资料</h3>
          <button class="text-muted" @click="showUploadModal = false">✕</button>
        </div>
        <form class="space-y-3" @submit.prevent="handleUpload">
          <div>
            <label class="block text-[11px] font-bold text-ink-800 mb-1">资料文件（≤ 50MB）</label>
            <input ref="fileInput" type="file" required class="w-full text-[11px]" />
          </div>
          <div>
            <label class="block text-[11px] font-bold text-ink-800 mb-1">标题</label>
            <input
              v-model="uploadForm.title"
              type="text"
              placeholder="如：第9章错题整理"
              class="w-full px-3 py-2 bg-paper-100 border border-paper-200 rounded-xl text-xs"
            />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-[11px] font-bold text-ink-800 mb-1">类别</label>
              <select
                v-model="uploadForm.category"
                class="w-full px-2 py-2 bg-paper-100 border border-paper-200 rounded-xl text-xs"
              >
                <option value="教材">教材</option>
                <option value="口诀">口诀</option>
                <option value="案例">案例</option>
                <option value="真题">真题</option>
                <option value="笔记">笔记</option>
              </select>
            </div>
            <div>
              <label class="block text-[11px] font-bold text-ink-800 mb-1">章节</label>
              <input
                v-model="uploadForm.chapter"
                type="text"
                placeholder="第9章"
                class="w-full px-2 py-2 bg-paper-100 border border-paper-200 rounded-xl text-xs"
              />
            </div>
          </div>
          <div class="flex gap-2 pt-1">
            <button type="button" class="flex-1 py-2 rounded-xl bg-paper-100 text-xs font-bold" @click="showUploadModal = false">
              取消
            </button>
            <button type="submit" :disabled="uploading" class="flex-1 py-2 rounded-xl bg-ink-800 text-paper-50 text-xs font-bold">
              {{ uploading ? '上传中…' : '确认上传' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { materialsApi } from '@/api'
import { haptics } from '@/utils/haptics'

const router = useRouter()
const publicCats = ['全部', '导图与三色笔记', '速记与背诵口诀', '机考与画图指南', '历年真题与解析', '官方教材与考纲']
const privateCats = ['全部', '教材', '口诀', '案例', '真题', '笔记']

const scope = ref<'public' | 'private'>('public')
const selectedCategory = ref('全部')
const publicList = ref<any[]>([])
const privateList = ref<any[]>([])
const stats = ref<any>(null)
const loading = ref(false)
const uploading = ref(false)
const convertingId = ref<string | null>(null)
const showUploadModal = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const uploadForm = ref({ title: '', category: '教材', chapter: '' })

const currentCats = computed(() => (scope.value === 'public' ? publicCats : privateCats))
const filtered = computed(() => {
  const list = scope.value === 'public' ? publicList.value : privateList.value
  if (selectedCategory.value === '全部') return list
  return list.filter((item) => item.category === selectedCategory.value)
})

onMounted(() => {
  fetchMaterials()
  fetchStats()
})

function switchScope(next: 'public' | 'private') {
  scope.value = next
  selectedCategory.value = '全部'
  haptics.click()
  fetchMaterials()
}

async function fetchStats() {
  try {
    stats.value = await materialsApi.getStats()
  } catch (e) {
    console.warn(e)
  }
}

async function fetchMaterials() {
  loading.value = true
  try {
    const res: any = await materialsApi.list({ scope: scope.value })
    if (scope.value === 'public') publicList.value = res || []
    else privateList.value = res || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function canPreview(type: string) {
  const t = (type || '').toLowerCase()
  return ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'txt', 'md'].includes(t)
}

function typeClass(type: string) {
  const t = (type || '').toLowerCase()
  if (t === 'pdf') return 'bg-cinnabar-50 text-cinnabar-700'
  if (['xls', 'xlsx', 'csv'].includes(t)) return 'bg-pine-100 text-pine-700'
  return 'bg-paper-200 text-ink-700'
}

function formatSize(size: number) {
  if (!size) return '—'
  return `${(size / (1024 * 1024)).toFixed(2)} MB`
}

function openRead(item: any) {
  haptics.click()
  router.push({
    name: 'MaterialRead',
    params: { id: item.id },
    query: { title: item.title, type: item.file_type },
  })
}

async function downloadItem(item: any) {
  haptics.click()
  try {
    const buf = await materialsApi.getFileBlob(item.id, false)
    const href = URL.createObjectURL(buf)
    const a = document.createElement('a')
    a.href = href
    a.download = `${item.title}${item.file_type ? '.' + item.file_type : ''}`
    document.body.appendChild(a)
    a.click()
    a.remove()
    setTimeout(() => URL.revokeObjectURL(href), 4000)
  } catch (e: any) {
    alert(e.message || '下载失败')
  }
}

async function handleUpload() {
  const files = fileInput.value?.files
  if (!files || files.length === 0) {
    alert('请先选择要上传的文件')
    return
  }
  uploading.value = true
  haptics.click()
  try {
    const formData = new FormData()
    formData.append('file', files[0])
    if (uploadForm.value.title) formData.append('title', uploadForm.value.title)
    formData.append('category', uploadForm.value.category)
    if (uploadForm.value.chapter) formData.append('chapter', uploadForm.value.chapter)
    await materialsApi.upload(formData)
    showUploadModal.value = false
    uploadForm.value.title = ''
    uploadForm.value.chapter = ''
    if (fileInput.value) fileInput.value.value = ''
    await fetchMaterials()
  } catch (e: any) {
    alert(e.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

async function deleteItem(id: string) {
  if (!confirm('确定要删除这份资料吗？')) return
  try {
    await materialsApi.delete(id)
    await fetchMaterials()
  } catch (e: any) {
    alert(e.message || '删除失败')
  }
}

async function convertQuestions(id: string) {
  convertingId.value = id
  try {
    const res: any = await materialsApi.convertToQuestions(id)
    alert(res.message)
    await fetchMaterials()
  } catch (e: any) {
    alert(e.message || '转换失败')
  } finally {
    convertingId.value = null
  }
}
</script>
