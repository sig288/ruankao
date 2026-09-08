<template>
  <div class="rk-page">
    <div class="rk-card p-3 flex items-center justify-between">
      <div>
        <h2 class="text-[13px] font-black text-ink-800">考点全景知识树</h2>
        <p class="text-[10px] text-muted mt-0.5">按 17 章展开 · 口诀来自必背整理</p>
      </div>
      <router-link
        to="/learn/glossary"
        class="px-2.5 py-1.5 text-[11px] font-bold rounded-lg bg-paper-100 text-ink-700"
      >
        英语词表
      </router-link>
    </div>

    <div v-if="progress" class="rk-card p-4 bg-ink-800 text-paper-50">
      <div class="flex items-end justify-between">
        <div>
          <p class="text-[10px] text-paper-300">全书掌握率</p>
          <p class="text-2xl font-black font-mono mt-0.5">{{ Math.round(progress.overall_completion_rate * 100) }}%</p>
        </div>
        <p class="text-[11px] text-paper-300">已掌握 {{ progress.mastered_points }} / {{ progress.total_points }}</p>
      </div>
      <div class="w-full h-1.5 bg-white/15 rounded-full mt-3 overflow-hidden">
        <div
          class="h-full bg-pine-500 rounded-full"
          :style="{ width: `${Math.round(progress.overall_completion_rate * 100)}%` }"
        ></div>
      </div>
    </div>

    <div v-if="progress?.recent_studied?.length" class="space-y-1.5">
      <p class="text-[11px] font-bold text-ink-800">最近学过</p>
      <div class="flex space-x-2 overflow-x-auto no-scrollbar">
        <router-link
          v-for="item in progress.recent_studied"
          :key="item.id"
          :to="`/learn/points/${item.id}`"
          class="rk-card shrink-0 max-w-[200px] p-2.5"
        >
          <div class="flex items-center justify-between text-[10px] text-muted mb-1">
            <span>{{ item.chapter_id }}</span>
            <span>{{ getStatusLabel(item.status) }}</span>
          </div>
          <div class="text-[12px] font-bold text-ink-800 truncate">{{ item.title }}</div>
        </router-link>
      </div>
    </div>

    <div class="flex items-center gap-2 overflow-x-auto no-scrollbar text-[11px]">
      <button
        v-for="filter in statusFilters"
        :key="filter.value"
        @click="selectedStatus = filter.value; loadPoints()"
        class="px-3 py-1.5 rounded-xl font-bold whitespace-nowrap min-h-[36px]"
        :class="selectedStatus === filter.value ? 'bg-ink-800 text-paper-50' : 'rk-card text-ink-700'"
      >
        {{ filter.label }}
      </button>
    </div>

    <div v-if="loading" class="text-center py-16 text-muted text-xs">正在展开知识树…</div>
    <div v-else class="space-y-2.5">
      <div v-for="chapter in chapters" :key="chapter.id" class="rk-card overflow-hidden">
        <button
          @click="toggleChapter(chapter.id)"
          class="w-full p-3.5 flex items-center justify-between text-left min-h-[52px]"
        >
          <div class="flex-1 pr-3 min-w-0">
            <div class="flex items-center gap-2">
              <span class="px-1.5 py-0.5 rounded bg-pine-100 text-pine-700 font-mono text-[10px] font-black">
                {{ chapter.code }}
              </span>
              <h3 class="text-[12px] font-bold text-ink-800 truncate">{{ chapter.title }}</h3>
            </div>
            <div class="flex items-center gap-3 mt-1.5 text-[10px] text-muted">
              <span>{{ chapter.total_points }} 个考点</span>
              <span>已掌握 {{ chapter.mastered_points }}</span>
              <span class="font-mono text-pine-600 font-bold">{{ Math.round(chapter.completion_rate * 100) }}%</span>
            </div>
          </div>
          <span class="text-muted text-xs transition-transform" :class="{ 'rotate-180': openChapters.includes(chapter.id) }">▾</span>
        </button>

        <div v-if="openChapters.includes(chapter.id)" class="border-t border-paper-200 bg-paper-100/60 p-2.5 space-y-2">
          <div v-if="getChapterPoints(chapter.id).length === 0" class="py-4 text-center text-xs text-muted">
            暂无匹配考点
          </div>
          <router-link
            v-for="point in getChapterPoints(chapter.id)"
            :key="point.id"
            :to="`/learn/points/${point.id}`"
            class="block bg-paper-50 p-3 rounded-xl border border-paper-200 active:scale-[0.99]"
          >
            <div class="flex items-start justify-between gap-2">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-1.5 mb-1">
                  <span class="px-1.5 py-0.5 rounded text-[9px] font-bold" :class="getFrequencyBadge(point.frequency)">
                    {{ getFrequencyLabel(point.frequency) }}
                  </span>
                  <span class="text-[10px] text-muted">约{{ point.est_minutes }}分钟</span>
                </div>
                <h4 class="text-[12px] font-bold text-ink-800 leading-snug">{{ point.title }}</h4>
              </div>
              <span class="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-semibold" :class="getStatusBadgeClass(point.status)">
                {{ getStatusLabel(point.status) }}
              </span>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { learnApi } from '@/api'
import { triggerHaptic } from '@/utils/haptics'

const loading = ref(true)
const chapters = ref<any[]>([])
const allPoints = ref<any[]>([])
const progress = ref<any>(null)
const openChapters = ref<string[]>(['CH07', 'CH09', 'CH10'])
const selectedStatus = ref<string>('')

const statusFilters = [
  { label: '全部', value: '' },
  { label: '未学', value: 'unlearned' },
  { label: '学习中', value: 'learning' },
  { label: '已掌握', value: 'mastered' },
]

async function loadData() {
  loading.value = true
  try {
    const [chapRes, progRes, ptsRes] = await Promise.all([
      learnApi.getChapters(),
      learnApi.getProgress(),
      learnApi.listPoints({ status: selectedStatus.value || undefined, page_size: 200 })
    ])
    chapters.value = chapRes
    progress.value = progRes
    allPoints.value = ptsRes.items || []
  } catch (err) {
    console.error('Failed to load learn data:', err)
  } finally {
    loading.value = false
  }
}

async function loadPoints() {
  try {
    const ptsRes = await learnApi.listPoints({ status: selectedStatus.value || undefined, page_size: 200 })
    allPoints.value = ptsRes.items || []
  } catch (err) {
    console.error(err)
  }
}

function toggleChapter(id: string) {
  triggerHaptic('tap')
  const idx = openChapters.value.indexOf(id)
  if (idx >= 0) {
    openChapters.value.splice(idx, 1)
  } else {
    openChapters.value.push(id)
  }
}

function getChapterPoints(chapterId: string) {
  return allPoints.value.filter(p => p.chapter_id === chapterId)
}

function getFrequencyBadge(freq: string) {
  if (freq === 'high') return 'bg-cinnabar-50 text-cinnabar-700'
  if (freq === 'mid') return 'bg-paper-200 text-ink-700'
  return 'bg-paper-100 text-muted'
}

function getFrequencyLabel(freq: string) {
  if (freq === 'high') return '高频'
  if (freq === 'mid') return '常考'
  return '了解'
}

function getStatusBadgeClass(status: string) {
  if (status === 'mastered') return 'bg-pine-100 text-pine-700'
  if (status === 'learning') return 'bg-ink-100 text-ink-700'
  return 'bg-paper-200 text-muted'
}

function getStatusLabel(status: string) {
  if (status === 'mastered') return '已掌握'
  if (status === 'learning') return '学习中'
  return '未学'
}

onMounted(() => {
  loadData()
})
</script>
