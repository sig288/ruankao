<template>
  <div class="rk-page">
    <!-- Header -->
    <div class="bg-white rounded-2xl p-3.5 border border-slate-200 shadow-sm flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <router-link to="/learn/glossary" class="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg active:bg-slate-100">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </router-link>
        <div>
          <h2 class="text-xs font-bold text-slate-800">英语术语 10 词速测</h2>
          <p class="text-[10px] text-slate-400">看英文选中文 · 秒杀卷末真题</p>
        </div>
      </div>

      <button
        v-if="quizState === 'testing'"
        @click="confirmExit"
        class="text-xs text-slate-400 hover:text-slate-600 px-2 py-1"
      >
        退出
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-20 text-slate-400 text-xs">
      正在智能抽取 10 组高频词条与混淆选项...
    </div>

    <!-- State 1: In Quiz Testing Mode -->
    <div v-else-if="quizState === 'testing' && currentQuestion" class="space-y-4">
      <!-- Progress Bar Card -->
      <div class="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm space-y-2">
        <div class="flex items-center justify-between text-xs">
          <span class="font-bold text-indigo-700 font-mono">第 {{ currentIndex + 1 }} / {{ questions.length }} 题</span>
          <span class="text-slate-400">已作答 {{ answeredCount }} / {{ questions.length }} 题</span>
        </div>
        <div class="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            class="h-full bg-indigo-600 rounded-full transition-all duration-300"
            :style="{ width: `${((currentIndex + 1) / questions.length) * 100}%` }"
          ></div>
        </div>
      </div>

      <!-- Question Card -->
      <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
        <!-- English Term Presentation -->
        <div class="text-center py-4 bg-gradient-to-b from-indigo-50/60 to-slate-50 rounded-xl border border-indigo-100/60 space-y-2">
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 font-semibold font-mono">
            {{ (currentQuestion.tags && currentQuestion.tags[0]) || '核心术语' }}
          </span>
          <h3 class="text-base font-black font-mono text-indigo-950 px-2">
            {{ currentQuestion.term_en }}
          </h3>
          <p class="text-[11px] text-slate-500">请选择正确的中文释义：</p>
        </div>

        <!-- 4 Options (44pt minimum touch area) -->
        <div class="space-y-2.5">
          <button
            v-for="opt in currentQuestion.options"
            :key="opt.key"
            @click="selectOption(opt.key, opt.text)"
            class="w-full min-h-[48px] text-left p-3.5 rounded-xl border text-xs leading-relaxed transition-all flex items-start space-x-3 active:scale-[0.99] touch-manipulation"
            :class="getOptionClass(opt.key)"
          >
            <span
              class="w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shrink-0"
              :class="getBadgeClass(opt.key)"
            >
              {{ opt.key }}
            </span>
            <span class="pt-0.5 text-slate-800 flex-1 font-medium">{{ opt.text }}</span>
          </button>
        </div>
      </div>

      <!-- Navigation & Submit Bar -->
      <div class="flex items-center justify-between pt-2">
        <button
          @click="prevQuestion"
          :disabled="currentIndex === 0"
          class="px-4 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl text-xs font-bold disabled:opacity-40 active:scale-95"
        >
          ← 上一题
        </button>

        <button
          v-if="currentIndex < questions.length - 1"
          @click="nextQuestion"
          class="px-5 py-2.5 bg-indigo-600 text-white rounded-xl text-xs font-bold shadow-sm hover:bg-indigo-700 active:scale-95"
        >
          下一题 →
        </button>

        <button
          v-else
          @click="submitQuiz"
          :disabled="submitting"
          class="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-black shadow-md active:scale-95 transition-all disabled:opacity-50"
        >
          {{ submitting ? '交卷中...' : '提交小测 ✓' }}
        </button>
      </div>
    </div>

    <!-- State 2: Result & Review Mode -->
    <div v-else-if="quizState === 'result' && quizResult" class="space-y-4">
      <!-- Score Banner -->
      <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm text-center space-y-3">
        <div
          class="w-16 h-16 rounded-full flex items-center justify-center mx-auto text-2xl font-black"
          :class="quizResult.score >= 60 ? 'bg-emerald-100 text-emerald-600' : 'bg-rose-100 text-rose-600'"
        >
          {{ quizResult.score >= 60 ? '通关' : '加油' }}
        </div>
        <div>
          <h2 class="text-2xl font-black font-mono text-slate-800">{{ quizResult.score }} <span class="text-sm font-normal text-slate-400">/ 100 分</span></h2>
          <p class="text-xs text-slate-500 mt-1">
            答对 <b class="text-emerald-600 font-mono">{{ quizResult.correct_count }}</b> 题 / 共 {{ quizResult.total_questions }} 题
            <span v-if="quizResult.total_questions > 0" class="text-slate-400 font-mono">({{ Math.round((quizResult.correct_count / quizResult.total_questions) * 100) }}%)</span>
          </p>
        </div>

        <div class="pt-3 border-t border-slate-100 flex space-x-3">
          <button
            @click="startNewQuiz"
            class="flex-1 py-2.5 bg-indigo-600 text-white rounded-xl text-xs font-bold shadow-sm active:scale-95 transition-all"
          >
            再测一组 (10词)
          </button>
          <router-link
            to="/learn/glossary"
            class="flex-1 py-2.5 bg-slate-100 text-slate-700 rounded-xl text-xs font-semibold text-center hover:bg-slate-200 active:scale-95"
          >
            返回词表
          </router-link>
        </div>
      </div>

      <!-- Questions Review List -->
      <div class="space-y-3">
        <div class="text-xs font-bold text-slate-700 px-1">
          📋 错题回顾与考点精析
        </div>

        <div
          v-for="(item, idx) in quizResult.results"
          :key="item.term_id"
          class="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs space-y-2.5"
          :class="item.is_correct ? 'border-emerald-200/80 bg-emerald-50/10' : 'border-rose-200/80 bg-rose-50/10'"
        >
          <div class="flex items-center justify-between text-xs">
            <div class="flex items-center space-x-2">
              <span class="font-bold text-slate-400 font-mono">#{{ idx + 1 }}</span>
              <span class="font-bold font-mono text-indigo-900">{{ item.term_en }}</span>
            </div>
            <span
              class="px-2 py-0.5 rounded-full text-[10px] font-bold"
              :class="item.is_correct ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'"
            >
              {{ item.is_correct ? '回答正确 ✓' : '回答错误 ✗' }}
            </span>
          </div>

          <!-- Answer Comparison with option key and text -->
          <div class="text-xs space-y-1.5 pt-1">
            <div class="flex items-start space-x-2">
              <span class="text-slate-400 text-[11px] shrink-0 pt-0.5">你的作答：</span>
              <div :class="item.is_correct ? 'text-emerald-700 font-bold' : 'text-rose-600 font-semibold'">
                <span class="font-mono mr-1">[{{ item.selected_key || '未填' }}]</span>
                <span>{{ item.selected_text || '未作答' }}</span>
              </div>
            </div>
            <div class="flex items-start space-x-2">
              <span class="text-slate-400 text-[11px] shrink-0 pt-0.5">正确答案：</span>
              <div class="text-emerald-700 font-bold">
                <span class="font-mono mr-1">[{{ item.correct_key }}]</span>
                <span>{{ item.correct_text || item.term_zh }}</span>
              </div>
            </div>
          </div>

          <!-- Tip -->
          <div v-if="item.tip" class="p-2.5 bg-slate-50 rounded-xl text-[11px] text-slate-600 leading-relaxed">
            <b class="text-slate-700">考点提示：</b>{{ item.tip }}
          </div>

          <!-- Confuse with -->
          <div v-if="item.confuse_with && item.confuse_with.length > 0" class="text-[11px] text-amber-800 bg-amber-50/70 p-2 rounded-lg">
            <b>易混辨析：</b>{{ item.confuse_with.join('；') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { learnApi } from '@/api'
import { triggerHaptic } from '@/utils/haptics'

const router = useRouter()

const loading = ref(true)
const submitting = ref(false)
const quizState = ref<'testing' | 'result'>('testing')
const questions = ref<any[]>([])
const currentIndex = ref(0)
interface QuizAnswerState {
  key: string
  text: string
}
const answers = ref<Record<string, QuizAnswerState>>({})
const quizResult = ref<any>(null)

const currentQuestion = computed(() => {
  return questions.value[currentIndex.value]
})

const answeredCount = computed(() => {
  return Object.keys(answers.value).length
})

async function startNewQuiz() {
  loading.value = true
  quizState.value = 'testing'
  currentIndex.value = 0
  answers.value = {}
  quizResult.value = null

  try {
    const res = await learnApi.generateQuiz(undefined, 10)
    questions.value = res
  } catch (err) {
    console.error('Failed to generate quiz:', err)
  } finally {
    loading.value = false
  }
}

function selectOption(key: string, text: string) {
  triggerHaptic('tap')
  if (!currentQuestion.value) return
  answers.value[currentQuestion.value.term_id] = { key, text }

  // Automatically advance to next after short pause if not last
  if (currentIndex.value < questions.value.length - 1) {
    setTimeout(() => {
      currentIndex.value++
    }, 250)
  }
}

function prevQuestion() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

function nextQuestion() {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
  }
}

function getOptionClass(key: string) {
  if (!currentQuestion.value) return ''
  const sel = answers.value[currentQuestion.value.term_id]
  if (sel?.key === key) {
    return 'bg-indigo-50 border-indigo-500 text-indigo-950 font-semibold shadow-xs'
  }
  return 'bg-white border-slate-200 hover:border-slate-300'
}

function getBadgeClass(key: string) {
  if (!currentQuestion.value) return ''
  const sel = answers.value[currentQuestion.value.term_id]
  if (sel?.key === key) {
    return 'bg-indigo-600 text-white'
  }
  return 'bg-slate-100 text-slate-600'
}

async function submitQuiz() {
  submitting.value = true
  try {
    const payload = questions.value.map(q => {
      const a = answers.value[q.term_id]
      return {
        term_id: q.term_id,
        selected_key: a?.key || '',
        selected_option: a?.text || '',
        options: q.options || []
      }
    })

    const res = await learnApi.submitQuiz(payload)
    quizResult.value = res
    quizState.value = 'result'

    if (res.score >= 60) {
      triggerHaptic('success')
    } else {
      triggerHaptic('error')
    }
  } catch (err) {
    console.error('Failed to submit quiz:', err)
  } finally {
    submitting.value = false
  }
}

function confirmExit() {
  if (confirm('正在小测中，确认退出吗？')) {
    router.push('/learn/glossary')
  }
}

onMounted(() => {
  startNewQuiz()
})
</script>
