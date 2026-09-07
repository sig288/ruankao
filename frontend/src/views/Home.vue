<template>
  <div class="p-4 space-y-4">
    <!-- Top Banner Card -->
    <div class="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-4 text-white shadow-md relative overflow-hidden">
      <div class="relative z-10">
        <div class="flex items-center justify-between">
          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-white/20 text-white backdrop-blur">
            第3版新大纲专用
          </span>
          <span class="text-xs text-blue-100">及格线 45 / 75 分</span>
        </div>
        <h2 class="text-lg font-black mt-2">软考中项 · 考前冲刺</h2>
        <p class="text-xs text-blue-100 mt-0.5">基础知识（选择） + 应用技术（案例计算与问答）</p>

        <!-- Mini Stats in Banner -->
        <div class="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-white/10 text-center">
          <div>
            <div class="text-base font-black">{{ stats.total_answered }}</div>
            <div class="text-[10px] text-blue-200">累计刷题</div>
          </div>
          <div>
            <div class="text-base font-black">{{ stats.overall_accuracy }}%</div>
            <div class="text-[10px] text-blue-200">综合正确率</div>
          </div>
          <div>
            <div class="text-base font-black text-amber-300">{{ stats.unmastered_wrong }}</div>
            <div class="text-[10px] text-blue-200">待消灭错题</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 14天倒计时与今日备考计划卡片 -->
    <div v-if="plan" class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-4 text-white shadow-sm border border-indigo-800/40">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="text-xs px-2 py-0.5 bg-indigo-500/30 text-indigo-200 rounded-full font-semibold border border-indigo-400/30">
            ⏳ 备考计划
          </span>
          <span class="text-xs text-indigo-300">目标: {{ plan.exam_date }}</span>
        </div>
        <router-link to="/plan" class="text-xs text-indigo-300 hover:text-white flex items-center space-x-0.5">
          <span>进入学习计划</span>
          <span>›</span>
        </router-link>
      </div>

      <div class="mt-3 flex items-center justify-between">
        <div>
          <div class="text-xs text-slate-300">距离考试仅剩</div>
          <div class="text-2xl font-extrabold font-mono text-amber-400">{{ plan.days_remaining }} <span class="text-xs font-normal text-slate-300">天</span></div>
        </div>
        <div class="text-right">
          <div class="text-xs text-slate-300">今日打卡进度</div>
          <div class="text-sm font-bold font-mono text-emerald-400">
            {{ completedTodayCount }} / {{ plan.today_tasks?.length || 0 }} 项
          </div>
        </div>
      </div>

      <!-- Mini Today Tasks list -->
      <div v-if="plan.today_tasks && plan.today_tasks.length > 0" class="mt-3 pt-3 border-t border-indigo-900/60 space-y-1.5">
        <div
          v-for="task in plan.today_tasks.slice(0, 2)"
          :key="task.id"
          class="flex items-center justify-between text-xs py-1 px-2 rounded-lg bg-white/5"
        >
          <div class="flex items-center space-x-2 truncate">
            <span :class="task.is_completed ? 'text-emerald-400' : 'text-slate-400'">{{ task.is_completed ? '✓' : '○' }}</span>
            <span class="truncate" :class="{ 'line-through text-slate-400': task.is_completed }">{{ task.title }}</span>
          </div>
          <span class="text-[10px] text-indigo-300 shrink-0 font-mono">{{ task.estimated_minutes }}分钟</span>
        </div>
      </div>
    </div>

    <!-- Core Entry Cards -->
    <div class="grid grid-cols-2 gap-3">
      <!-- 章节精练 -->
      <router-link
        to="/practice"
        class="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col justify-between hover:border-blue-300 transition-all active:scale-[0.98]"
      >
        <div class="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-bold text-slate-800">章节专项练</h3>
          <p class="text-[11px] text-slate-500 mt-0.5">十大知识领域细化刷题</p>
        </div>
      </router-link>

      <!-- 薄弱点精准突击 (P0) -->
      <router-link
        to="/practice?mode=weak"
        class="bg-gradient-to-br from-rose-500/10 to-amber-500/10 p-4 rounded-2xl border border-rose-200 shadow-sm flex flex-col justify-between hover:border-rose-300 transition-all active:scale-[0.98]"
      >
        <div class="w-10 h-10 rounded-xl bg-rose-500 text-white flex items-center justify-center mb-3 shadow-sm">
          <span class="text-lg">🔥</span>
        </div>
        <div>
          <div class="flex items-center space-x-1">
            <h3 class="text-sm font-bold text-rose-900">薄弱点突击</h3>
            <span class="text-[9px] px-1 py-0.2 bg-rose-600 text-white rounded font-bold">P0</span>
          </div>
          <p class="text-[11px] text-rose-600/80 mt-0.5">算法动态组卷专攻错题弱项</p>
        </div>
      </router-link>

      <!-- 全真机考 -->
      <router-link
        to="/mock-exam"
        class="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col justify-between hover:border-indigo-300 transition-all active:scale-[0.98]"
      >
        <div class="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-bold text-slate-800">全真机考模拟</h3>
          <p class="text-[11px] text-slate-500 mt-0.5">75题标准计时模拟考</p>
        </div>
      </router-link>

      <!-- 案例分析专题 -->
      <router-link
        to="/case-exam"
        class="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col justify-between hover:border-emerald-300 transition-all active:scale-[0.98]"
      >
        <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-bold text-slate-800">案例分析专题</h3>
          <p class="text-[11px] text-slate-500 mt-0.5">计算与问答半自动判分</p>
        </div>
      </router-link>

      <!-- 错题本 -->
      <router-link
        to="/wrong-questions"
        class="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col justify-between hover:border-rose-300 transition-all active:scale-[0.98]"
      >
        <div class="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center mb-3">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div>
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-800">错题强化</h3>
            <span v-if="stats.unmastered_wrong > 0" class="text-[10px] px-1.5 py-0.2 bg-rose-100 text-rose-600 font-bold rounded-full">
              {{ stats.unmastered_wrong }}
            </span>
          </div>
          <p class="text-[11px] text-slate-500 mt-0.5">支持 DeepSeek 助教拆解</p>
        </div>
      </router-link>

      <!-- 我的资料库 (P1) -->
      <router-link
        to="/materials"
        class="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col justify-between hover:border-purple-300 transition-all active:scale-[0.98]"
      >
        <div class="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mb-3">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
          </svg>
        </div>
        <div>
          <div class="flex items-center space-x-1">
            <h3 class="text-sm font-bold text-slate-800">私有资料库</h3>
            <span class="text-[9px] px-1 py-0.2 bg-purple-600 text-white rounded font-bold">P1</span>
          </div>
          <p class="text-[11px] text-slate-500 mt-0.5">上传资料 & CSV转题库</p>
        </div>
      </router-link>
    </div>

    <!-- 考点掌握度诊断 Banner (M4) -->
    <router-link
      to="/statistics"
      class="block bg-gradient-to-r from-blue-700 via-indigo-700 to-indigo-800 rounded-2xl p-4 text-white shadow-sm hover:opacity-95 transition-all"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center text-lg">
            📊
          </div>
          <div>
            <h4 class="text-sm font-bold text-white">考点掌握度诊断全景 (M4)</h4>
            <p class="text-[11px] text-blue-100 mt-0.5">17章大纲 & 十大管理领域深度画像，自动识别考点盲区</p>
          </div>
        </div>
        <span class="text-xs font-semibold px-2 py-1 bg-white/20 rounded-lg">查看 ›</span>
      </div>
    </router-link>

    <!-- Quick Knowledge Shortcuts -->
    <div class="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider">高频命题热区（第3版新大纲）</h3>
        <router-link to="/practice" class="text-xs text-blue-600 font-medium">全部章节 ›</router-link>
      </div>

      <div class="flex flex-wrap gap-2">
        <router-link
          v-for="item in highFreqTopics"
          :key="item.name"
          :to="{ path: '/practice', query: { chapter: item.chapter, knowledge: item.knowledge } }"
          class="px-2.5 py-1.5 bg-slate-50 hover:bg-blue-50 border border-slate-200/60 rounded-xl text-xs text-slate-700 hover:text-blue-700 transition-colors flex items-center space-x-1"
        >
          <span>{{ item.name }}</span>
          <span class="text-[10px] text-slate-400 font-mono">★</span>
        </router-link>
      </div>
    </div>

    <!-- Agent Integration Notice -->
    <div class="bg-slate-900 rounded-2xl p-4 text-white shadow-sm flex items-start space-x-3">
      <div class="p-2 bg-slate-800 rounded-xl text-blue-400">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <div class="flex-1">
        <h4 class="text-xs font-bold text-blue-300">外部 Agent 错题互联已就绪</h4>
        <p class="text-[11px] text-slate-400 mt-0.5 leading-relaxed">
          可通过独立 Agent API Key 拉取本系统的做题数据，并调用回写接口注入专业讲解。
        </p>
        <div class="mt-2 flex items-center space-x-3">
          <a href="/api/docs" target="_blank" class="text-xs text-blue-400 underline font-mono">/api/docs (OpenAPI)</a>
          <router-link v-if="authStore.isAdmin" to="/admin" class="text-xs text-slate-300 hover:text-white underline">管理 Key ›</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { wrongBookApi, planApi } from '@/api'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()

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

const highFreqTopics = [
  { name: '挣值管理 (EVM)', chapter: '项目成本管理', knowledge: '挣值分析EVM' },
  { name: '关键路径法 (CPM)', chapter: '项目进度管理', knowledge: '关键路径与浮动时间' },
  { name: '整体变更控制 (CCB)', chapter: '项目整合管理', knowledge: '整体变更控制流程' },
  { name: '配置三库与基线', chapter: '配置与变更管理', knowledge: '配置三库与基线管理' },
  { name: '招投标与法规', chapter: '信息化与法律法规', knowledge: '招投标与政府采购法规' },
  { name: '合同类型与风险', chapter: '项目采购管理', knowledge: '合同类型与风险分配' },
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
