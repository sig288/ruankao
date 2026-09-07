<template>
  <div class="p-4 space-y-4 pb-24">
    <!-- Header with Countdown Widget -->
    <div class="bg-gradient-to-br from-blue-600 via-indigo-600 to-indigo-700 rounded-3xl p-5 text-white shadow-xl relative overflow-hidden">
      <div class="relative z-10 flex items-center justify-between">
        <div>
          <span class="text-[11px] font-medium tracking-wider uppercase opacity-80">全国软考中项备考倒计时</span>
          <div class="flex items-baseline space-x-1.5 mt-1">
            <span class="text-4xl font-extrabold tracking-tight font-mono">{{ plan?.days_remaining ?? 60 }}</span>
            <span class="text-sm font-semibold opacity-90">天</span>
          </div>
          <p class="text-xs opacity-75 mt-1">目标考试日：{{ plan?.exam_date }} · 每日 {{ plan?.daily_minutes }} 分钟</p>
        </div>

        <button
          @click="showConfigModal = true"
          class="px-3 py-1.5 bg-white/20 hover:bg-white/30 backdrop-blur-md rounded-xl text-xs font-semibold border border-white/20 active:scale-95 transition-all"
        >
          ⚙️ 调整计划
        </button>
      </div>

      <!-- Radial background decorations -->
      <div class="absolute -right-8 -bottom-8 w-36 h-36 bg-white/10 rounded-full blur-xl pointer-events-none"></div>
    </div>

    <!-- Progress Tracker -->
    <div class="bg-white dark:bg-slate-800 rounded-2xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm flex items-center justify-between">
      <div>
        <span class="text-xs text-slate-500">当前任务完成度</span>
        <div class="text-sm font-bold text-slate-800 dark:text-white mt-0.5">
          已完成 {{ completedCount }} / {{ totalTasks }} 项
        </div>
      </div>
      <div class="w-32 bg-slate-100 dark:bg-slate-700 h-2.5 rounded-full overflow-hidden">
        <div
          class="bg-emerald-500 h-full transition-all duration-500 rounded-full"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>
    </div>

    <!-- Daily Task List -->
    <div class="space-y-2.5">
      <h3 class="text-sm font-bold text-slate-800 dark:text-white flex items-center justify-between">
        <span>📅 14天通关每日学习任务</span>
        <span class="text-xs text-blue-600 font-normal">动态根据薄弱项排期</span>
      </h3>

      <div v-if="loading" class="py-12 text-center text-slate-400 text-xs">
        正在拉取备考计划...
      </div>

      <div
        v-for="task in plan?.tasks"
        :key="task.task_id"
        class="bg-white dark:bg-slate-800 rounded-2xl p-3.5 border transition-all shadow-sm flex items-center justify-between"
        :class="task.is_completed ? 'border-emerald-200 dark:border-emerald-800/40 bg-emerald-50/20' : 'border-slate-200 dark:border-slate-700'"
      >
        <div class="flex items-start space-x-3 flex-1 mr-2">
          <!-- Checkbox -->
          <button
            @click="toggleTask(task.task_id)"
            class="w-5 h-5 mt-0.5 rounded-md border flex items-center justify-center transition-colors flex-shrink-0"
            :class="task.is_completed ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-slate-300 dark:border-slate-600 hover:border-blue-500'"
          >
            <span v-if="task.is_completed" class="text-xs font-bold">✓</span>
          </button>

          <div>
            <div class="flex items-center space-x-2">
              <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-700 text-slate-500">
                第{{ task.day_index }}天 · {{ task.date }}
              </span>
              <span class="text-[10px] text-indigo-600 dark:text-indigo-400 font-medium">
                ⏱ {{ task.duration }}分钟
              </span>
            </div>
            <h4
              class="text-xs font-medium mt-1 leading-snug"
              :class="task.is_completed ? 'line-through text-slate-400 dark:text-slate-500' : 'text-slate-800 dark:text-slate-100'"
            >
              {{ task.title }}
            </h4>
          </div>
        </div>

        <!-- Jump Action Button -->
        <router-link
          :to="task.path"
          class="px-2.5 py-1.5 bg-blue-50 dark:bg-blue-900/40 hover:bg-blue-100 text-blue-700 dark:text-blue-300 rounded-xl text-xs font-semibold whitespace-nowrap active:scale-95 transition-all"
        >
          去完成 →
        </router-link>
      </div>
    </div>

    <!-- Config Modal -->
    <div v-if="showConfigModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-slate-800 rounded-3xl w-full max-w-sm p-5 space-y-4 shadow-2xl border border-slate-100 dark:border-slate-700">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-700 pb-3">
          <h3 class="text-sm font-bold text-slate-800 dark:text-white">设置考试目标与节奏</h3>
          <button @click="showConfigModal = false" class="text-slate-400 text-sm">✕</button>
        </div>

        <form @submit.prevent="saveConfig" class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">中项考试目标日期</label>
            <input
              v-model="editForm.exam_date"
              type="date"
              required
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-xs"
            />
          </div>

          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">每日可投入学习时长（分钟）</label>
            <input
              v-model.number="editForm.daily_minutes"
              type="number"
              min="15"
              max="240"
              required
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-xs"
            />
          </div>

          <div class="pt-2 flex space-x-2">
            <button
              type="button"
              @click="showConfigModal = false"
              class="flex-1 py-2 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-xl text-xs font-medium"
            >
              取消
            </button>
            <button
              type="submit"
              class="flex-1 py-2 bg-blue-600 text-white rounded-xl text-xs font-semibold shadow hover:bg-blue-700"
            >
              更新计划
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { planApi } from '@/api'
import { haptics } from '@/utils/haptics'

const plan = ref<any>(null)
const loading = ref(false)
const showConfigModal = ref(false)

const editForm = ref({
  exam_date: '',
  daily_minutes: 60
})

const totalTasks = computed(() => plan.value?.tasks?.length || 0)
const completedCount = computed(() => {
  return (plan.value?.tasks || []).filter((t: any) => t.is_completed).length
})
const progressPercent = computed(() => {
  if (totalTasks.value === 0) return 0
  return Math.round((completedCount.value / totalTasks.value) * 100)
})

onMounted(() => {
  fetchPlan()
})

async function fetchPlan() {
  loading.value = true
  try {
    const res = await planApi.getMe() as any
    plan.value = res
    editForm.value.exam_date = res.exam_date
    editForm.value.daily_minutes = res.daily_minutes
  } catch (e: any) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function toggleTask(taskId: string) {
  haptics.click()
  try {
    const res = await planApi.toggleTask(taskId) as any
    const task = plan.value.tasks.find((t: any) => t.task_id === taskId)
    if (task) {
      task.is_completed = res.is_completed
      if (res.is_completed) haptics.correct()
    }
  } catch (e: any) {
    alert(e.message || '更新失败')
  }
}

async function saveConfig() {
  haptics.click()
  try {
    const res = await planApi.setConfig(editForm.value) as any
    plan.value = res
    showConfigModal.value = false
    haptics.correct()
  } catch (e: any) {
    alert(e.message || '保存失败')
  }
}
</script>
