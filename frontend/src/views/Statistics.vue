<template>
  <div class="p-4 space-y-4 pb-24">
    <!-- Readiness Score Card -->
    <div class="bg-gradient-to-br from-indigo-600 via-blue-600 to-sky-600 rounded-3xl p-5 text-white shadow-xl relative overflow-hidden">
      <div class="relative z-10 flex items-center justify-between">
        <div>
          <span class="text-[11px] font-medium tracking-wider uppercase opacity-85">第3版大纲 · 综合备考胜率指数</span>
          <div class="flex items-baseline space-x-1.5 mt-1">
            <span class="text-4xl font-black tracking-tight font-mono">{{ masteryData?.overall_readiness ?? 0 }}</span>
            <span class="text-sm font-semibold opacity-90">/ 100</span>
          </div>
          <p class="text-xs opacity-75 mt-1">
            已覆盖 {{ masteryData?.total_practiced ?? 0 }} 题 · 题库总量 {{ masteryData?.total_in_bank ?? 0 }} 题
          </p>
        </div>

        <div class="w-16 h-16 rounded-full border-4 border-white/20 flex items-center justify-center font-bold text-lg bg-white/10 backdrop-blur-md">
          {{ getReadinessGrade(masteryData?.overall_readiness || 0) }}
        </div>
      </div>
    </div>

    <!-- P0 Highlight: Weakness-driven Practice Banner (M5) -->
    <div class="bg-gradient-to-r from-rose-500 to-amber-500 rounded-2xl p-4 text-white shadow-lg flex items-center justify-between">
      <div class="space-y-0.5">
        <div class="flex items-center space-x-1.5">
          <span class="text-base">🎯</span>
          <h3 class="text-sm font-bold">薄弱点精准突击组卷</h3>
        </div>
        <p class="text-xs opacity-90">
          检测到 {{ masteryData?.weak_chapters?.length || 0 }} 个薄弱知识领域，智能组装 10 题靶向专项练
        </p>
      </div>

      <button
        @click="startWeakDrill"
        :disabled="drillLoading"
        class="px-3.5 py-2 bg-white text-rose-600 rounded-xl text-xs font-bold shadow-md hover:bg-rose-50 active:scale-95 transition-all whitespace-nowrap"
      >
        {{ drillLoading ? '组卷中...' : '立即开练 →' }}
      </button>
    </div>

    <!-- Dimension Toggle: 17 Chapters vs 10 Domains -->
    <div class="bg-slate-200 dark:bg-slate-700 p-1 rounded-xl flex space-x-1">
      <button
        @click="activeDimension = 'chapters'"
        class="flex-1 py-1.5 text-xs font-semibold rounded-lg transition-all"
        :class="activeDimension === 'chapters' ? 'bg-white dark:bg-slate-800 text-blue-600 dark:text-blue-400 shadow-sm' : 'text-slate-600 dark:text-slate-300'"
      >
        按 17 章大纲维度 ({{ masteryData?.chapters?.length || 0 }})
      </button>
      <button
        @click="activeDimension = 'domains'"
        class="flex-1 py-1.5 text-xs font-semibold rounded-lg transition-all"
        :class="activeDimension === 'domains' ? 'bg-white dark:bg-slate-800 text-blue-600 dark:text-blue-400 shadow-sm' : 'text-slate-600 dark:text-slate-300'"
      >
        按 十大管理领域 ({{ masteryData?.domains?.length || 0 }})
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="py-12 text-center text-slate-400 text-xs">
      正在计算您的各考点掌握度模型...
    </div>

    <!-- Mastery Item List -->
    <div v-else class="space-y-3">
      <div
        v-for="item in currentList"
        :key="item.name"
        class="bg-white dark:bg-slate-800 rounded-2xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm space-y-2.5 transition-all"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span
              class="text-[10px] px-2 py-0.5 rounded-full font-bold uppercase"
              :class="getLevelBadgeClass(item.level)"
            >
              {{ getLevelText(item.level) }}
            </span>
            <h4 class="text-xs font-bold text-slate-800 dark:text-white">{{ item.name }}</h4>
          </div>

          <div class="flex items-center space-x-2">
            <span v-if="item.trend_7d !== undefined && item.trend_7d !== 0" class="text-[10px] font-medium" :class="item.trend_7d > 0 ? 'text-emerald-500' : 'text-rose-500'">
              {{ item.trend_7d > 0 ? '↑ +' : '↓ ' }}{{ Math.round(item.trend_7d * 100) }}% 7天趋势
            </span>
            <router-link
              :to="`/practice?chapter=${encodeURIComponent(item.name)}`"
              class="text-[11px] text-blue-600 dark:text-blue-400 hover:underline font-medium"
            >
              练本章 →
            </router-link>
          </div>
        </div>

        <!-- Metrics Progress -->
        <div class="grid grid-cols-2 gap-3 pt-1">
          <div>
            <div class="flex justify-between text-[11px] text-slate-500 mb-1">
              <span>覆盖度</span>
              <span class="font-mono">{{ item.practiced_questions }}/{{ item.total_questions }} ({{ Math.round((item.coverage_rate || 0) * 100) }}%)</span>
            </div>
            <div class="w-full bg-slate-100 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
              <div
                class="bg-blue-600 h-full rounded-full"
                :style="{ width: `${Math.min(100, Math.round((item.coverage_rate || 0) * 100))}%` }"
              ></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-[11px] text-slate-500 mb-1">
              <span>正确率 (30天)</span>
              <span class="font-mono">
                {{ item.accuracy_rate !== null ? `${Math.round(item.accuracy_rate * 100)}%` : '未答' }}
              </span>
            </div>
            <div class="w-full bg-slate-100 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full"
                :class="item.accuracy_rate && item.accuracy_rate >= 0.8 ? 'bg-emerald-500' : item.accuracy_rate && item.accuracy_rate >= 0.6 ? 'bg-amber-500' : 'bg-rose-500'"
                :style="{ width: `${item.accuracy_rate !== null ? Math.round(item.accuracy_rate * 100) : 0}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { masteryApi } from '@/api'
import { haptics } from '@/utils/haptics'

const router = useRouter()
const loading = ref(false)
const drillLoading = ref(false)
const activeDimension = ref<'chapters' | 'domains'>('chapters')
const masteryData = ref<any>(null)

const currentList = computed(() => {
  if (!masteryData.value) return []
  return activeDimension.value === 'chapters'
    ? masteryData.value.chapters
    : masteryData.value.domains
})

onMounted(() => {
  fetchMastery()
})

async function fetchMastery() {
  loading.value = true
  try {
    const res = await masteryApi.getMe() as any
    masteryData.value = res
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function startWeakDrill() {
  haptics.click()
  drillLoading.value = true
  try {
    // Jump to practice in weak mode
    router.push('/practice?mode=weak')
  } catch (e: any) {
    alert(e.message || '组卷失败')
  } finally {
    drillLoading.value = false
  }
}

function getReadinessGrade(score: number): string {
  if (score >= 85) return 'A+'
  if (score >= 70) return 'A'
  if (score >= 60) return 'B'
  if (score >= 45) return '及格'
  return '待冲刺'
}

function getLevelText(level: string): string {
  if (level === 'strong') return '强项'
  if (level === 'medium') return '中等'
  if (level === 'weak') return '薄弱'
  return '未练'
}

function getLevelBadgeClass(level: string): string {
  if (level === 'strong') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300'
  if (level === 'medium') return 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300'
  if (level === 'weak') return 'bg-rose-100 text-rose-700 dark:bg-rose-900/50 dark:text-rose-300 animate-pulse'
  return 'bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-300'
}
</script>
