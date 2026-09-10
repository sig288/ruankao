<template>
  <div class="rk-page">
    <div class="rk-card p-3 flex items-center justify-between">
      <div class="flex items-center gap-2 min-w-0">
        <router-link to="/learn/points" class="p-1.5 min-w-[36px] min-h-[36px] flex items-center justify-center text-muted">
          ‹
        </router-link>
        <div class="min-w-0">
          <span class="text-[10px] text-pine-600 font-mono font-bold">{{ point?.chapter_id }}</span>
          <h2 class="text-[12px] font-bold text-ink-800 truncate">{{ point?.chapter_title || '考点精析' }}</h2>
        </div>
      </div>
      <router-link to="/learn/points" class="text-[11px] px-2.5 py-1 bg-paper-100 rounded-lg text-ink-700">目录</router-link>
    </div>

    <div v-if="loading" class="text-center py-20 text-muted text-xs">正在打开讲义…</div>

    <div v-else-if="point" class="space-y-3">
      <div class="rk-card p-4 space-y-3">
        <div class="flex items-center gap-2">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold" :class="getFrequencyBadge(point.frequency)">
            {{ getFrequencyLabel(point.frequency) }}
          </span>
          <span class="text-[11px] text-muted">约 {{ point.est_minutes }} 分钟</span>
        </div>
        <h1 class="text-base font-black text-ink-800 leading-snug">{{ point.title }}</h1>
        <div v-if="point.domain_tags?.length" class="flex flex-wrap gap-1.5">
          <span v-for="tag in point.domain_tags" :key="tag" class="px-2 py-0.5 bg-pine-50 text-pine-700 text-[10px] rounded-md">
            {{ tag }}
          </span>
        </div>
        <div class="pt-3 border-t border-paper-200 flex items-center justify-between gap-2">
          <span class="text-[11px] text-muted">掌握状态</span>
          <div class="flex gap-1">
            <button
              v-for="s in statusOptions"
              :key="s.value"
              @click="setStatus(s.value)"
              class="px-2.5 py-1 rounded-lg text-[11px] font-bold min-h-[32px]"
              :class="point.status === s.value ? 'bg-ink-800 text-paper-50' : 'bg-paper-100 text-muted'"
            >
              {{ s.label }}
            </button>
          </div>
        </div>
      </div>

      <div class="rk-card p-4 space-y-1">
        <h3 class="text-[13px] font-black text-ink-800 mb-1">考点精析</h3>
        <MarkdownBody :source="point.summary_md" />
      </div>

      <div v-if="point.formula_md" class="rk-card p-4 bg-cinnabar-50 border-cinnabar-100 space-y-2">
        <h3 class="text-[13px] font-black text-cinnabar-700">考场口诀</h3>
        <MarkdownBody :source="point.formula_md" />
      </div>

      <div v-if="point.glossary_terms && point.glossary_terms.length > 0" class="rk-card p-4 space-y-2.5">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <span class="text-sm">🔤</span>
            <h3 class="text-[13px] font-black text-ink-800">相关英语术语</h3>
          </div>
          <router-link to="/learn/glossary" class="text-[11px] text-pine-600 font-bold hover:underline">全部词库 ›</router-link>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <router-link
            v-for="term in point.glossary_terms"
            :key="term.id"
            :to="`/learn/glossary/${term.id}`"
            class="p-3 rounded-xl bg-paper-100 border border-paper-200 hover:border-indigo-300 hover:bg-white transition-all block group"
          >
            <div class="flex items-center justify-between">
              <span class="text-xs font-black font-mono text-indigo-700 group-hover:text-indigo-900">{{ term.term_en }}</span>
              <span
                class="text-[9px] px-1.5 py-0.2 rounded font-bold"
                :class="term.frequency === 'high' ? 'bg-rose-100 text-rose-700' : 'bg-paper-200 text-muted'"
              >
                {{ term.frequency === 'high' ? '高频' : '常用' }}
              </span>
            </div>
            <div class="text-xs font-semibold text-ink-800 mt-1">{{ term.term_zh }}</div>
            <p v-if="term.tip" class="text-[10px] text-muted truncate mt-1">{{ term.tip }}</p>
          </router-link>
        </div>
      </div>

      <div class="rk-card p-4 space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-[13px] font-black text-ink-800">相关例题</h3>
            <p class="text-[10px] text-muted mt-0.5">真题与模拟题 · 精准匹配本考点</p>
          </div>
          <router-link
            v-if="practiceQuestions.length > 0"
            :to="{ path: '/practice', query: { point_id: point.id, title: point.title } }"
            class="px-3 py-1.5 bg-pine-600 hover:bg-pine-700 text-paper-50 rounded-xl text-xs font-bold shadow-xs active:scale-95 transition-all flex items-center gap-1"
          >
            <span>开始刷题 ({{ practiceQuestions.length }})</span>
            <span>›</span>
          </router-link>
          <button
            v-else
            disabled
            class="px-2.5 py-1 bg-paper-100 text-muted rounded-lg text-xs font-medium cursor-not-allowed opacity-60"
          >
            暂无例题
          </button>
        </div>

        <div v-if="practiceLoading" class="text-center py-6 text-muted text-xs">调取例题…</div>
        <div v-else-if="practiceQuestions.length === 0" class="py-6 text-center text-xs text-muted bg-paper-50 rounded-xl border border-dashed border-paper-200">
          <p class="font-medium text-ink-700">该考点题库正在收录中</p>
          <p class="text-[10px] text-muted mt-1">您可以前往章节题库进行综合强化训练</p>
          <router-link to="/practice" class="inline-block mt-3 px-3 py-1.5 bg-paper-100 text-pine-700 font-bold rounded-lg border border-paper-200 hover:bg-paper-200 transition-colors">
            去章节练习 ›
          </router-link>
        </div>
        <div v-else class="space-y-3">
          <div v-for="(q, qIdx) in practiceQuestions" :key="q.id" class="p-3 rounded-xl border border-paper-200 bg-paper-100/50 space-y-2">
            <div class="flex items-center justify-between text-[11px] text-muted">
              <span>第 {{ qIdx + 1 }} 题</span>
              <span>{{ q.subject === 'case' ? '案例' : '选择' }}</span>
            </div>
            <div class="text-[12px] font-semibold text-ink-800 leading-relaxed">{{ q.stem }}</div>
            <div v-if="q.options" class="space-y-2">
              <button
                v-for="(opt, oIdx) in q.options"
                :key="oIdx"
                @click="selectOption(q.id, getOptKey(opt, oIdx))"
                class="w-full text-left p-2.5 rounded-xl border text-[12px] leading-relaxed flex items-start gap-2.5 min-h-[44px]"
                :class="getOptionClass(q.id, getOptKey(opt, oIdx))"
              >
                <span class="w-5 h-5 rounded-full flex items-center justify-center font-bold text-[11px] shrink-0" :class="getBadgeClass(q.id, getOptKey(opt, oIdx))">
                  {{ getOptKey(opt, oIdx) }}
                </span>
                <span class="pt-0.5 flex-1">{{ cleanOptText(opt) }}</span>
              </button>
            </div>
            <div v-else class="p-3 bg-paper-50 rounded-xl text-xs text-muted">
              案例请到专题作答。
              <router-link to="/case-exam" class="text-pine-600 font-bold ml-1">前往 ›</router-link>
            </div>
            <div v-if="userAnswers[q.id]" class="p-3 rounded-xl bg-paper-50 border border-paper-200 text-xs space-y-2">
              <div class="flex items-center justify-between">
                <span class="font-bold" :class="isAnswerCorrect(q) ? 'text-pine-600' : 'text-cinnabar-600'">
                  {{ isAnswerCorrect(q) ? '回答正确' : '回答错误' }}
                </span>
                <span class="text-muted">答案 <b class="text-pine-600 font-mono">{{ q.correct_answer || '见解析' }}</b></span>
              </div>
              <div v-if="q.analysis" class="text-muted pt-1 border-t border-paper-200">
                <b class="text-ink-800">解析：</b>{{ q.analysis }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { learnApi, questionApi } from '@/api'
import { triggerHaptic } from '@/utils/haptics'
import MarkdownBody from '@/components/MarkdownBody.vue'

const route = useRoute()
function currentPointId() {
  return String(route.params.id || '')
}

const loading = ref(true)
const point = ref<any>(null)
const practiceLoading = ref(true)
const practiceQuestions = ref<any[]>([])
const userAnswers = ref<Record<string, string>>({})

const statusOptions = [
  { value: 'unlearned', label: '未学' },
  { value: 'learning', label: '学习中' },
  { value: 'mastered', label: '已掌握' },
]

async function loadPoint() {
  loading.value = true
  try {
    const res = await learnApi.getPointDetail(currentPointId())
    point.value = res
  } catch (err) {
    console.error('Failed to load point detail:', err)
  } finally {
    loading.value = false
  }
}

async function loadPractice() {
  practiceLoading.value = true
  try {
    const res = await learnApi.getPointPractice(currentPointId(), 5)
    const detailedQs = []
    for (const item of (res.items || [])) {
      try {
        const fullQ = await questionApi.getDetail(item.id)
        detailedQs.push(fullQ)
      } catch {
        detailedQs.push(item)
      }
    }
    practiceQuestions.value = detailedQs
  } catch (err) {
    console.error('Failed to load practice questions:', err)
  } finally {
    practiceLoading.value = false
  }
}

async function setStatus(status: string) {
  triggerHaptic('tap')
  try {
    await learnApi.updatePointStatus(currentPointId(), status)
    if (point.value) point.value.status = status
    if (status === 'mastered') triggerHaptic('success')
  } catch (err) {
    console.error('Failed to update status:', err)
  }
}

function selectOption(questionId: string, choiceKey: string) {
  if (userAnswers.value[questionId]) return
  userAnswers.value[questionId] = choiceKey
  const q = practiceQuestions.value.find(x => x.id === questionId)
  triggerHaptic(q && q.correct_answer === choiceKey ? 'success' : 'error')
}

function isAnswerCorrect(q: any): boolean {
  return userAnswers.value[q.id] === q.correct_answer
}

function getOptKey(opt: string, idx: number): string {
  if (/^[A-D][.、\s]/.test(opt)) return opt[0]
  return ['A', 'B', 'C', 'D'][idx] || 'A'
}

function cleanOptText(opt: string): string {
  return opt.replace(/^[A-D][.、\s]+/, '')
}

function getOptionClass(questionId: string, key: string) {
  const selected = userAnswers.value[questionId]
  if (!selected) return 'bg-paper-50 border-paper-200'
  const q = practiceQuestions.value.find(x => x.id === questionId)
  if (q && q.correct_answer === key) return 'bg-pine-50 border-pine-600 text-pine-700 font-semibold'
  if (selected === key) return 'bg-cinnabar-50 border-cinnabar-600 text-cinnabar-700 font-semibold'
  return 'bg-paper-50 border-paper-200 opacity-60'
}

function getBadgeClass(questionId: string, key: string) {
  const selected = userAnswers.value[questionId]
  if (!selected) return 'bg-paper-200 text-ink-800'
  const q = practiceQuestions.value.find(x => x.id === questionId)
  if (q && q.correct_answer === key) return 'bg-pine-600 text-white'
  if (selected === key) return 'bg-cinnabar-600 text-white'
  return 'bg-paper-200 text-muted'
}

function getFrequencyBadge(freq: string) {
  if (freq === 'high') return 'bg-cinnabar-50 text-cinnabar-700'
  if (freq === 'mid') return 'bg-paper-200 text-ink-700'
  return 'bg-paper-100 text-muted'
}

function getFrequencyLabel(freq: string) {
  if (freq === 'high') return '高频核心'
  if (freq === 'mid') return '常考'
  return '基础'
}

onMounted(() => {
  loadPoint()
  loadPractice()
})

watch(
  () => route.params.id,
  (id) => {
    if (!id) return
    userAnswers.value = {}
    loadPoint()
    loadPractice()
  }
)
</script>
