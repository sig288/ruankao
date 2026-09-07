<template>
  <div class="mt-4 border-t border-indigo-100 dark:border-slate-700 pt-3">
    <!-- Trigger Button when folded -->
    <div v-if="!isOpen" class="flex items-center justify-between">
      <button
        @click="openPanel('explain')"
        class="flex items-center space-x-1.5 px-3 py-2 bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-slate-800 dark:to-slate-750 text-indigo-700 dark:text-indigo-300 rounded-xl border border-indigo-200 dark:border-indigo-800 text-xs font-semibold shadow-sm hover:from-indigo-100 hover:to-blue-100 transition-all active:scale-95"
      >
        <span class="text-base">🤖</span>
        <span>呼叫 AI 学霸精讲</span>
      </button>

      <button
        @click="openPanel('mnemonic')"
        class="flex items-center space-x-1 px-2.5 py-2 bg-amber-50 dark:bg-slate-800 text-amber-700 dark:text-amber-300 rounded-xl border border-amber-200 dark:border-amber-800 text-xs font-medium hover:bg-amber-100 transition-all active:scale-95"
      >
        <span>🎯</span>
        <span>生成口诀</span>
      </button>

      <span class="text-[11px] text-slate-400">
        配额 {{ remainingQuota }}/{{ dailyLimit }}
      </span>
    </div>

    <!-- Active AI Panel -->
    <div v-else class="bg-gradient-to-b from-indigo-50/70 to-slate-50 dark:from-slate-800 dark:to-slate-850 rounded-2xl p-4 border border-indigo-200 dark:border-indigo-800 shadow-md">
      <!-- Header with Tabs & Close -->
      <div class="flex items-center justify-between mb-3 border-b border-indigo-100 dark:border-slate-700 pb-2">
        <div class="flex space-x-1">
          <button
            @click="switchTab('explain')"
            class="px-2.5 py-1 rounded-lg text-xs font-medium transition-colors"
            :class="activeTab === 'explain' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-300 hover:bg-indigo-100 dark:hover:bg-slate-700'"
          >
            💡 白话精讲
          </button>
          <button
            @click="switchTab('mnemonic')"
            class="px-2.5 py-1 rounded-lg text-xs font-medium transition-colors"
            :class="activeTab === 'mnemonic' ? 'bg-amber-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-300 hover:bg-amber-100 dark:hover:bg-slate-700'"
          >
            🎯 通关口诀
          </button>
          <button
            v-if="isCase"
            @click="switchTab('case_breakdown')"
            class="px-2.5 py-1 rounded-lg text-xs font-medium transition-colors"
            :class="activeTab === 'case_breakdown' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-300 hover:bg-emerald-100 dark:hover:bg-slate-700'"
          >
            📝 采分点拆解
          </button>
        </div>

        <div class="flex items-center space-x-2">
          <span class="text-[10px] bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 px-1.5 py-0.5 rounded-full font-mono">
            余{{ remainingQuota }}次
          </span>
          <button @click="isOpen = false" class="text-slate-400 hover:text-slate-600 text-xs p-1">
            ✕
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-6 flex flex-col items-center justify-center space-y-2 text-indigo-600 dark:text-indigo-400">
        <svg class="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-xs font-medium animate-pulse">DeepSeek 正在为您梳理第3版命题考点...</span>
      </div>

      <!-- Content State -->
      <div v-else-if="currentText" class="space-y-3">
        <div class="prose prose-sm dark:prose-invert max-w-none text-xs leading-relaxed text-slate-700 dark:text-slate-200 whitespace-pre-wrap font-sans bg-white/70 dark:bg-slate-900/70 p-3 rounded-xl border border-indigo-100 dark:border-slate-700 shadow-inner max-h-72 overflow-y-auto">
          {{ currentText }}
        </div>

        <div class="flex items-center justify-between pt-1">
          <span class="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium flex items-center">
            ✓ 已自动同步至您的个人错题本与学习档案
          </span>
          <button
            @click="copyContent"
            class="px-2.5 py-1 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-xs font-medium hover:bg-slate-300 transition-colors"
          >
            {{ copyLabel }}
          </button>
        </div>
      </div>

      <!-- Empty / Error Retry -->
      <div v-else class="py-4 text-center">
        <p class="text-xs text-slate-500 mb-2">点击下方按钮，由大模型为您专属生成解答</p>
        <button
          @click="fetchAiAssist"
          class="px-4 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-medium shadow hover:bg-indigo-700"
        >
          立即生成
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { aiApi } from '@/api'
import { haptics } from '@/utils/haptics'

const props = defineProps<{
  questionId?: string
  isCase?: boolean
  initialExplanation?: string
  initialMnemonic?: string
}>()

const isOpen = ref(false)
const activeTab = ref<'explain' | 'mnemonic' | 'case_breakdown'>('explain')
const loading = ref(false)
const copyLabel = ref('一键复制')
const remainingQuota = ref(30)
const dailyLimit = ref(30)

const cacheMap = ref<Record<string, string>>({
  explain: props.initialExplanation || '',
  mnemonic: props.initialMnemonic || '',
  case_breakdown: ''
})

const currentText = computed(() => cacheMap.value[activeTab.value])

onMounted(async () => {
  try {
    const quota = await aiApi.getQuota() as any
    remainingQuota.value = quota.remaining
    dailyLimit.value = quota.daily_limit
  } catch (e) {
    // ignore
  }
})

function openPanel(tab: 'explain' | 'mnemonic' | 'case_breakdown') {
  haptics.click()
  isOpen.value = true
  activeTab.value = tab
  if (!cacheMap.value[tab]) {
    fetchAiAssist()
  }
}

function switchTab(tab: 'explain' | 'mnemonic' | 'case_breakdown') {
  haptics.click()
  activeTab.value = tab
  if (!cacheMap.value[tab]) {
    fetchAiAssist()
  }
}

async function fetchAiAssist() {
  if (!props.questionId) return
  loading.value = true
  haptics.click()
  try {
    const res = await aiApi.createJob({
      question_id: props.questionId,
      action_type: activeTab.value
    }) as any

    cacheMap.value[activeTab.value] = res.response
    remainingQuota.value = res.remaining_quota
    haptics.correct()
  } catch (err: any) {
    alert(err.message || 'AI 伴学服务暂时繁忙，已自动为您呈现教材核心解析')
  } finally {
    loading.value = false
  }
}

function copyContent() {
  haptics.click()
  if (currentText.value) {
    navigator.clipboard.writeText(currentText.value)
    copyLabel.value = '已复制！'
    setTimeout(() => {
      copyLabel.value = '一键复制'
    }, 2000)
  }
}
</script>
