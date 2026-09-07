<template>
  <div class="p-4 space-y-4">
    <!-- Header Selection -->
    <div class="bg-white p-3.5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
      <div class="flex-1 mr-2">
        <label class="block text-[10px] font-bold text-slate-400 uppercase">案例分析题目</label>
        <select
          v-model="selectedQId"
          @change="loadSelectedCase"
          class="w-full bg-transparent font-bold text-slate-800 text-sm focus:outline-none truncate"
        >
          <option v-for="(q, idx) in caseQuestions" :key="q.id" :value="q.id">
            案例 {{ idx + 1 }}：{{ q.knowledge }}
          </option>
        </select>
      </div>
      <span class="px-2 py-0.5 bg-emerald-50 text-emerald-700 text-xs font-bold rounded-lg border border-emerald-200">
        应用技术
      </span>
    </div>

    <div v-if="loading" class="text-center py-12 text-slate-400 text-sm">
      正在加载案例题...
    </div>

    <!-- Case Question Detail -->
    <div v-else-if="currentCase" class="space-y-4">
      <!-- Stem Card -->
      <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500">{{ currentCase.chapter }} · {{ currentCase.knowledge }}</span>
          <span class="text-xs font-bold text-emerald-600">满分：{{ totalCaseScore }} 分</span>
        </div>

        <div class="text-xs text-slate-800 leading-relaxed whitespace-pre-line bg-slate-50 p-4 rounded-xl border border-slate-100 font-sans">
          {{ currentCase.stem }}
        </div>
      </div>

      <!-- User Answer Input -->
      <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <label class="text-xs font-bold text-slate-800">考生作答区</label>
          <span class="text-[11px] text-slate-400">支持分点编写（如 1. 2. 3.）</span>
        </div>

        <textarea
          v-model="userAnswerText"
          rows="7"
          class="w-full p-3.5 bg-slate-50 border border-slate-300 rounded-xl text-xs leading-relaxed focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white"
          placeholder="请在此输入您的解答（例如计算过程、偏差原因、纠偏措施等）..."
        ></textarea>

        <button
          @click="handleGradeCase"
          :disabled="grading || !userAnswerText.trim()"
          class="w-full py-3 bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] text-white font-bold rounded-xl text-xs shadow-md transition-all disabled:opacity-50 flex items-center justify-center space-x-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ grading ? '采分点引擎评估中...' : '提交并进行关键词智能采分' }}</span>
        </button>
      </div>

      <!-- Grading Results & Model Answer -->
      <div v-if="gradeResult" class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4 animate-fade-in">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 class="text-sm font-black text-slate-800">智能采分结果</h3>
            <p class="text-[11px] text-slate-500">基于软考阅卷采分点关键词匹配</p>
          </div>
          <div class="text-right">
            <span class="text-xl font-black text-emerald-600">{{ gradeResult.earned_score }}</span>
            <span class="text-xs text-slate-400"> / {{ gradeResult.total_score }} 分</span>
          </div>
        </div>

        <!-- Rubric Items Breakdown -->
        <div class="space-y-2.5">
          <h4 class="text-xs font-bold text-slate-700">采分点命中明细：</h4>
          <div
            v-for="(r, idx) in gradeResult.rubric_results"
            :key="idx"
            class="p-3 rounded-xl border text-xs leading-relaxed space-y-1"
            :class="r.is_hit ? 'bg-emerald-50/70 border-emerald-200' : 'bg-rose-50/50 border-rose-200'"
          >
            <div class="flex items-center justify-between font-bold">
              <span :class="r.is_hit ? 'text-emerald-800' : 'text-rose-800'">
                {{ idx + 1 }}. {{ r.point }}
              </span>
              <span :class="r.is_hit ? 'text-emerald-700 font-mono' : 'text-rose-600 font-mono'">
                +{{ r.earned_score }} / {{ r.max_score }}分
              </span>
            </div>
            <div class="text-[11px] text-slate-500 flex flex-wrap gap-1 items-center pt-1">
              <span>命中词：</span>
              <span v-for="kw in r.matched_keywords" :key="kw" class="px-1.5 py-0.2 bg-emerald-200/80 text-emerald-900 rounded font-mono text-[10px]">
                {{ kw }}
              </span>
              <span v-if="r.matched_keywords.length === 0" class="text-slate-400 italic">未命中</span>
            </div>
          </div>
        </div>

        <!-- Official Reference Answer -->
        <div class="pt-3 border-t border-slate-100">
          <h4 class="text-xs font-bold text-slate-800 mb-2">【官方标准参考答案与得分要点】</h4>
          <div class="bg-slate-50 p-4 rounded-xl text-xs text-slate-700 leading-relaxed whitespace-pre-line border border-slate-100">
            {{ currentCase.correct_answer }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { questionApi, practiceApi } from '@/api'

const caseQuestions = ref<any[]>([])
const selectedQId = ref('')
const currentCase = ref<any>(null)
const loading = ref(false)
const grading = ref(false)
const userAnswerText = ref('')
const gradeResult = ref<any>(null)

const totalCaseScore = computed(() => {
  if (!currentCase.value?.rubrics) return 15
  return currentCase.value.rubrics.reduce((sum: number, r: any) => sum + (r.score || 0), 0)
})

async function loadCaseQuestions() {
  loading.value = true
  try {
    const res: any = await questionApi.list({ subject: 'case', limit: 20 })
    caseQuestions.value = res
    if (res.length > 0) {
      selectedQId.value = res[0].id
      await loadSelectedCase()
    }
  } catch (err) {
    console.error('Failed to load case questions', err)
  } finally {
    loading.value = false
  }
}

async function loadSelectedCase() {
  if (!selectedQId.value) return
  try {
    const q: any = await questionApi.getDetail(selectedQId.value)
    currentCase.value = q
    userAnswerText.value = ''
    gradeResult.value = null
  } catch (err) {
    console.error('Failed to get case detail', err)
  }
}

async function handleGradeCase() {
  if (!currentCase.value || !userAnswerText.value.trim()) return
  grading.value = true
  try {
    const res: any = await practiceApi.submit({
      question_id: currentCase.value.id,
      user_answer: userAnswerText.value,
    })
    gradeResult.value = res
  } catch (err) {
    console.error('Grading failed', err)
  } finally {
    grading.value = false
  }
}

onMounted(() => {
  loadCaseQuestions()
})
</script>
