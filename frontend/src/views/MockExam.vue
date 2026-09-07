<template>
  <div class="p-4 space-y-4">
    <!-- State 1: Configuration / Start Screen -->
    <div v-if="examState === 'intro'" class="space-y-4">
      <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm text-center">
        <div class="w-14 h-14 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-3">
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
        </div>
        <h2 class="text-base font-black text-slate-800">系统集成项目管理工程师 · 全真机考</h2>
        <p class="text-xs text-slate-500 mt-1">模拟全国软考标准化机考环境</p>

        <div class="mt-6 space-y-3 text-left">
          <label class="block text-xs font-bold text-slate-700">请选择试卷规格</label>
          <div class="grid grid-cols-2 gap-3">
            <button
              @click="configCount = 75; configTime = 120"
              class="p-3.5 rounded-xl border text-left transition-all"
              :class="configCount === 75 ? 'border-indigo-600 bg-indigo-50/70 text-indigo-900 ring-2 ring-indigo-500' : 'border-slate-200 bg-white'"
            >
              <div class="font-bold text-xs">标准全真卷</div>
              <div class="text-[11px] text-slate-500 mt-0.5">75 题 · 限时 120 分钟</div>
            </button>

            <button
              @click="configCount = 15; configTime = 25"
              class="p-3.5 rounded-xl border text-left transition-all"
              :class="configCount === 15 ? 'border-indigo-600 bg-indigo-50/70 text-indigo-900 ring-2 ring-indigo-500' : 'border-slate-200 bg-white'"
            >
              <div class="font-bold text-xs">通勤极速体验卷</div>
              <div class="text-[11px] text-slate-500 mt-0.5">15 题 · 限时 25 分钟</div>
            </button>
          </div>
        </div>

        <div class="mt-6 bg-slate-50 p-3.5 rounded-xl text-left text-xs text-slate-600 space-y-1">
          <p class="font-bold text-slate-700">考试规则：</p>
          <p>• 单选题每题 1 分，满分 75 分（体验卷满分 15 分）</p>
          <p>• 考中不显示正确答案与解析，提交后生成正式成绩单</p>
          <p>• 错题将自动归档至「错题本」，可供外部 AI 助教调阅</p>
        </div>

        <button
          @click="startExam"
          :disabled="loading"
          class="w-full mt-6 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-sm shadow-md transition-all active:scale-[0.99] disabled:opacity-50"
        >
          {{ loading ? '正在抽取试卷...' : '立即开始答题' }}
        </button>
      </div>
    </div>

    <!-- State 2: Active Exam Mode -->
    <div v-else-if="examState === 'testing'" class="space-y-4">
      <!-- Fixed Exam Sticky Bar -->
      <div class="bg-white p-3 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span class="text-xs font-mono font-bold" :class="remainingTime < 300 ? 'text-red-600' : 'text-slate-700'">
            倒计时：{{ formatTime(remainingTime) }}
          </span>
        </div>

        <div class="flex items-center space-x-2">
          <button
            @click="showSheet = true"
            class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium"
          >
            答题卡 ({{ answeredCount }}/{{ questions.length }})
          </button>
          <button
            @click="confirmSubmit"
            class="px-3 py-1 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-bold shadow-sm"
          >
            交卷
          </button>
        </div>
      </div>

      <!-- Question Card -->
      <div v-if="currentQ" class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
        <div class="flex items-center justify-between text-xs text-slate-400">
          <span>第 {{ currentIndex + 1 }} 题 / 共 {{ questions.length }} 题</span>
          <span class="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[11px]">{{ currentQ.chapter }}</span>
        </div>

        <div class="text-sm font-semibold text-slate-800 leading-relaxed">
          {{ currentQ.stem }}
        </div>

        <div class="space-y-2.5 pt-2">
          <button
            v-for="(opt, idx) in currentQ.options"
            :key="idx"
            @click="selectOption(getOptionKey(opt, idx))"
            class="w-full text-left p-3.5 rounded-xl border text-xs leading-relaxed transition-all flex items-start space-x-3"
            :class="answers[currentQ.id] === getOptionKey(opt, idx) ? 'border-indigo-600 bg-indigo-50/70 text-indigo-900 ring-2 ring-indigo-500 font-semibold' : 'border-slate-200 bg-white hover:border-slate-300'"
          >
            <span
              class="w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shrink-0"
              :class="answers[currentQ.id] === getOptionKey(opt, idx) ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600'"
            >
              {{ getOptionKey(opt, idx) }}
            </span>
            <span class="pt-0.5 flex-1">{{ cleanOptionText(opt) }}</span>
          </button>
        </div>
      </div>

      <!-- Exam Navigation Bar -->
      <div class="flex items-center justify-between pt-2">
        <button
          @click="prevQ"
          :disabled="currentIndex === 0"
          class="px-4 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl text-xs font-bold disabled:opacity-40"
        >
          上一题
        </button>

        <button
          @click="nextQ"
          :disabled="currentIndex >= questions.length - 1"
          class="px-5 py-2.5 bg-indigo-600 text-white rounded-xl text-xs font-bold shadow-sm hover:bg-indigo-700 disabled:opacity-40"
        >
          下一题
        </button>
      </div>
    </div>

    <!-- State 3: Exam Result & Report Screen -->
    <div v-else-if="examState === 'result' && examResult" class="space-y-4">
      <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm text-center">
        <div
          class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-3 text-2xl font-black"
          :class="isPass ? 'bg-emerald-100 text-emerald-600' : 'bg-rose-100 text-rose-600'"
        >
          {{ isPass ? '通过' : '未过' }}
        </div>
        <h2 class="text-xl font-black text-slate-800">{{ examResult.score }} <span class="text-sm font-normal text-slate-500">/ {{ examResult.total_score }} 分</span></h2>
        <p class="text-xs text-slate-500 mt-1">
          及格标准：{{ examResult.total_score * 0.6 }} 分 | 正确率：{{ Math.round((examResult.correct_count / examResult.total_questions) * 100) }}%
        </p>

        <div class="grid grid-cols-3 gap-2 mt-6 pt-4 border-t border-slate-100 text-center">
          <div>
            <div class="text-sm font-bold text-slate-800">{{ examResult.total_questions }}</div>
            <div class="text-[10px] text-slate-400">总题数</div>
          </div>
          <div>
            <div class="text-sm font-bold text-emerald-600">{{ examResult.correct_count }}</div>
            <div class="text-[10px] text-slate-400">正确数</div>
          </div>
          <div>
            <div class="text-sm font-bold text-slate-800">{{ Math.floor(examResult.time_spent / 60) }}分{{ examResult.time_spent % 60 }}秒</div>
            <div class="text-[10px] text-slate-400">用时</div>
          </div>
        </div>

        <div class="mt-6 flex space-x-3">
          <button
            @click="examState = 'intro'"
            class="flex-1 py-3 bg-indigo-600 text-white font-bold rounded-xl text-xs shadow hover:bg-indigo-700"
          >
            再考一套
          </button>
          <router-link
            to="/wrong-questions"
            class="flex-1 py-3 bg-slate-100 text-slate-700 font-bold rounded-xl text-xs hover:bg-slate-200 text-center"
          >
            去错题本巩固
          </router-link>
        </div>
      </div>

      <!-- Detail Answers Breakdown -->
      <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
        <h3 class="text-xs font-bold text-slate-800 uppercase">答题详单与解析</h3>
        <div class="space-y-4 divide-y divide-slate-100">
          <div v-for="(item, idx) in examResult.details" :key="idx" class="pt-4 first:pt-0 space-y-2">
            <div class="flex items-start justify-between">
              <span class="text-xs font-bold text-slate-800">第 {{ idx + 1 }} 题</span>
              <span
                class="px-2 py-0.5 rounded text-[10px] font-bold"
                :class="item.is_correct ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'"
              >
                {{ item.is_correct ? '正确' : '错误' }}
              </span>
            </div>
            <p class="text-xs text-slate-700">{{ item.stem }}</p>
            <div class="text-[11px] space-x-3 text-slate-500">
              <span>你的作答：<b :class="item.is_correct ? 'text-emerald-600' : 'text-rose-600'">{{ item.user_answer || '未答' }}</b></span>
              <span>正确答案：<b class="text-emerald-600">{{ item.correct_answer }}</b></span>
            </div>
            <div class="p-3 bg-slate-50 rounded-xl text-xs text-slate-600 leading-relaxed">
              <span class="font-bold text-slate-700">解析：</span>{{ item.analysis }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Answer Sheet Modal -->
    <div v-if="showSheet" class="fixed inset-0 bg-black/40 z-50 flex items-end justify-center">
      <div class="bg-white w-full max-w-lg rounded-t-3xl p-5 max-h-[70vh] flex flex-col space-y-4">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-sm font-bold text-slate-800">答题卡</h3>
          <button @click="showSheet = false" class="text-slate-400 text-sm font-bold">关闭 ✕</button>
        </div>

        <div class="grid grid-cols-5 gap-2.5 overflow-y-auto py-2">
          <button
            v-for="(q, idx) in questions"
            :key="q.id"
            @click="jumpToQuestion(idx)"
            class="h-10 rounded-xl border text-xs font-bold flex items-center justify-center transition-all"
            :class="answers[q.id] ? 'bg-indigo-600 text-white border-indigo-600' : (currentIndex === idx ? 'border-indigo-500 ring-2 ring-indigo-300' : 'bg-slate-50 border-slate-200 text-slate-600')"
          >
            {{ idx + 1 }}
          </button>
        </div>

        <button
          @click="confirmSubmit"
          class="w-full py-3 bg-rose-600 text-white font-bold rounded-xl text-xs shadow-md"
        >
          立即交卷
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { examApi } from '@/api'

const examState = ref<'intro' | 'testing' | 'result'>('intro')
const configCount = ref(75)
const configTime = ref(120) // minutes
const loading = ref(false)

const questions = ref<any[]>([])
const currentIndex = ref(0)
const answers = ref<Record<string, string>>({})
const remainingTime = ref(0)
const showSheet = ref(false)
const examResult = ref<any>(null)

let timer: any = null

const currentQ = computed(() => questions.value[currentIndex.value] || null)
const answeredCount = computed(() => Object.keys(answers.value).length)
const isPass = computed(() => {
  if (!examResult.value) return false
  return examResult.value.score >= examResult.value.total_score * 0.6
})

function getOptionKey(opt: string, idx: number): string {
  const match = opt.match(/^([A-D])[\.、\s]/i)
  if (match) return match[1].toUpperCase()
  return String.fromCharCode(65 + idx)
}

function cleanOptionText(opt: string): string {
  return opt.replace(/^[A-D][\.、\s]+/i, '')
}

function selectOption(key: string) {
  if (!currentQ.value) return
  answers.value[currentQ.value.id] = key
}

function jumpToQuestion(idx: number) {
  currentIndex.value = idx
  showSheet.value = false
}

function nextQ() {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
  }
}

function prevQ() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

async function startExam() {
  loading.value = true
  try {
    const res: any = await examApi.generate({
      subject: 'basic',
      question_count: configCount.value,
    })
    questions.value = res
    currentIndex.value = 0
    answers.value = {}
    remainingTime.value = configTime.value * 60
    examState.value = 'testing'

    clearInterval(timer)
    timer = setInterval(() => {
      if (remainingTime.value > 0) {
        remainingTime.value--
      } else {
        clearInterval(timer)
        submitExamAction()
      }
    }, 1000)
  } catch (err) {
    console.error('Failed to start exam', err)
  } finally {
    loading.value = false
  }
}

function confirmSubmit() {
  const unAns = questions.value.length - answeredCount.value
  let msg = '确定现在交卷吗？'
  if (unAns > 0) {
    msg = `您还有 ${unAns} 道题未作答，确定现在提前交卷吗？`
  }
  if (confirm(msg)) {
    submitExamAction()
  }
}

async function submitExamAction() {
  clearInterval(timer)
  showSheet.value = false
  const timeSpent = configTime.value * 60 - remainingTime.value

  try {
    const res: any = await examApi.submit({
      subject: 'basic',
      time_spent: Math.max(timeSpent, 1),
      answers: answers.value,
    })
    examResult.value = res
    examState.value = 'result'
  } catch (err) {
    console.error('Submit exam failed', err)
  }
}

onUnmounted(() => {
  clearInterval(timer)
})
</script>
