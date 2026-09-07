<template>
  <div class="p-4 space-y-4 pb-24">
    <!-- Header with upload button -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-lg font-bold text-slate-800 dark:text-white">📚 我的自有资料库</h2>
        <p class="text-xs text-slate-500">上传教材、口诀、案例及题库表，私人专属存储</p>
      </div>
      <button
        @click="showUploadModal = true"
        class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold shadow-sm flex items-center space-x-1 active:scale-95 transition-all"
      >
        <span>+ 上传资料</span>
      </button>
    </div>

    <!-- Category Filter Pills -->
    <div class="flex space-x-2 overflow-x-auto pb-1 no-scrollbar">
      <button
        v-for="cat in categories"
        :key="cat"
        @click="selectedCategory = cat; fetchMaterials()"
        class="px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors"
        :class="selectedCategory === cat ? 'bg-blue-600 text-white font-medium shadow-sm' : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700'"
      >
        {{ cat }}
      </button>
    </div>

    <!-- Materials List -->
    <div v-if="loading" class="py-12 text-center text-slate-400 text-xs">
      正在加载资料清单...
    </div>

    <div v-else-if="materials.length === 0" class="bg-white dark:bg-slate-800 rounded-2xl p-8 text-center border border-slate-200 dark:border-slate-700 shadow-sm">
      <div class="text-3xl mb-2">📁</div>
      <h3 class="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1">暂无上传资料</h3>
      <p class="text-xs text-slate-400 mb-4">您可以上传常用的软考中项 PDF、CSV 题库或背诵口诀图片</p>
      <button
        @click="showUploadModal = true"
        class="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-medium"
      >
        立即上传第一份资料
      </button>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="item in materials"
        :key="item.id"
        class="bg-white dark:bg-slate-800 rounded-2xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col space-y-2.5"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-start space-x-3">
            <div class="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-900/40 text-blue-600 dark:text-blue-300 flex items-center justify-center font-bold text-sm uppercase">
              {{ item.file_type }}
            </div>
            <div>
              <h4 class="text-sm font-bold text-slate-800 dark:text-white leading-snug">{{ item.title }}</h4>
              <div class="flex items-center space-x-2 mt-1">
                <span class="text-[10px] bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-md">
                  {{ item.category }}
                </span>
                <span v-if="item.chapter" class="text-[10px] text-blue-600 dark:text-blue-400 font-medium">
                  {{ item.chapter }}
                </span>
                <span class="text-[10px] text-slate-400">
                  {{ (item.file_size / (1024 * 1024)).toFixed(2) }} MB
                </span>
              </div>
            </div>
          </div>

          <button
            @click="deleteItem(item.id)"
            class="text-slate-400 hover:text-red-500 text-xs p-1"
            title="删除资料"
          >
            🗑
          </button>
        </div>

        <!-- M2 Bridge Action: Convert to Practice Questions -->
        <div v-if="item.file_type === 'csv' || item.file_type === 'json'" class="pt-2 border-t border-slate-100 dark:border-slate-700 flex items-center justify-between">
          <span class="text-[11px] text-slate-500">
            已生成可刷题目：<strong class="text-blue-600 font-semibold">{{ item.converted_question_count }}</strong> 题
          </span>
          <button
            @click="convertQuestions(item.id)"
            :disabled="convertingId === item.id"
            class="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 rounded-lg text-xs font-medium border border-indigo-200 dark:border-indigo-800 flex items-center space-x-1"
          >
            <span>⚡</span>
            <span>{{ convertingId === item.id ? '转化中...' : '导入为刷题' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-slate-800 rounded-3xl w-full max-w-sm p-5 space-y-4 shadow-2xl border border-slate-100 dark:border-slate-700">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-700 pb-3">
          <h3 class="text-sm font-bold text-slate-800 dark:text-white">上传学习资料</h3>
          <button @click="showUploadModal = false" class="text-slate-400 text-sm">✕</button>
        </div>

        <form @submit.prevent="handleUpload" class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">资料文件（≤ 50MB）</label>
            <input
              type="file"
              ref="fileInput"
              required
              class="w-full text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
            />
          </div>

          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">自定义资料标题</label>
            <input
              v-model="uploadForm.title"
              type="text"
              placeholder="如：第3版十大领域速记口诀"
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-xs"
            />
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">资料类别</label>
              <select
                v-model="uploadForm.category"
                class="w-full px-2 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-xs"
              >
                <option value="教材">教材</option>
                <option value="口诀">口诀</option>
                <option value="案例">案例</option>
                <option value="真题">真题</option>
                <option value="笔记">笔记</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">关联章节</label>
              <input
                v-model="uploadForm.chapter"
                type="text"
                placeholder="如：第9章 进度管理"
                class="w-full px-2 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-xs"
              />
            </div>
          </div>

          <div class="pt-2 flex space-x-2">
            <button
              type="button"
              @click="showUploadModal = false"
              class="flex-1 py-2 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-xl text-xs font-medium"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="uploading"
              class="flex-1 py-2 bg-blue-600 text-white rounded-xl text-xs font-semibold shadow hover:bg-blue-700 disabled:opacity-50"
            >
              {{ uploading ? '上传中...' : '确认上传' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { materialsApi } from '@/api'
import { haptics } from '@/utils/haptics'

const categories = ['全部', '教材', '口诀', '案例', '真题', '笔记']
const selectedCategory = ref('全部')
const materials = ref<any[]>([])
const loading = ref(false)
const uploading = ref(false)
const convertingId = ref<string | null>(null)
const showUploadModal = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const uploadForm = ref({
  title: '',
  category: '教材',
  chapter: ''
})

onMounted(() => {
  fetchMaterials()
})

async function fetchMaterials() {
  loading.value = true
  try {
    const params: any = {}
    if (selectedCategory.value !== '全部') {
      params.category = selectedCategory.value
    }
    const res = await materialsApi.list(params) as any
    materials.value = res
  } catch (e: any) {
    console.error(e)
  } finally {
    loading.value = false
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
    haptics.correct()
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
  haptics.click()
  try {
    await materialsApi.delete(id)
    await fetchMaterials()
  } catch (e: any) {
    alert(e.message || '删除失败')
  }
}

async function convertQuestions(id: string) {
  convertingId.value = id
  haptics.click()
  try {
    const res = await materialsApi.convertToQuestions(id) as any
    haptics.milestone()
    alert(res.message)
    await fetchMaterials()
  } catch (e: any) {
    alert(e.message || '转换失败')
  } finally {
    convertingId.value = null
  }
}
</script>
