<template>
  <div class="rk-page">
    <!-- Header -->
    <div class="bg-white rounded-2xl p-3.5 border border-slate-200 shadow-sm flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <router-link to="/learn/glossary" class="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg active:bg-slate-100">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </router-link>
        <div>
          <h2 class="text-xs font-bold text-slate-800">英语术语详情卡</h2>
          <p class="text-[10px] text-slate-400">真题词条详解与易混辨析</p>
        </div>
      </div>

      <!-- Favorite Button -->
      <button
        v-if="term"
        @click="toggleFavorite"
        class="p-2 text-slate-300 hover:text-amber-500 transition-colors"
        :class="{ 'text-amber-500': term.favorited }"
      >
        <svg class="w-5 h-5 fill-current" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-20 text-slate-400 text-xs">
      正在加载词条卡片...
    </div>

    <div v-else-if="term" class="space-y-4">
      <!-- Term Core Card -->
      <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
        <div class="flex items-center space-x-2">
          <span
            class="px-2 py-0.5 rounded text-[10px] font-bold"
            :class="term.frequency === 'high' ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-600'"
          >
            {{ term.frequency === 'high' ? '卷末高频考词' : '常用专业术语' }}
          </span>
          <span v-if="term.favorited" class="text-xs text-amber-600 font-bold">★ 已收藏</span>
        </div>

        <div>
          <h1 class="text-lg font-black text-indigo-900 font-mono tracking-wide leading-tight">
            {{ term.term_en }}
          </h1>
          <p class="text-sm font-bold text-slate-700 mt-1">
            {{ term.term_zh }}
          </p>
        </div>

        <!-- Tags -->
        <div v-if="term.tags && term.tags.length > 0" class="flex flex-wrap gap-1.5 pt-1">
          <span
            v-for="tag in term.tags"
            :key="tag"
            class="px-2 py-0.5 bg-indigo-50 text-indigo-700 text-[10px] font-medium rounded-md"
          >
            # {{ tag }}
          </span>
        </div>

        <!-- State Switcher (B-US3) -->
        <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
          <span class="text-xs text-slate-500 font-medium">记忆状态：</span>
          <div class="flex items-center space-x-1.5">
            <button
              @click="setKnown('dont_know')"
              class="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all"
              :class="term.known === 'dont_know' ? 'bg-rose-600 text-white shadow-sm' : 'bg-slate-100 text-slate-600'"
            >
              记不住 / 不会
            </button>
            <button
              @click="setKnown('know')"
              class="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all"
              :class="term.known === 'know' ? 'bg-emerald-600 text-white shadow-sm' : 'bg-slate-100 text-slate-600'"
            >
              已记住 ✓
            </button>
          </div>
        </div>
      </div>

      <!-- Exam Tips Card (B-US2) -->
      <div v-if="term.tip" class="bg-gradient-to-br from-indigo-50 to-blue-50 border border-indigo-200/80 rounded-2xl p-4 shadow-sm space-y-2">
        <div class="flex items-center space-x-1.5 text-indigo-900 font-bold text-xs">
          <span class="text-base">💡</span>
          <span>考点速记与真题提示</span>
        </div>
        <p class="text-xs text-indigo-950 leading-relaxed bg-white/70 p-3 rounded-xl border border-indigo-100/70">
          {{ term.tip }}
        </p>
      </div>

      <!-- Confusing Terms Card (B-US2) -->
      <div v-if="term.confuse_with && term.confuse_with.length > 0" class="bg-amber-50/60 border border-amber-200 rounded-2xl p-4 shadow-sm space-y-2.5">
        <div class="flex items-center space-x-1.5 text-amber-900 font-bold text-xs">
          <span class="text-base">⚠️</span>
          <span>易混概念辨析防掉坑</span>
        </div>
        <div class="space-y-1.5">
          <div
            v-for="(confuse, idx) in term.confuse_with"
            :key="idx"
            class="text-xs text-amber-900 p-2.5 bg-white/80 rounded-xl border border-amber-100 flex items-start space-x-2"
          >
            <span class="font-bold text-amber-600 shrink-0">辨析:</span>
            <span>{{ confuse }}</span>
          </div>
        </div>
      </div>

      <!-- Linked Knowledge Points (B-US6) -->
      <div v-if="term.knowledge_points && term.knowledge_points.length > 0" class="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm space-y-3">
        <div class="flex items-center justify-between pb-2 border-b border-slate-100">
          <div class="flex items-center space-x-1.5">
            <span class="text-base">🌲</span>
            <h3 class="text-xs font-bold text-slate-800">关联大纲知识点</h3>
          </div>
          <span class="text-[11px] text-slate-400">点击直达考点精学</span>
        </div>

        <div class="space-y-2">
          <router-link
            v-for="point in term.knowledge_points"
            :key="point.id"
            :to="`/learn/points/${point.id}`"
            class="block p-3 rounded-xl bg-slate-50 border border-slate-200 hover:border-blue-400 transition-all"
          >
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-mono text-blue-600 font-bold">{{ point.chapter_id }}</span>
              <span class="text-xs text-blue-600 font-medium">查看考点 ›</span>
            </div>
            <div class="text-xs font-bold text-slate-800 mt-1">{{ point.title }}</div>
          </router-link>
        </div>
      </div>

      <!-- Quick Quiz Action Button (B-US4) -->
      <div class="pt-2">
        <router-link
          to="/learn/glossary/quiz"
          class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-md flex items-center justify-center space-x-2 active:scale-98 transition-all"
        >
          <span>🎯</span>
          <span>进行 10 词快速小测验</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { learnApi } from '@/api'
import { triggerHaptic } from '@/utils/haptics'

const route = useRoute()
const termId = String(route.params.id)

const loading = ref(true)
const term = ref<any>(null)

async function loadDetail() {
  loading.value = true
  try {
    const res = await learnApi.getGlossaryDetail(termId)
    term.value = res
  } catch (err) {
    console.error('Failed to load glossary detail:', err)
  } finally {
    loading.value = false
  }
}

async function toggleFavorite() {
  triggerHaptic('tap')
  if (!term.value) return
  const nextFav = !term.value.favorited
  try {
    const res = await learnApi.updateGlossaryStatus(termId, { favorited: nextFav })
    term.value.favorited = res.favorited !== undefined ? res.favorited : nextFav
  } catch (err) {
    console.error(err)
  }
}

async function setKnown(target: string) {
  triggerHaptic('tap')
  if (!term.value) return
  const nextKnown = term.value.known === target ? 'unknown' : target
  try {
    const res = await learnApi.updateGlossaryStatus(termId, { known: nextKnown })
    term.value.known = res.known ?? nextKnown
    if (nextKnown === 'know') {
      triggerHaptic('success')
    }
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  loadDetail()
})
</script>
