<template>
  <div class="ios-page space-y-3.5">
    <!-- Header with Segmented Filter -->
    <div class="ios-card p-3.5 space-y-3">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-bold text-slate-900">错题本与弱点消灭</h2>
          <p class="text-xs text-slate-400 mt-0.5">自动沉淀日常练习与模考答错题</p>
        </div>

        <select
          v-if="availableKnowledges.length > 0"
          v-model="selectedKnowledge"
          @change="loadWrongQuestions()"
          class="text-xs bg-slate-100 border border-slate-200 rounded-xl px-2.5 py-1.5 text-slate-700 max-w-[130px] truncate focus:outline-none"
        >
          <option value="">全部知识点</option>
          <option v-for="k in availableKnowledges" :key="k" :value="k">{{ k }}</option>
        </select>
      </div>

      <!-- iOS Segmented Control -->
      <div class="ios-segmented">
        <button
          class="ios-segmented-item"
          :class="{ 'is-active': filterMastered === null }"
          @click="filterMastered = null; loadWrongQuestions()"
        >
          全部错题
        </button>
        <button
          class="ios-segmented-item"
          :class="{ 'is-active': filterMastered === false }"
          @click="filterMastered = false; loadWrongQuestions()"
        >
          未消灭 ({{ unmasteredCount }})
        </button>
        <button
          class="ios-segmented-item"
          :class="{ 'is-active': filterMastered === true }"
          @click="filterMastered = true; loadWrongQuestions()"
        >
          已掌握
        </button>
      </div>
    </div>

    <!-- Target Weak Drill Banner -->
    <div v-if="items.some(x => !x.is_mastered)" class="ios-card bg-[#007AFF] text-white p-4 flex items-center justify-between shadow-sm">
      <div>
        <div class="font-bold text-sm">错题智能靶向突击</div>
        <div class="text-xs text-blue-100 mt-0.5">抽选当前薄弱与未消灭考题组卷突破</div>
      </div>
      <router-link
        to="/practice?mode=weak"
        class="px-3.5 py-1.5 bg-white text-[#007AFF] rounded-full text-xs font-bold shadow-sm active:scale-95 transition"
      >
        去消灭 ›
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-16 text-slate-400 text-sm">
      正在检索错题本...
    </div>

    <!-- Empty State -->
    <div v-else-if="items.length === 0" class="ios-card p-10 text-center text-slate-500">
      <div class="w-12 h-12 bg-emerald-50 text-[#34C759] rounded-full flex items-center justify-center mx-auto mb-3 text-2xl font-bold">
        ✓
      </div>
      <p class="text-sm font-bold text-slate-800">暂无需要消灭的错题</p>
      <p class="text-xs text-slate-400 mt-1">恭喜！错题库已全部掌握或暂无错题记录。</p>
    </div>

    <!-- Wrong Questions List -->
    <div v-else class="space-y-3.5">
      <div
        v-for="item in items"
        :key="item.id"
        class="ios-card p-4 space-y-3 relative transition-all"
        :class="{ 'opacity-65 bg-slate-50/80': item.is_mastered }"
      >
        <!-- Card Top Badges & Actions -->
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center space-x-1.5 flex-wrap">
            <span class="ios-pill ios-pill-blue">{{ item.knowledge }}</span>
            <span class="ios-pill ios-pill-red">做错 {{ item.wrong_count }} 次</span>
          </div>

          <div class="flex items-center space-x-2">
            <!-- Go Consolidate Button -->
            <router-link
              v-if="item.knowledge_point_ids && item.knowledge_point_ids.length > 0"
              :to="`/learn/points/${item.knowledge_point_ids[0]}`"
              class="ios-btn-secondary px-2.5 py-1 text-xs font-semibold rounded-lg"
            >
              <span>去巩固</span>
              <span>›</span>
            </router-link>
            <router-link
              v-else
              :to="`/practice?knowledge=${encodeURIComponent(item.knowledge)}`"
              class="ios-btn-secondary px-2.5 py-1 text-xs font-semibold rounded-lg"
            >
              <span>去巩固</span>
              <span>›</span>
            </router-link>

            <!-- Toggle Mastered Button -->
            <button
              @click="toggleMaster(item)"
              class="text-xs px-2 py-1 rounded-lg border transition-colors"
              :class="item.is_mastered ? 'bg-emerald-50 text-[#34C759] border-emerald-200' : 'bg-slate-50 text-slate-500 border-slate-200 hover:text-slate-800'"
            >
              {{ item.is_mastered ? '已掌握 ✓' : '标记已掌握' }}
            </button>
          </div>
        </div>

        <!-- Stem -->
        <div class="text-sm font-semibold text-slate-800 leading-relaxed">
          {{ item.stem }}
        </div>

        <!-- Answer Comparison Box -->
        <div class="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-rose-600 font-semibold">上次作答：{{ item.last_answer || '未作答' }}</span>
            <span class="text-emerald-700 font-bold font-mono">标准正确答案：{{ item.correct_answer }}</span>
          </div>
          <p v-if="item.analysis" class="text-slate-600 pt-1 text-[11px] leading-normal border-t border-slate-200/60 mt-1 whitespace-pre-line">
            {{ item.analysis }}
          </p>
        </div>

        <!-- P0 DeepSeek AI Companion Assist Panel -->
        <AiAssistPanel
          :question-id="item.question_id"
          :initial-explanation="item.agent_explanation"
          :initial-mnemonic="item.ai_mnemonic"
          :is-case="false"
        />

        <!-- Footer Meta -->
        <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1">
          <span>最近答错：{{ formatDate(item.last_wrong_at) }}</span>
          <button
            @click="deleteWrongItem(item.id)"
            class="text-slate-400 hover:text-rose-500 transition"
          >
            移除此错题
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { wrongBookApi } from '@/api'
import AiAssistPanel from '@/components/AiAssistPanel.vue'

const items = ref<any[]>([])
const loading = ref(false)
const filterMastered = ref<boolean | null>(false)
const selectedKnowledge = ref<string>('')
const availableKnowledges = ref<string[]>([])

const unmasteredCount = computed(() => {
  return items.value.filter(x => !x.is_mastered).length
})

async function loadWrongQuestions() {
  loading.value = true
  try {
    const params: any = {}
    if (filterMastered.value !== null) {
      params.mastered = filterMastered.value
    }
    if (selectedKnowledge.value) {
      params.knowledge = selectedKnowledge.value
    }
    const res: any = await wrongBookApi.listWrong(params)
    items.value = res

    // Extract unique knowledge points for the filter dropdown
    if (availableKnowledges.value.length === 0 && Array.isArray(res)) {
      const kSet = new Set<string>()
      res.forEach(item => {
        if (item.knowledge) kSet.add(item.knowledge)
      })
      availableKnowledges.value = Array.from(kSet)
    }
  } catch (err) {
    console.error('Failed to load wrong questions', err)
  } finally {
    loading.value = false
  }
}

async function toggleMaster(item: any) {
  const target = !item.is_mastered
  try {
    await wrongBookApi.toggleMaster(item.id, target)
    item.is_mastered = target
  } catch (err) {
    alert('操作失败')
  }
}

async function deleteWrongItem(id: string) {
  if (!confirm('确定将此题从错题本中移除吗？')) return
  try {
    await wrongBookApi.deleteWrong(id)
    items.value = items.value.filter(x => x.id !== id)
  } catch (err) {
    alert('删除失败')
  }
}

function formatDate(dtStr: string) {
  if (!dtStr) return ''
  const d = new Date(dtStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

onMounted(() => {
  loadWrongQuestions()
})
</script>
