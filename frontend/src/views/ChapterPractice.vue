<template>
  <div
    class="p-4 flex flex-col space-y-4 pb-24"
    @touchstart="handleTouchStart"
    @touchend="handleTouchEnd"
  >
    <!-- Chapter Selector Drawer / Header -->
    <div class="bg-white dark:bg-slate-800 p-3.5 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center justify-between">
      <div class="flex-1 mr-2">
        <label class="block text-[10px] font-bold text-slate-400 uppercase">
          {{ isWeakMode ? '🔥 智能推题模式' : '当前章节' }}
        </label>
        <div v-if="isWeakMode" class="font-bold text-rose-600 dark:text-rose-400 text-sm">
          🎯 靶向薄弱点攻坚 (10题专练)
        </div>
        <select
          v-else
          v-model="selectedChapter"
          @change="handleChapterChange"
          class="w-full bg-transparent font-bold text-slate-800 dark:text-white text-sm focus:outline-none truncate cursor-pointer"
        >
          <option value="">全部十大知识领域</option>
          <option v-for="ch in chapters" :key="ch.chapter" :value="ch.chapter">
            {{ ch.chapter }} ({{ ch.total }}题)
          </option>
        </select>
      </div>

      <div class="flex items-center space-x-2">
        <button
          v-if="currentQuestion"
          @click="toggleFavorite"
          class="p-2 rounded-xl transition-colors active:scale-95"
          :class="isFavorited ? 'text-amber-500 bg-amber-50 dark:bg-amber-950/40' : 'text-slate-400 bg-slate-100 dark:bg-slate-700 hover:text-amber-500'"
          title="收藏本题"
        >
          <svg class="w-5 h-5" :fill="isFavorited ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="loading" class="text-center py-16 text-slate-400 text-sm">
      正在智能抽取题目...
    </div>
    <div v-else-if="questions.length === 0" class="bg-white dark:bg-slate-800 rounded-2xl p-8 text-center text-slate-500 border border-slate-200 dark:border-slate-700">
      当前考点暂无题目，请切换章节或在管理后台导入。
    </div>

    <!-- Question Card -->
    <div v-else-if="currentQuestion" class="space-y-4">
      <!-- Progress Bar & Meta -->
      <div class="flex items-center justify-between text-xs text-slate-500">
        <span class="inline-flex items-center space-x-1 flex-wrap">
          <span class="px-2 py-0.5 bg-blue-50 dark:bg-blue-900/40 text-blue-600 dark:text-blue-300 rounded-md font-medium text-[11px]">{{ currentQuestion.chapter }}</span>
          <span class="px-2 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-md font-medium text-[11px]">{{ currentQuestion.knowledge }}</span>
        </span>
        <span class="font-mono font-bold text-slate-700 dark:text-slate-300 whitespace-nowrap ml-2">
          <span class="text-blue-600 text-sm">{{ currentIndex + 1 }}</span> / {{ questions.length }}
        </span>
      </div>

      <!-- Question Card Container -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200/90 dark:border-slate-700 shadow-sm space-y-4">
        <!-- Stem -->
        <div class="text-sm font-semibold text-slate-800 dark:text-white leading-relaxed">
          {{ currentQuestion.stem }}
        </div>

        <!-- Options List with 44pt touch area -->
        <div class="space-y-2.5 pt-2">
          <button
            v-for="(opt, idx) in currentQuestion.options"
            :key="idx"
            @click="handleSelectOption(getOptionKey(opt, idx))"
            :disabled="hasSubmitted"
            class="w-full min-h-[48px] text-left p-3.5 rounded-xl border text-xs leading-relaxed transition-all flex items-start space-x-3 active:scale-[0.99] touch-manipulation"
            :class="getOptionClass(opt, idx)"
          >
            <span class="w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shrink-0" :class="getBadgeClass(opt, idx)">
              {{ getOptionKey(opt, idx) }}
            </span>
            <span class="pt-0.5 text-slate-800 dark:text-slate-100 flex-1">{{ cleanOptionText(opt) }}</span>
          </button>
        </div>
      </div>

      <!-- Instant Feedback & Analysis Box -->
      <div v-if="hasSubmitted" class="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200/90 dark:border-slate-700 shadow-sm space-y-3">
        <div class="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-700">
          <div class="flex items-center space-x-2">
            <span
              class="px-2.5 py-0.5 rounded-full text-xs font-bold"
              :class="isCorrect ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300' : 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300'"
            >
              {{ isCorrect ? '回答正确 ✓' : '回答错误 ✗' }}
            </span>
            <span class="text-xs text-slate-500">正确答案：<b class="text-emerald-600 font-mono text-sm">{{ currentQuestion.correct_answer }}</b></span>
          </div>
          <span class="text-xs text-slate-400">已沉淀至错题模型</span>
        </div>

        <div>
          <h4 class="text-xs font-bold text-slate-700 dark:text-slate-200 mb-1">【考点解析】</h4>
          <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-line">{{ currentQuestion.analysis }}</p>
        </div>

        <!-- P0 DeepSeek AI Companion Assist Panel -->
        <AiAssistPanel
          :question-id="currentQuestion.id"
          :is-case="false"
        />
      </div>

      <!-- Navigation Actions -->
      <div class="flex items-center justify-between pt-2">
        <button
          @click="prevQuestion"
          :disabled="currentIndex === 0"
          class="px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold shadow-sm disabled:opacity-40 active:scale-95"
        >
          ← 上一题
        </button>

        <span class="text-[11px] text-slate-400">支持手势左右滑动切题</span>

        <button
          @click="nextQuestion"
          :disabled="currentIndex >= questions.length - 1"
          class="px-5 py-2.5 bg-blue-600 text-white rounded-xl text-xs font-bold shadow-sm hover:bg-blue-700 active:scale-95 transition-all disabled:opacity-40"
        >
          下一题 →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { questionApi, practiceApi, wrongBookApi, masteryApi } from '@/api'
import { haptics } from '@/utils/haptics'
import AiAssistPanel from '@/components/AiAssistPanel.vue'

const route = useRoute()

const chapters = ref<any[]>([])
const selectedChapter = ref('')
const questions = ref<any[]>([])
const currentIndex = ref(0)
const loading = ref(false)

const userAnswers = ref<Record<string, string>>({})
const submitResults = ref<Record<string, any>>({})
const favoritedMap = ref<Record<string, boolean>>({})

// Touch swipe tracking (M7 手势左右滑动切题)
const touchStartX = ref(0)
const touchEndX = ref(0)

const isWeakMode = computed(() => route.query.mode === 'weak')
const currentQuestion = computed(() => questions.value[currentIndex.value] || null)

const hasSubmitted = computed(() => {
  return !!currentQuestion.value && !!submitResults.value[currentQuestion.value.id]
})

const isCorrect = computed(() => {
  return currentQuestion.value && submitResults.value[currentQuestion.value.id]?.is_correct
})

const isFavorited = computed(() => {
  return currentQuestion.value && favoritedMap.value[currentQuestion.value.id]
})

function handleTouchStart(e: TouchEvent) {
  touchStartX.value = e.changedTouches[0].screenX
}

function handleTouchEnd(e: TouchEvent) {
  touchEndX.value = e.changedTouches[0].screenX
  const diff = touchEndX.value - touchStartX.value
  if (diff < -50) {
    // Swipe left -> next
    nextQuestion()
  } else if (diff > 50) {
    // Swipe right -> prev
    prevQuestion()
  }
}

function getOptionKey(opt: string, idx: number): string {
  const match = opt.match(/^([A-D])[\.、\s]/i)
  if (match) return match[1].toUpperCase()
  return String.fromCharCode(65 + idx)
}

function cleanOptionText(opt: string): string {
  return opt.replace(/^[A-D][\.、\s]+/i, '')
}

function getOptionClass(opt: string, idx: number) {
  if (!currentQuestion.value) return 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800'
  const key = getOptionKey(opt, idx)
  const qid = currentQuestion.value.id
  const submitted = submitResults.value[qid]

  if (!submitted) {
    return 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-blue-400 hover:bg-blue-50/40'
  }

  const uAns = userAnswers.value[qid]
  const cAns = currentQuestion.value.correct_answer

  if (key === cAns) {
    return 'border-emerald-500 bg-emerald-50/70 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-300 font-semibold'
  }
  if (key === uAns && !submitted.is_correct) {
    return 'border-rose-500 bg-rose-50/70 dark:bg-rose-950/40 text-rose-900 dark:text-rose-300'
  }
  return 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-850 opacity-60'
}

function getBadgeClass(opt: string, idx: number) {
  const key = getOptionKey(opt, idx)
  if (!currentQuestion.value) return 'bg-slate-100 dark:bg-slate-700 text-slate-600'
  const qid = currentQuestion.value.id
  const submitted = submitResults.value[qid]

  if (!submitted) return 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
  const uAns = userAnswers.value[qid]
  const cAns = currentQuestion.value.correct_answer

  if (key === cAns) return 'bg-emerald-600 text-white'
  if (key === uAns && !submitted.is_correct) return 'bg-rose-600 text-white'
  return 'bg-slate-200 dark:bg-slate-600 text-slate-500'
}

async function handleSelectOption(key: string) {
  if (!currentQuestion.value || hasSubmitted.value) return
  const qid = currentQuestion.value.id
  userAnswers.value[qid] = key

  try {
    const res: any = await practiceApi.submit({
      question_id: qid,
      user_answer: key
    })
    submitResults.value[qid] = res
    if (res.is_correct) {
      haptics.correct()
    } else {
      haptics.wrong()
    }
  } catch (err) {
    console.error('Submit answer error', err)
  }
}

async function toggleFavorite() {
  if (!currentQuestion.value) return
  const qid = currentQuestion.value.id
  haptics.click()
  try {
    const res: any = await wrongBookApi.toggleFavorite(qid)
    favoritedMap.value[qid] = res.favorited
  } catch (err) {
    console.error('Toggle favorite failed', err)
  }
}

function nextQuestion() {
  if (currentIndex.value < questions.value.length - 1) {
    haptics.click()
    currentIndex.value++
  }
}

function prevQuestion() {
  if (currentIndex.value > 0) {
    haptics.click()
    currentIndex.value--
  }
}

async function loadQuestions() {
  loading.value = true
  try {
    if (isWeakMode.value) {
      // M5: Weakness drill mode
      const res: any = await masteryApi.weakDrill(10)
      questions.value = res
    } else {
      const params: any = { subject: 'basic', limit: 100 }
      if (selectedChapter.value) {
        params.chapter = selectedChapter.value
      }
      const res: any = await questionApi.list(params)
      questions.value = res
    }
    currentIndex.value = 0
  } catch (err) {
    console.error('Load questions error', err)
  } finally {
    loading.value = false
  }
}

function handleChapterChange() {
  loadQuestions()
}

onMounted(async () => {
  try {
    const chRes: any = await questionApi.getChapters('basic')
    chapters.value = chRes
    if (route.query.chapter) {
      selectedChapter.value = route.query.chapter as string
    }
  } catch (err) {
    console.error('Get chapters error', err)
  }
  await loadQuestions()
})
</script>
