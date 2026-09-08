<template>
  <div class="rk-page">
    <section class="rk-card overflow-hidden relative bg-ink-800 text-paper-50 p-4">
      <p class="text-[10px] tracking-widest text-paper-300 uppercase">{{ greeting }} · {{ authStore.username }}</p>
      <div class="mt-2 flex items-end justify-between gap-3">
        <div>
          <h2 class="text-lg font-black leading-tight">灯下备考，拿下中项</h2>
          <p class="text-[11px] text-paper-300 mt-1">选择 75 分 · 案例计算与问答</p>
        </div>
        <div class="text-right shrink-0">
          <div class="text-[10px] text-paper-300">距考试</div>
          <div class="text-2xl font-black font-mono text-cinnabar-100 leading-none">
            {{ plan?.days_remaining ?? '--' }}
            <span class="text-[10px] font-semibold text-paper-300">天</span>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-white/10 text-center">
        <div>
          <div class="text-base font-black">{{ stats.total_answered }}</div>
          <div class="text-[10px] text-paper-300">已刷题</div>
        </div>
        <div>
          <div class="text-base font-black">{{ stats.overall_accuracy }}%</div>
          <div class="text-[10px] text-paper-300">正确率</div>
        </div>
        <div>
          <div class="text-base font-black text-cinnabar-100">{{ stats.unmastered_wrong }}</div>
          <div class="text-[10px] text-paper-300">待消灭</div>
        </div>
      </div>
    </section>

    <section v-if="plan" class="rk-card p-3.5">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-[11px] font-bold text-ink-800">今日打卡 {{ completedTodayCount }}/{{ plan.today_tasks?.length || 0 }}</p>
          <p class="text-[10px] text-muted mt-0.5">目标 {{ plan.exam_date }}</p>
        </div>
        <router-link to="/plan" class="text-[11px] font-bold text-pine-600">计划 ›</router-link>
      </div>
      <div v-if="plan.today_tasks?.length" class="mt-2 space-y-1.5">
        <div
          v-for="task in plan.today_tasks.slice(0, 2)"
          :key="task.id"
          class="flex items-center justify-between text-[11px] px-2 py-1.5 rounded-lg bg-paper-100"
        >
          <span class="truncate" :class="{ 'line-through text-muted': task.is_completed }">
            {{ task.is_completed ? '✓' : '○' }} {{ task.title }}
          </span>
          <span class="font-mono text-[10px] text-muted shrink-0">{{ task.estimated_minutes }}′</span>
        </div>
      </div>
    </section>

    <section class="grid grid-cols-2 gap-2.5">
      <router-link to="/learn/points" class="rk-card p-3.5 active:scale-[0.98] transition">
        <div class="w-9 h-9 rounded-xl bg-pine-100 text-pine-700 flex items-center justify-center text-sm font-black">学</div>
        <h3 class="text-[13px] font-black text-ink-800 mt-2.5">考点知识树</h3>
        <p class="text-[10px] text-muted mt-0.5">17章精析 · 口诀速记</p>
      </router-link>

      <router-link to="/practice" class="rk-card p-3.5 active:scale-[0.98] transition">
        <div class="w-9 h-9 rounded-xl bg-cinnabar-50 text-cinnabar-700 flex items-center justify-center text-sm font-black">练</div>
        <h3 class="text-[13px] font-black text-ink-800 mt-2.5">章节专项练</h3>
        <p class="text-[10px] text-muted mt-0.5">按领域拆开刷</p>
      </router-link>

      <router-link to="/mock-exam" class="rk-card p-3.5 active:scale-[0.98] transition">
        <div class="w-9 h-9 rounded-xl bg-ink-100 text-ink-700 flex items-center justify-center text-sm font-black">考</div>
        <h3 class="text-[13px] font-black text-ink-800 mt-2.5">全真机考</h3>
        <p class="text-[10px] text-muted mt-0.5">75题 · 120分钟</p>
      </router-link>

      <router-link to="/case-exam" class="rk-card p-3.5 active:scale-[0.98] transition">
        <div class="w-9 h-9 rounded-xl bg-paper-200 text-ink-700 flex items-center justify-center text-sm font-black">例</div>
        <h3 class="text-[13px] font-black text-ink-800 mt-2.5">案例分析</h3>
        <p class="text-[10px] text-muted mt-0.5">计算与关键词采分</p>
      </router-link>
    </section>

    <router-link
      to="/practice?mode=weak"
      class="rk-card p-3.5 flex items-center justify-between bg-cinnabar-50 border-cinnabar-100"
    >
      <div>
        <p class="text-[13px] font-black text-cinnabar-700">薄弱点突击</p>
        <p class="text-[10px] text-cinnabar-600 mt-0.5">错题 + 弱章动态组卷</p>
      </div>
      <span class="text-[11px] font-bold text-cinnabar-700">开练 ›</span>
    </router-link>

    <router-link
      v-if="!inApp"
      to="/download"
      class="rk-card p-3.5 flex items-center justify-between"
    >
      <div>
        <p class="text-[13px] font-black text-ink-800">下载 Android 客户端</p>
        <p class="text-[10px] text-muted mt-0.5">官方 APK · 安装到手机主屏</p>
      </div>
      <span class="text-[11px] font-bold text-pine-600">下载 ›</span>
    </router-link>

    <section class="grid grid-cols-4 gap-2">
      <router-link to="/learn/glossary" class="rk-card p-2.5 text-center">
        <div class="text-sm">词</div>
        <div class="text-[10px] font-bold text-ink-800 mt-1">英语词表</div>
      </router-link>
      <router-link to="/statistics" class="rk-card p-2.5 text-center">
        <div class="text-sm">图</div>
        <div class="text-[10px] font-bold text-ink-800 mt-1">掌握度</div>
      </router-link>
      <router-link to="/materials" class="rk-card p-2.5 text-center">
        <div class="text-sm">档</div>
        <div class="text-[10px] font-bold text-ink-800 mt-1">备考文库</div>
      </router-link>
      <router-link to="/favorites" class="rk-card p-2.5 text-center">
        <div class="text-sm">藏</div>
        <div class="text-[10px] font-bold text-ink-800 mt-1">收藏</div>
      </router-link>
    </section>

    <section class="rk-card p-3.5">
      <div class="flex items-center justify-between mb-2.5">
        <h3 class="text-[11px] font-black text-ink-800">高频必背热区</h3>
        <router-link to="/learn/points" class="text-[10px] font-bold text-pine-600">知识树 ›</router-link>
      </div>
      <div class="flex flex-wrap gap-1.5">
        <router-link
          v-for="item in highFreqTopics"
          :key="item.name"
          :to="item.to"
          class="px-2.5 py-1.5 rounded-xl bg-paper-100 text-[11px] text-ink-800 border border-paper-200"
        >
          {{ item.name }}
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { wrongBookApi, planApi } from '@/api'
import { useAuthStore } from '@/store/auth'
import { isNativeApp } from '@/version'

const authStore = useAuthStore()
const inApp = isNativeApp()

const stats = ref({
  total_answered: 0,
  overall_accuracy: 0.0,
  unmastered_wrong: 0,
})

const plan = ref<any>(null)

const completedTodayCount = computed(() => {
  if (!plan.value?.today_tasks) return 0
  return plan.value.today_tasks.filter((t: any) => t.is_completed).length
})

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 11) return '早安'
  if (h < 14) return '午安'
  if (h < 18) return '下午好'
  return '夜读'
})

const highFreqTopics = [
  { name: '挣值 EVM', to: '/learn/points/kp_evm_cpi' },
  { name: '关键路径', to: '/learn/points/kp_cpm_float' },
  { name: '整体变更', to: '/learn/points/kp_ccb_change' },
  { name: '配置三库', to: '/learn/points/kp_ch07_config_baseline' },
  { name: '进度成本四象限', to: '/learn/points/kp_ch09_quad_measures' },
  { name: '八大绩效域', to: '/learn/points/kp_perf_domains_overview' },
]

onMounted(async () => {
  try {
    const res: any = await wrongBookApi.getStatistics()
    stats.value = res
  } catch (err) {
    console.error('Failed to load stats', err)
  }

  try {
    const planRes: any = await planApi.getMe()
    plan.value = planRes
  } catch (err) {
    console.error('Failed to load plan', err)
  }
})
</script>
