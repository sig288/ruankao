<template>
  <div class="rk-page">
    <div class="rk-card p-3.5 flex items-center justify-between">
      <div>
        <h2 class="text-[13px] font-black text-ink-800">高频英语术语</h2>
        <p class="text-[10px] text-muted">卷末约 5 分 · 必拿</p>
      </div>
      <router-link
        to="/learn/points"
        class="px-2.5 py-1.5 text-[11px] font-bold rounded-lg bg-paper-100 text-ink-700"
      >
        知识树
      </router-link>
    </div>

    <div class="rk-card p-4 bg-ink-800 text-paper-50 flex items-center justify-between">
      <div>
        <p class="text-[13px] font-black">10 词速测</p>
        <p class="text-[10px] text-paper-300 mt-0.5">看英文选中文，即时复盘</p>
      </div>
      <router-link
        to="/learn/glossary/quiz"
        class="px-3 py-2 bg-paper-50 text-ink-800 rounded-xl text-[11px] font-black"
      >
        开始 ›
      </router-link>
    </div>

    <!-- Search Box (B-US1) -->
    <div class="relative">
      <input
        v-model="searchQuery"
        @input="handleSearch"
        type="text"
        placeholder="搜索英文缩写、全称或中文释义 (如 EVM、WBS)..."
        class="w-full bg-white border border-slate-200 rounded-xl py-2.5 pl-9 pr-8 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 shadow-xs"
      />
      <span class="absolute left-3 top-2.5 text-slate-400 text-xs">🔍</span>
      <button
        v-if="searchQuery"
        @click="searchQuery = ''; loadTerms()"
        class="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 text-xs"
      >
        ✕
      </button>
    </div>

    <!-- Status Filters (B-US3) -->
    <div class="flex items-center space-x-1.5 overflow-x-auto pb-0.5 text-xs no-scrollbar">
      <button
        v-for="st in statusTabs"
        :key="st.key"
        @click="switchStatusTab(st.key)"
        class="px-3 py-1.5 rounded-xl font-semibold transition-all whitespace-nowrap"
        :class="activeStatusTab === st.key ? 'bg-slate-800 text-white shadow-sm' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'"
      >
        {{ st.label }}
      </button>
    </div>

    <!-- Domain Tag Chips -->
    <div class="flex items-center space-x-1.5 overflow-x-auto pb-1 text-[11px] no-scrollbar">
      <button
        @click="selectedTag = ''; loadTerms()"
        class="px-2.5 py-1 rounded-lg font-medium transition-all whitespace-nowrap"
        :class="!selectedTag ? 'bg-indigo-100 text-indigo-700 font-bold' : 'bg-white border border-slate-200 text-slate-500'"
      >
        全部领域
      </button>
      <button
        v-for="tag in commonTags"
        :key="tag"
        @click="selectedTag = selectedTag === tag ? '' : tag; loadTerms()"
        class="px-2.5 py-1 rounded-lg font-medium transition-all whitespace-nowrap"
        :class="selectedTag === tag ? 'bg-indigo-600 text-white font-bold shadow-xs' : 'bg-white border border-slate-200 text-slate-600'"
      >
        {{ tag }}
      </button>
    </div>

    <!-- Terms List Header & Total Count -->
    <div class="flex items-center justify-between text-xs text-slate-400 px-1">
      <span>共检索到 <b class="text-slate-700 font-mono">{{ total }}</b> 个核心术语</span>
      <span>点击卡片查看考点详析</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-16 text-slate-400 text-xs">
      正在检索英语词库...
    </div>

    <!-- Empty State -->
    <div v-else-if="items.length === 0" class="bg-white rounded-2xl p-10 text-center text-slate-500 border border-slate-200">
      <div class="text-2xl mb-2">📖</div>
      <p class="text-xs font-bold text-slate-700">未找到匹配的英语术语</p>
      <p class="text-[11px] text-slate-400 mt-1">请尝试更换搜索词或筛选标签</p>
    </div>

    <!-- Terms Cards List (B-US1, B-US2, B-US3) -->
    <div v-else class="space-y-3">
      <div
        v-for="term in items"
        :key="term.id"
        class="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm space-y-2.5 relative transition-all"
        :class="{ 'border-amber-300 bg-amber-50/20': term.favorited }"
      >
        <!-- Header: EN + Favorite + Frequency -->
        <div class="flex items-start justify-between">
          <div class="flex-1 pr-2 cursor-pointer" @click="$router.push(`/learn/glossary/${term.id}`)">
            <div class="flex items-center space-x-2 mb-0.5">
              <span class="text-xs font-black font-mono text-indigo-700 tracking-wide">
                {{ term.term_en }}
              </span>
              <span
                class="px-1.5 py-0.2 rounded text-[9px] font-bold"
                :class="term.frequency === 'high' ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-600'"
              >
                {{ term.frequency === 'high' ? '高频' : '常用' }}
              </span>
            </div>
            <div class="text-xs font-bold text-slate-800">
              {{ term.term_zh }}
            </div>
          </div>

          <!-- Favorite Button -->
          <button
            @click="toggleFavorite(term)"
            class="p-1.5 text-slate-300 hover:text-amber-500 transition-colors"
            :class="{ 'text-amber-500': term.favorited }"
            title="收藏"
          >
            <svg class="w-5 h-5 fill-current" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </button>
        </div>

        <!-- Tip Box -->
        <div
          v-if="term.tip"
          @click="$router.push(`/learn/glossary/${term.id}`)"
          class="p-2.5 bg-slate-50 rounded-xl text-[11px] text-slate-600 leading-relaxed cursor-pointer"
        >
          <span class="font-bold text-slate-700">考点提示：</span>{{ term.tip }}
        </div>

        <!-- Tags & Mastery Status Action Strip -->
        <div class="pt-1 flex items-center justify-between border-t border-slate-100">
          <div class="flex flex-wrap gap-1">
            <span
              v-for="tag in (term.tags || []).slice(0, 2)"
              :key="tag"
              class="text-[9px] px-1.5 py-0.2 bg-slate-100 text-slate-500 rounded"
            >
              {{ tag }}
            </span>
          </div>

          <!-- Know / Don't Know Quick Toggle (B-US3) -->
          <div class="flex items-center space-x-1.5">
            <button
              @click="setKnownStatus(term, 'dont_know')"
              class="px-2 py-0.8 rounded-lg text-[10px] font-semibold transition-colors"
              :class="term.known === 'dont_know' ? 'bg-rose-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
            >
              不会
            </button>
            <button
              @click="setKnownStatus(term, 'know')"
              class="px-2 py-0.8 rounded-lg text-[10px] font-semibold transition-colors"
              :class="term.known === 'know' ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
            >
              已掌握
            </button>
          </div>
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
const items = ref<any[]>([])
const total = ref(0)
const searchQuery = ref('')
const selectedTag = ref('')
const activeStatusTab = ref('all')

const statusTabs = [
  { key: 'all', label: '全部' },
  { key: 'dont_know', label: '不会 ✗' },
  { key: 'know', label: '已掌握 ✓' },
  { key: 'favorited', label: '已收藏 ★' },
]

const commonTags = [
  '成本管理',
  '进度管理',
  '范围管理',
  '采购管理',
  '敏捷开发',
  '云计算',
  '质量管理',
  '风险管理',
  '核心工具'
]

let searchTimer: any = null
function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    loadTerms()
  }, 300)
}

function switchStatusTab(key: string) {
  triggerHaptic('tap')
  activeStatusTab.value = key
  loadTerms()
}

async function loadTerms() {
  loading.value = true
  try {
    const params: any = {
      q: searchQuery.value || undefined,
      tag: selectedTag.value || undefined,
      page_size: 100
    }

    if (activeStatusTab.value === 'dont_know') {
      params.known = 'dont_know'
    } else if (activeStatusTab.value === 'know') {
      params.known = 'know'
    } else if (activeStatusTab.value === 'favorited') {
      params.favorited = true
    }

    const res = await learnApi.listGlossary(params)
    items.value = res.items || []
    total.value = res.total || 0
  } catch (err) {
    console.error('Failed to load glossary:', err)
  } finally {
    loading.value = false
  }
}

async function toggleFavorite(term: any) {
  triggerHaptic('tap')
  const newFav = !term.favorited
  try {
    await learnApi.updateGlossaryStatus(term.id, { favorited: newFav })
    term.favorited = newFav
  } catch (err) {
    console.error(err)
  }
}

async function setKnownStatus(term: any, target: string) {
  triggerHaptic('tap')
  const newKnown = term.known === target ? 'unknown' : target
  try {
    await learnApi.updateGlossaryStatus(term.id, { known: newKnown })
    term.known = newKnown
    if (newKnown === 'know') {
      triggerHaptic('success')
    }
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  loadTerms()
})
</script>
