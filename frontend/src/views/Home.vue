<template>
  <div class="ios-page space-y-4">
    <!-- Today Large Title & Top Meta -->
    <div class="pt-2 px-1 flex items-baseline justify-between">
      <div>
        <p class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{{ todayDateStr }}</p>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight mt-0.5">今天</h1>
      </div>

      <!-- AI Status Capsule (D4) -->
      <div
        class="ios-pill text-[11px] cursor-pointer active:scale-95 transition"
        :class="aiStatusClass"
        @click="showAiTip"
      >
        <span class="w-1.5 h-1.5 rounded-full" :class="aiDotClass"></span>
        <span>{{ aiStatusText }}</span>
      </div>
    </div>

    <!-- Summary KPI Card -->
    <div class="ios-card p-4">
      <div class="flex items-center justify-between">
        <div>
          <span class="text-xs font-medium text-slate-400">备考进度</span>
          <p class="text-base font-bold text-slate-800 mt-0.5">{{ greeting }}，{{ authStore.username }}</p>
        </div>
        <div v-if="plan?.days_remaining !== undefined" class="text-right">
          <span class="text-[10px] font-medium text-slate-400">距离考试</span>
          <div class="text-xl font-black font-mono text-[#007AFF] leading-none mt-0.5">
            {{ plan.days_remaining }} <span class="text-xs font-semibold text-slate-400">天</span>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-100 text-center">
        <div>
          <div class="text-lg font-bold font-mono text-slate-800">{{ stats.total_answered }}</div>
          <div class="text-[11px] text-slate-400 font-medium">已刷题</div>
        </div>
        <div>
          <div class="text-lg font-bold font-mono text-[#34C759]">{{ stats.overall_accuracy }}%</div>
          <div class="text-[11px] text-slate-400 font-medium">正确率</div>
        </div>
        <div>
          <div class="text-lg font-bold font-mono text-[#FF3B30]">{{ stats.unmastered_wrong }}</div>
          <div class="text-[11px] text-slate-400 font-medium">待消灭错题</div>
        </div>
      </div>
    </div>

    <!-- Daily Study Plan Punch-in -->
    <div v-if="plan" class="ios-card p-3.5">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded-full bg-blue-50 text-[#007AFF] flex items-center justify-center text-xs font-bold">✓</div>
          <span class="text-[13px] font-bold text-slate-800">今日打卡 ({{ completedTodayCount }}/{{ plan.today_tasks?.length || 0 }})</span>
        </div>
        <router-link to="/plan" class="text-xs font-medium text-[#007AFF] hover:underline">查看计划 ›</router-link>
      </div>

      <div v-if="plan.today_tasks?.length" class="mt-2.5 space-y-1.5">
        <div
          v-for="task in plan.today_tasks.slice(0, 2)"
          :key="task.id"
          class="flex items-center justify-between text-xs px-3 py-2 rounded-xl bg-slate-50 border border-slate-100/80"
        >
          <span class="truncate" :class="{ 'line-through text-slate-400': task.is_completed }">
            {{ task.is_completed ? '●' : '○' }} {{ task.title }}
          </span>
          <span class="font-mono text-[11px] text-slate-400 shrink-0 ml-2">{{ task.estimated_minutes }}分钟</span>
        </div>
      </div>
    </div>

    <!-- Group 1: Core Exam Modules (Inset Grouped) -->
    <div class="ios-group">
      <div class="ios-group-header">核心备考</div>
      <div class="ios-card">
        <router-link to="/learn/points" class="ios-row">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-xl bg-blue-50 text-[#007AFF] flex items-center justify-center font-bold text-sm">学</div>
            <div>
              <div class="text-sm font-semibold text-slate-800">考点知识树</div>
              <div class="text-[11px] text-slate-400">83 个考点精析 · 关联例题专练</div>
            </div>
          </div>
          <span class="text-slate-300 font-bold text-sm">›</span>
        </router-link>

        <router-link to="/practice" class="ios-row">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-xl bg-indigo-50 text-[#5856D6] flex items-center justify-center font-bold text-sm">练</div>
            <div>
              <div class="text-sm font-semibold text-slate-800">章节专项刷题</div>
              <div class="text-[11px] text-slate-400">按领域拆分 · 专注做题模式</div>
            </div>
          </div>
          <span class="text-slate-300 font-bold text-sm">›</span>
        </router-link>

        <router-link to="/mock-exam" class="ios-row">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-xl bg-emerald-50 text-[#34C759] flex items-center justify-center font-bold text-sm">考</div>
            <div>
              <div class="text-sm font-semibold text-slate-800">全真机考模拟</div>
              <div class="text-[11px] text-slate-400">75 题 · 120 分钟标准全真考场</div>
            </div>
          </div>
          <span class="text-slate-300 font-bold text-sm">›</span>
        </router-link>

        <router-link to="/case-exam" class="ios-row">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-xl bg-purple-50 text-[#AF52DE] flex items-center justify-center font-bold text-sm">例</div>
            <div>
              <div class="text-sm font-semibold text-slate-800">案例分析专题</div>
              <div class="text-[11px] text-slate-400">计算公式推导 · 阅卷采分点拆解</div>
            </div>
          </div>
          <span class="text-slate-300 font-bold text-sm">›</span>
        </router-link>
      </div>
    </div>

    <!-- Group 2: Weakness & Tooling (Inset Grouped) -->
    <div class="ios-group">
      <div class="ios-group-header">提分利器</div>
      <div class="ios-card">
        <router-link to="/practice?mode=weak" class="ios-row">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-xl bg-orange-50 text-[#FF9500] flex items-center justify-center font-bold text-sm">突</div>
            <div>
              <div class="text-sm font-semibold text-slate-800">薄弱点智能突击</div>
              <div class="text-[11px] text-slate-400">错题 + 薄弱考点动态智能组卷</div>
            </div>
          </div>
          <span class="text-slate-300 font-bold text-sm">›</span>
        </router-link>

        <router-link to="/wrong-questions" class="ios-row">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-xl bg-rose-50 text-[#FF3B30] flex items-center justify-center font-bold text-sm">错</div>
            <div>
              <div class="text-sm font-semibold text-slate-800">错题本与消灭</div>
              <div class="text-[11px] text-slate-400">按考点精确筛选 · DeepSeek 白话精讲</div>
            </div>
          </div>
          <span class="text-slate-300 font-bold text-sm">›</span>
        </router-link>

        <router-link to="/learn/glossary/quiz" class="ios-row">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-xl bg-teal-50 text-[#30B0C7] flex items-center justify-center font-bold text-sm">词</div>
            <div>
              <div class="text-sm font-semibold text-slate-800">高频英语术语速测</div>
              <div class="text-[11px] text-slate-400">10 词每日小测 · 选项标准判分</div>
            </div>
          </div>
          <span class="text-slate-300 font-bold text-sm">›</span>
        </router-link>

        <router-link to="/materials" class="ios-row">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-sm">档</div>
            <div>
              <div class="text-sm font-semibold text-slate-800">备考文库与真题</div>
              <div class="text-[11px] text-slate-400">第 3 版官方教材 · 历年真题 PDF 阅读</div>
            </div>
          </div>
          <span class="text-slate-300 font-bold text-sm">›</span>
        </router-link>
      </div>
    </div>

    <!-- High Frequency Keypoints Quick Links -->
    <div class="ios-group">
      <div class="ios-group-header">考前高频速记直达</div>
      <div class="ios-card p-3.5">
        <div class="flex flex-wrap gap-1.5">
          <router-link
            v-for="item in highFreqTopics"
            :key="item.name"
            :to="item.to"
            class="px-2.5 py-1.5 rounded-xl bg-slate-50 text-xs font-medium text-slate-700 border border-slate-200/80 hover:bg-slate-100 transition"
          >
            {{ item.name }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { wrongBookApi, planApi, aiApi } from '@/api'
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
const aiQuota = ref<any>(null)

const todayDateStr = computed(() => {
  const d = new Date()
  const weekDays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return `${d.getMonth() + 1}月${d.getDate()}日 ${weekDays[d.getDay()]}`
})

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

// AI status capsule helpers
const aiStatusText = computed(() => {
  if (!aiQuota.value) return 'AI 伴学'
  if (aiQuota.value.global_enabled === false) return 'AI 维护中'
  if (aiQuota.value.ai_enabled === false) return 'AI 未开通'
  return `AI 伴学: ${aiQuota.value.remaining}/${aiQuota.value.daily_limit}次`
})

const aiStatusClass = computed(() => {
  if (!aiQuota.value) return 'ios-pill-gray'
  if (aiQuota.value.global_enabled === false) return 'ios-pill-orange'
  if (aiQuota.value.ai_enabled === false) return 'ios-pill-gray'
  if (aiQuota.value.remaining === 0) return 'ios-pill-red'
  return 'ios-pill-blue'
})

const aiDotClass = computed(() => {
  if (!aiQuota.value) return 'bg-slate-400'
  if (aiQuota.value.global_enabled === false) return 'bg-amber-500'
  if (aiQuota.value.ai_enabled === false) return 'bg-slate-400'
  if (aiQuota.value.remaining === 0) return 'bg-rose-500'
  return 'bg-[#007AFF]'
})

function showAiTip() {
  if (!aiQuota.value) return
  if (aiQuota.value.ai_enabled === false) {
    alert('【AI 伴学未开通】\n为防止额度消耗与保障辅导质量，新学员默认关闭 AI 伴学功能。请联系管理员开启权限并分配额度！')
  } else if (aiQuota.value.global_enabled === false) {
    alert('【AI 伴学维护中】\n管理员开启了全站维护模式，请稍后再试。')
  } else {
    alert(`【DeepSeek AI 伴学】\n可用额度：${aiQuota.value.daily_limit} 次\n已使用：${aiQuota.value.used_today} 次\n剩余：${aiQuota.value.remaining} 次`)
  }
}

const highFreqTopics = [
  { name: '挣值 EVM 公式', to: '/learn/points/kp_evm_cpi' },
  { name: '关键路径 CPM', to: '/learn/points/kp_cpm_float' },
  { name: '整体变更控制 CCB', to: '/learn/points/kp_ccb_change' },
  { name: '配置三库基线', to: '/learn/points/kp_ch07_config_baseline' },
  { name: '进度成本四象限', to: '/learn/points/kp_ch09_quad_measures' },
  { name: '八大绩效域精析', to: '/learn/points/kp_perf_domains_overview' },
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

  try {
    const qRes: any = await aiApi.getQuota()
    aiQuota.value = qRes
  } catch (err) {
    console.error('Failed to load AI quota', err)
  }
})
</script>
