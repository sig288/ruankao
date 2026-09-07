<template>
  <div class="p-4 space-y-4">
    <!-- Top Summary Card -->
    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
      <h2 class="text-sm font-black text-slate-800">软考掌握度评估</h2>

      <div class="grid grid-cols-2 gap-3">
        <div class="bg-blue-50/70 p-3.5 rounded-xl border border-blue-100">
          <div class="text-[11px] text-blue-600 font-bold">综合正确率</div>
          <div class="text-2xl font-black text-blue-900 mt-1">{{ stats.overall_accuracy }}%</div>
          <div class="text-[10px] text-blue-500 mt-0.5">及格线参考：60%</div>
        </div>

        <div class="bg-indigo-50/70 p-3.5 rounded-xl border border-indigo-100">
          <div class="text-[11px] text-indigo-600 font-bold">累计做题量</div>
          <div class="text-2xl font-black text-indigo-900 mt-1">{{ stats.total_answered }}</div>
          <div class="text-[10px] text-indigo-500 mt-0.5">正确 {{ stats.correct_answered }} 题</div>
        </div>
      </div>

      <div class="flex items-center justify-between text-xs pt-1 border-t border-slate-100 text-slate-500">
        <span>已记录错题总数：<b class="text-slate-700">{{ stats.total_wrong }}</b></span>
        <span>待消灭攻坚：<b class="text-rose-600">{{ stats.unmastered_wrong }}</b></span>
      </div>
    </div>

    <!-- Chapter Breakdown Progress Bars -->
    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-xs font-bold text-slate-800 uppercase">各知识领域掌握度</h3>
        <span class="text-[11px] text-slate-400">正确率诊断</span>
      </div>

      <div v-if="stats.chapter_breakdown.length === 0" class="text-center py-6 text-xs text-slate-400">
        暂无章节做题数据，快去「章节练」开启刷题吧！
      </div>

      <div v-else class="space-y-3 pt-1">
        <div v-for="ch in stats.chapter_breakdown" :key="ch.chapter" class="space-y-1">
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-slate-700">{{ ch.chapter }}</span>
            <span class="text-slate-500 font-mono text-[11px]">
              {{ ch.correct }}/{{ ch.total }} (<b :class="getRateColor(ch.accuracy)">{{ ch.accuracy }}%</b>)
            </span>
          </div>

          <!-- Progress bar -->
          <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              class="h-2 rounded-full transition-all duration-500"
              :class="getBarColor(ch.accuracy)"
              :style="{ width: `${Math.min(ch.accuracy, 100)}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Past Mock Exams History -->
    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
      <h3 class="text-xs font-bold text-slate-800 uppercase">历次机考模考记录</h3>

      <div v-if="examHistory.length === 0" class="text-center py-6 text-xs text-slate-400">
        暂无模考记录
      </div>

      <div v-else class="space-y-2.5 divide-y divide-slate-100">
        <div v-for="ex in examHistory" :key="ex.id" class="pt-2.5 first:pt-0 flex items-center justify-between text-xs">
          <div>
            <div class="font-bold text-slate-800">
              {{ ex.subject === 'basic' ? '基础知识单选题' : '案例分析专题' }}
            </div>
            <div class="text-[10px] text-slate-400 mt-0.5">
              {{ formatDate(ex.created_at) }} · 用时 {{ Math.floor(ex.time_spent / 60) }}分
            </div>
          </div>
          <div class="text-right">
            <div class="font-black text-sm" :class="ex.score >= ex.total_score * 0.6 ? 'text-emerald-600' : 'text-rose-600'">
              {{ ex.score }} <span class="text-[10px] font-normal text-slate-400">/ {{ ex.total_score }}</span>
            </div>
            <span
              class="text-[9px] px-1.5 py-0.2 rounded font-bold"
              :class="ex.score >= ex.total_score * 0.6 ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'"
            >
              {{ ex.score >= ex.total_score * 0.6 ? '及格' : '需强化' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { wrongBookApi, examApi } from '@/api'

const stats = ref<any>({
  total_answered: 0,
  correct_answered: 0,
  overall_accuracy: 0,
  total_wrong: 0,
  unmastered_wrong: 0,
  chapter_breakdown: [],
})

const examHistory = ref<any[]>([])

function getRateColor(rate: number) {
  if (rate >= 75) return 'text-emerald-600'
  if (rate >= 60) return 'text-blue-600'
  return 'text-rose-600'
}

function getBarColor(rate: number) {
  if (rate >= 75) return 'bg-emerald-500'
  if (rate >= 60) return 'bg-blue-500'
  return 'bg-rose-500'
}

function formatDate(dtStr: string) {
  if (!dtStr) return ''
  const d = new Date(dtStr)
  return `${d.getMonth() + 1}月${d.getDate()}日 ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

onMounted(async () => {
  try {
    const s: any = await wrongBookApi.getStatistics()
    stats.value = s
    const ex: any = await examApi.history()
    examHistory.value = ex
  } catch (err) {
    console.error('Failed to load statistics', err)
  }
})
</script>
