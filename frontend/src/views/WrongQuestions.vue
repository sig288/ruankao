<template>
  <div class="p-4 space-y-4">
    <!-- Header with Filter -->
    <div class="bg-white p-3.5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
      <div>
        <h2 class="text-sm font-black text-slate-800">错题本与弱点消灭</h2>
        <p class="text-[10px] text-slate-400">自动沉淀日常练习与模考失误题</p>
      </div>

      <div class="flex items-center space-x-1.5">
        <button
          @click="filterMastered = filterMastered === false ? null : false; loadWrongQuestions()"
          class="px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors"
          :class="filterMastered === false ? 'bg-rose-600 text-white' : 'bg-slate-100 text-slate-600'"
        >
          未掌握
        </button>
        <button
          @click="filterMastered = null; loadWrongQuestions()"
          class="px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors"
          :class="filterMastered === null ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600'"
        >
          全部
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="loading" class="text-center py-16 text-slate-400 text-sm">
      正在检索错题本...
    </div>
    <div v-else-if="items.length === 0" class="bg-white rounded-2xl p-10 text-center text-slate-500 border border-slate-200">
      <div class="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-3 text-xl font-bold">
        ✓
      </div>
      <p class="text-sm font-bold text-slate-700">暂无需要消灭的错题</p>
      <p class="text-xs text-slate-400 mt-1">继续刷题或模拟考，巩固薄弱点！</p>
    </div>

    <!-- Wrong Questions List -->
    <div v-else class="space-y-4">
      <div
        v-for="item in items"
        :key="item.id"
        class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3 relative"
        :class="{ 'opacity-60 bg-slate-50/80': item.is_mastered }"
      >
        <!-- Top Badges & Actions -->
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center space-x-1.5">
            <span class="px-2 py-0.5 bg-blue-50 text-blue-700 rounded font-medium text-[11px]">{{ item.knowledge }}</span>
            <span class="px-1.5 py-0.2 bg-rose-50 text-rose-600 font-bold rounded text-[10px]">做错 {{ item.wrong_count }} 次</span>
          </div>

          <div class="flex items-center space-x-2">
            <button
              @click="toggleMaster(item)"
              class="text-xs px-2 py-1 rounded-lg font-medium transition-colors"
              :class="item.is_mastered ? 'bg-slate-200 text-slate-700' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'"
            >
              {{ item.is_mastered ? '重标未掌握' : '标为已掌握' }}
            </button>
            <button
              @click="deleteWrong(item.id)"
              class="text-xs text-slate-300 hover:text-red-500 transition-colors p-1"
              title="移出错题本"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Stem -->
        <div class="text-xs font-semibold text-slate-800 leading-relaxed">
          {{ item.stem }}
        </div>

        <!-- Options if basic -->
        <div v-if="item.options" class="space-y-1 bg-slate-50/70 p-2.5 rounded-xl text-[11px] text-slate-600">
          <div v-for="(opt, oIdx) in item.options" :key="oIdx">
            {{ opt }}
          </div>
        </div>

        <!-- Answer comparison -->
        <div class="flex items-center space-x-4 text-xs pt-1">
          <span class="text-rose-600">你的上次答案：<b>{{ item.user_answer || '未填' }}</b></span>
          <span class="text-emerald-600">正确答案：<b>{{ item.correct_answer }}</b></span>
        </div>

        <!-- Analysis -->
        <div class="p-3 bg-slate-50 rounded-xl text-xs text-slate-600 leading-relaxed">
          <span class="font-bold text-slate-700">解析：</span>{{ item.analysis }}
        </div>

        <!-- External AI Agent Explanation Card -->
        <div
          v-if="item.agent_explanation"
          class="bg-gradient-to-br from-indigo-50/90 to-blue-50/70 border border-indigo-200 rounded-xl p-3.5 text-xs text-indigo-950 space-y-1.5 shadow-sm"
        >
          <div class="flex items-center space-x-1.5 text-indigo-700 font-bold text-[11px]">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>外部 Agent 助教深度讲解与记忆锦囊</span>
          </div>
          <div class="leading-relaxed whitespace-pre-line text-slate-700 text-[11px] pt-1 border-t border-indigo-100">
            {{ item.agent_explanation }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { wrongBookApi } from '@/api'

const items = ref<any[]>([])
const loading = ref(false)
const filterMastered = ref<boolean | null>(false)

async function loadWrongQuestions() {
  loading.value = true
  try {
    const params: any = { limit: 100 }
    if (filterMastered.value !== null) {
      params.is_mastered = filterMastered.value
    }
    const res: any = await wrongBookApi.listWrong(params)
    items.value = res.items || []
  } catch (err) {
    console.error('Failed to load wrong questions', err)
  } finally {
    loading.value = false
  }
}

async function toggleMaster(item: any) {
  try {
    const newStatus = !item.is_mastered
    await wrongBookApi.toggleMaster(item.id, newStatus)
    item.is_mastered = newStatus
  } catch (err) {
    console.error('Toggle master failed', err)
  }
}

async function deleteWrong(id: string) {
  if (!confirm('确认从错题本中移除该题吗？')) return
  try {
    await wrongBookApi.deleteWrong(id)
    items.value = items.value.filter((x) => x.id !== id)
  } catch (err) {
    console.error('Delete wrong failed', err)
  }
}

onMounted(() => {
  loadWrongQuestions()
})
</script>
