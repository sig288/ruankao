<template>
  <div class="p-4 space-y-4">
    <div class="bg-white p-3.5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
      <div>
        <h2 class="text-sm font-black text-slate-800">我的收藏夹</h2>
        <p class="text-[10px] text-slate-400">重点题目随手收藏复习</p>
      </div>
      <span class="text-xs font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded-lg border border-amber-200">
        {{ favorites.length }} 题
      </span>
    </div>

    <div v-if="loading" class="text-center py-16 text-slate-400 text-sm">
      正在加载收藏题...
    </div>

    <div v-else-if="favorites.length === 0" class="bg-white rounded-2xl p-10 text-center text-slate-500 border border-slate-200">
      <div class="w-12 h-12 bg-amber-50 text-amber-500 rounded-2xl flex items-center justify-center mx-auto mb-3 text-xl">
        ★
      </div>
      <p class="text-sm font-bold text-slate-700">暂无收藏题目</p>
      <p class="text-xs text-slate-400 mt-1">在刷题时点击右上角星标即可收藏！</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="item in favorites"
        :key="item.favorite_id"
        class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3"
      >
        <div class="flex items-center justify-between">
          <span class="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-[11px] font-medium">{{ item.chapter }} · {{ item.knowledge }}</span>
          <button
            @click="unfavorite(item.question_id)"
            class="text-xs text-amber-500 hover:text-amber-700 font-bold"
          >
            ★ 取消收藏
          </button>
        </div>

        <div class="text-xs font-semibold text-slate-800 leading-relaxed">
          {{ item.stem }}
        </div>

        <div v-if="item.options" class="space-y-1 bg-slate-50/70 p-2.5 rounded-xl text-[11px] text-slate-600">
          <div v-for="(opt, oIdx) in item.options" :key="oIdx">
            {{ opt }}
          </div>
        </div>

        <div class="p-3 bg-slate-50 rounded-xl text-xs text-slate-600 leading-relaxed">
          <div class="font-bold text-emerald-600 mb-1">正确答案：{{ item.correct_answer }}</div>
          <div><span class="font-bold text-slate-700">解析：</span>{{ item.analysis }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { wrongBookApi } from '@/api'

const favorites = ref<any[]>([])
const loading = ref(false)

async function loadFavorites() {
  loading.value = true
  try {
    const res: any = await wrongBookApi.listFavorites()
    favorites.value = res
  } catch (err) {
    console.error('Failed to load favorites', err)
  } finally {
    loading.value = false
  }
}

async function unfavorite(qid: string) {
  try {
    await wrongBookApi.toggleFavorite(qid)
    favorites.value = favorites.value.filter((x) => x.question_id !== qid)
  } catch (err) {
    console.error('Unfavorite failed', err)
  }
}

onMounted(() => {
  loadFavorites()
})
</script>
