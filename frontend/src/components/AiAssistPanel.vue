<template>
  <div class="mt-3 border-t border-slate-100 pt-3">
    <!-- Trigger Button when folded -->
    <div v-if="!isOpen" class="flex items-center justify-between">
      <div class="flex items-center space-x-1.5">
        <button
          @click="openPanel('explain')"
          class="flex items-center space-x-1 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-[#007AFF] rounded-xl border border-blue-200/60 text-xs font-semibold shadow-xs transition active:scale-95"
        >
          <span>💡</span>
          <span>AI 深度精讲</span>
        </button>

        <button
          @click="openPanel('mnemonic')"
          class="flex items-center space-x-1 px-2.5 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-700 rounded-xl border border-amber-200/60 text-xs font-semibold transition active:scale-95"
        >
          <span>🎯</span>
          <span>记忆口诀</span>
        </button>
      </div>

      <span class="text-[11px] font-medium" :class="isAiEnabled ? 'text-slate-400' : 'text-amber-600 font-semibold'">
        {{ isAiEnabled ? `配额 ${remainingQuota}/${dailyLimit}` : '未开通' }}
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
      <div v-else-if="renderedHtml" class="space-y-3">
        <div
          class="ai-rendered-content max-w-none text-xs leading-relaxed text-slate-700 dark:text-slate-200 font-sans bg-white/80 dark:bg-slate-900/80 p-3.5 rounded-xl border border-indigo-100/80 dark:border-slate-700 shadow-inner max-h-96 overflow-y-auto"
          v-html="renderedHtml"
        ></div>

        <div class="flex items-center justify-between pt-1">
          <span class="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium flex items-center">
            ✓ 已自动同步至您的个人错题本与学习档案
          </span>
          <button
            @click="copyContent"
            class="px-2.5 py-1 bg-slate-200/80 hover:bg-slate-300 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 rounded-lg text-xs font-medium transition-colors"
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
import { ref, computed, watch, onMounted } from 'vue'
import { marked } from 'marked'
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
const isAiEnabled = ref(true)

const cacheMap = ref<Record<string, string>>({
  explain: props.initialExplanation || '',
  mnemonic: props.initialMnemonic || '',
  case_breakdown: ''
})

// Clean markdown utility: strips code fences and leading AI chatter
function cleanMarkdown(raw: string): string {
  if (!raw) return ''
  let text = raw.trim()

  // 1. Remove markdown code block wrapper ```markdown ... ``` or ``` ... ```
  const codeBlockMatch = text.match(/^```(?:markdown|md)?\s*\n([\s\S]*?)\n```\s*$/i)
  if (codeBlockMatch) {
    text = codeBlockMatch[1].trim()
  }

  // 2. Remove leading conversational greeting / chatter before the first main heading or section
  const lines = text.split('\n')
  let startIdx = 0
  const chatterRegex = /^(好的|当然|没问题|各位同学|大家好|同学们|你好|您好|针对这道|对于这道|收到|请看|下面是|以下是|作为软考|这道题主要考查)/
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i].trim()
    if (!l) continue
    if (startIdx === i && !l.startsWith('#') && !l.startsWith('>') && !l.startsWith('*') && !l.startsWith('-') && !l.startsWith('|')) {
      if (chatterRegex.test(l) && i + 1 < lines.length) {
        startIdx = i + 1
        continue
      }
    }
    break
  }
  if (startIdx > 0 && startIdx < lines.length) {
    text = lines.slice(startIdx).join('\n').trim()
  }

  return text
}

const currentRawText = computed(() => cacheMap.value[activeTab.value] || '')

const cleanedText = computed(() => cleanMarkdown(currentRawText.value))

const renderedHtml = computed(() => {
  if (!cleanedText.value) return ''
  try {
    return marked.parse(cleanedText.value, { gfm: true, breaks: true }) as string
  } catch (e) {
    return cleanedText.value
  }
})

watch(() => props.questionId, () => {
  cacheMap.value = {
    explain: props.initialExplanation || '',
    mnemonic: props.initialMnemonic || '',
    case_breakdown: ''
  }
  if (isOpen.value && !cacheMap.value[activeTab.value]) {
    fetchAiAssist()
  }
})

watch(() => props.initialExplanation, (val) => {
  if (val && !cacheMap.value.explain) {
    cacheMap.value.explain = val
  }
})

watch(() => props.initialMnemonic, (val) => {
  if (val && !cacheMap.value.mnemonic) {
    cacheMap.value.mnemonic = val
  }
})

onMounted(async () => {
  try {
    const quota = await aiApi.getQuota() as any
    remainingQuota.value = quota.remaining
    dailyLimit.value = quota.daily_limit
    isAiEnabled.value = !!quota.ai_enabled
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
  if (cleanedText.value) {
    navigator.clipboard.writeText(cleanedText.value)
    copyLabel.value = '已复制！'
    setTimeout(() => {
      copyLabel.value = '一键复制'
    }, 2000)
  }
}
</script>

<style scoped>
:deep(.ai-rendered-content) {
  word-break: break-word;
}

:deep(.ai-rendered-content h3) {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1e1b4b;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  border-bottom: 1.5px solid #e0e7ff;
  padding-bottom: 0.35rem;
}

:deep(.ai-rendered-content h3:first-child) {
  margin-top: 0;
}

:deep(.ai-rendered-content h4) {
  font-size: 0.85rem;
  font-weight: 700;
  color: #312e81;
  margin-top: 0.85rem;
  margin-bottom: 0.35rem;
}

:deep(.ai-rendered-content p) {
  font-size: 0.8125rem;
  line-height: 1.75;
  color: #334155;
  margin-bottom: 0.65rem;
}

:deep(.ai-rendered-content strong) {
  font-weight: 700;
  color: #1e1b4b;
  background-color: rgba(99, 102, 241, 0.09);
  padding: 0.05rem 0.3rem;
  border-radius: 0.25rem;
}

:deep(.ai-rendered-content blockquote) {
  margin: 0.75rem 0;
  padding: 0.6rem 0.85rem;
  background: linear-gradient(135deg, rgba(238, 242, 255, 0.85), rgba(245, 243, 255, 0.85));
  border-left: 3.5px solid #6366f1;
  border-radius: 0 0.6rem 0.6rem 0;
  color: #312e81;
  font-size: 0.8125rem;
  line-height: 1.65;
}

:deep(.ai-rendered-content blockquote p) {
  margin-bottom: 0.25rem;
  color: #312e81;
}

:deep(.ai-rendered-content blockquote p:last-child) {
  margin-bottom: 0;
}

:deep(.ai-rendered-content table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.75rem 0;
  font-size: 0.75rem;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

:deep(.ai-rendered-content th) {
  background-color: #e0e7ff;
  color: #312e81;
  font-weight: 600;
  padding: 0.45rem 0.65rem;
  text-align: left;
  border: 1px solid #c7d2fe;
}

:deep(.ai-rendered-content td) {
  padding: 0.45rem 0.65rem;
  border: 1px solid #e0e7ff;
  color: #334155;
  background-color: #ffffff;
}

:deep(.ai-rendered-content tr:nth-child(even) td) {
  background-color: #f8faff;
}

:deep(.ai-rendered-content ul),
:deep(.ai-rendered-content ol) {
  margin: 0.4rem 0 0.75rem;
  padding-left: 1.25rem;
}

:deep(.ai-rendered-content ul) {
  list-style-type: disc;
}

:deep(.ai-rendered-content ol) {
  list-style-type: decimal;
}

:deep(.ai-rendered-content li) {
  font-size: 0.8125rem;
  line-height: 1.7;
  color: #334155;
  margin-bottom: 0.25rem;
}

:deep(.ai-rendered-content hr) {
  border: none;
  border-top: 1px dashed #c7d2fe;
  margin: 0.85rem 0;
}

:deep(.ai-rendered-content code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.75rem;
  background-color: #eef2ff;
  color: #4338ca;
  padding: 0.1rem 0.35rem;
  border-radius: 0.3rem;
  border: 1px solid #e0e7ff;
}

:deep(.ai-rendered-content pre) {
  background-color: #1e293b;
  color: #f8fafc;
  padding: 0.75rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  font-size: 0.75rem;
  margin: 0.5rem 0;
}

:deep(.ai-rendered-content pre code) {
  background-color: transparent;
  color: inherit;
  border: none;
  padding: 0;
}

/* Dark mode overrides */
.dark :deep(.ai-rendered-content h3) {
  color: #e0e7ff;
  border-bottom-color: #374151;
}
.dark :deep(.ai-rendered-content h4) {
  color: #c7d2fe;
}
.dark :deep(.ai-rendered-content p),
.dark :deep(.ai-rendered-content li) {
  color: #cbd5e1;
}
.dark :deep(.ai-rendered-content strong) {
  color: #f1f5f9;
  background-color: rgba(99, 102, 241, 0.25);
}
.dark :deep(.ai-rendered-content blockquote) {
  background: rgba(30, 41, 59, 0.8);
  color: #c7d2fe;
  border-left-color: #818cf8;
}
.dark :deep(.ai-rendered-content blockquote p) {
  color: #c7d2fe;
}
.dark :deep(.ai-rendered-content th) {
  background-color: #312e81;
  color: #e0e7ff;
  border-color: #4338ca;
}
.dark :deep(.ai-rendered-content td) {
  background-color: #0f172a;
  color: #cbd5e1;
  border-color: #334155;
}
.dark :deep(.ai-rendered-content tr:nth-child(even) td) {
  background-color: #1e293b;
}
</style>
