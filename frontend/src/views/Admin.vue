<template>
  <div class="rk-page">
    <div class="rk-card p-3.5 flex items-center justify-between">
      <div>
        <h2 class="text-sm font-black text-slate-800">系统管理中心</h2>
        <p class="text-[10px] text-slate-400">题库导入、状态监控与外部 Agent 密钥</p>
      </div>
      <span class="px-2 py-0.5 bg-amber-50 text-amber-700 text-xs font-bold rounded-lg border border-amber-200">
        管理员权限
      </span>
    </div>

    <!-- Quick Stats Grid -->
    <div class="grid grid-cols-3 gap-2 text-center">
      <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
        <div class="text-base font-black text-slate-800">{{ stats.total_questions }}</div>
        <div class="text-[10px] text-slate-400">题库总题量</div>
      </div>
      <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
        <div class="text-base font-black text-blue-600">{{ stats.basic_questions }}</div>
        <div class="text-[10px] text-slate-400">基础单选题</div>
      </div>
      <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
        <div class="text-base font-black text-emerald-600">{{ stats.case_questions }}</div>
        <div class="text-[10px] text-slate-400">案例分析题</div>
      </div>
    </div>

    <!-- Section 1: Agent API Key Management (Core requirement) -->
    <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-xs font-bold text-slate-800 uppercase flex items-center space-x-1.5">
            <span class="w-2 h-2 rounded-full bg-blue-600"></span>
            <span>外部 Agent 错题 API Key 管理</span>
          </h3>
          <p class="text-[11px] text-slate-400 mt-0.5">供「软考中项助手」等智能体调用，与用户 JWT 完全独立</p>
        </div>
      </div>

      <!-- Add Key Form -->
      <div class="flex space-x-2">
        <input
          v-model="newKeyName"
          type="text"
          placeholder="例如：微信服务号Agent / 飞书助教"
          class="flex-1 px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          @click="handleCreateKey"
          :disabled="!newKeyName.trim() || creatingKey"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all disabled:opacity-50"
        >
          生成新 Key
        </button>
      </div>

      <!-- Keys List -->
      <div class="space-y-2.5 pt-1">
        <div
          v-for="k in agentKeys"
          :key="k.id"
          class="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1.5"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="font-bold text-slate-800">{{ k.name }}</span>
              <span
                class="px-1.5 py-0.2 rounded text-[10px] font-bold"
                :class="k.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'"
              >
                {{ k.is_active ? '有效' : '已停用' }}
              </span>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click="handleToggleKey(k.id)"
                class="text-xs text-blue-600 hover:underline"
              >
                {{ k.is_active ? '停用' : '启用' }}
              </button>
              <button
                @click="handleDeleteKey(k.id)"
                class="text-xs text-rose-500 hover:underline"
              >
                删除
              </button>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <input
              type="text"
              readonly
              :value="k.key"
              class="flex-1 px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-xs font-mono text-slate-700 select-all"
            />
            <button
              @click="copyKey(k.key)"
              class="px-2.5 py-1 bg-white border border-slate-300 text-slate-700 rounded-lg text-xs font-medium hover:bg-slate-100"
            >
              复制
            </button>
          </div>

          <div class="text-[10px] text-slate-400 flex justify-between">
            <span>创建时间：{{ formatDate(k.created_at) }}</span>
            <span>最后调用：{{ k.last_used_at ? formatDate(k.last_used_at) : '暂未调用' }}</span>
          </div>
        </div>
      </div>

      <!-- Curl Quick Guide -->
      <div class="bg-slate-900 rounded-xl p-3.5 text-white space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-bold text-blue-300">Agent 调用命令示例 (cURL)</span>
          <span class="text-[10px] text-slate-400">OpenAPI: <a href="/api/docs" target="_blank" class="text-blue-400 underline">/api/docs</a></span>
        </div>
        <pre class="text-[10px] font-mono text-slate-300 overflow-x-auto p-2 bg-slate-950 rounded-lg whitespace-pre-wrap"># 拉取待讲解错题
curl -H "Authorization: Bearer {{ agentKeys[0]?.key || 'YOUR_AGENT_KEY' }}" \
  "{{ originUrl }}/api/v1/agent/wrong-questions?limit=10"

# 回写 AI 助教深入讲解
curl -X POST -H "Authorization: Bearer {{ agentKeys[0]?.key || 'YOUR_AGENT_KEY' }}" \
  -H "Content-Type: application/json" \
  -d '{"wrong_question_id":"wq_xxx","explanation":"挣值管理中CV=EV-AC<0表示超支...","study_tips":"口诀：EV在前面，减负超支减正节约"}' \
  "{{ originUrl }}/api/v1/agent/explain-callback"</pre>
      </div>
    </div>

    <!-- Section 2: JSON / CSV Import -->
    <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-xs font-bold text-slate-800 uppercase">批量导入题库 (JSON)</h3>
        <button
          @click="prefillSampleJson"
          class="text-xs text-blue-600 hover:underline"
        >
          填入示例模版
        </button>
      </div>

      <textarea
        v-model="importJsonText"
        rows="6"
        placeholder="请粘贴符合题库 JSON Schema 的题目数组..."
        class="w-full p-3 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
      ></textarea>

      <div v-if="importFeedback" class="text-xs font-bold" :class="importSuccess ? 'text-emerald-600' : 'text-rose-600'">
        {{ importFeedback }}
      </div>

      <button
        @click="handleImportQuestions"
        :disabled="importing || !importJsonText.trim()"
        class="w-full py-3 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl text-xs shadow-md transition-all disabled:opacity-50"
      >
        {{ importing ? '正在校验并导入...' : '执行批量导入' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'

const originUrl = computed(() => {
  if (typeof window !== 'undefined') {
    return window.location.origin
  }
  return 'http://<SERVER_IP>'
})

const stats = ref({
  total_questions: 0,
  basic_questions: 0,
  case_questions: 0,
})

const agentKeys = ref<any[]>([])
const newKeyName = ref('')
const creatingKey = ref(false)

const importJsonText = ref('')
const importing = ref(false)
const importFeedback = ref('')
const importSuccess = ref(true)

async function loadStats() {
  try {
    const res: any = await adminApi.getStats()
    stats.value = res
  } catch (err) {
    console.error('Failed to load admin stats', err)
  }
}

async function loadAgentKeys() {
  try {
    const res: any = await adminApi.listAgentKeys()
    agentKeys.value = res
  } catch (err) {
    console.error('Failed to load agent keys', err)
  }
}

async function handleCreateKey() {
  if (!newKeyName.value.trim()) return
  creatingKey.value = true
  try {
    await adminApi.createAgentKey(newKeyName.value.trim())
    newKeyName.value = ''
    await loadAgentKeys()
  } catch (err) {
    alert('创建 Key 失败')
  } finally {
    creatingKey.value = false
  }
}

async function handleToggleKey(id: string) {
  try {
    await adminApi.toggleAgentKey(id)
    await loadAgentKeys()
  } catch (err) {
    alert('切换状态失败')
  }
}

async function handleDeleteKey(id: string) {
  if (!confirm('确定要删除此 Agent Key 吗？外部应用将立即失去访问权限！')) return
  try {
    await adminApi.deleteAgentKey(id)
    await loadAgentKeys()
  } catch (err) {
    alert('删除失败')
  }
}

function copyKey(key: string) {
  navigator.clipboard.writeText(key)
  alert('已复制 Key 到剪贴板')
}

function formatDate(dtStr: string) {
  if (!dtStr) return ''
  const d = new Date(dtStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function prefillSampleJson() {
  importJsonText.value = JSON.stringify(
    [
      {
        subject: 'basic',
        chapter: '项目进度管理',
        knowledge: '进度压缩与快速跟进',
        stem: '在进度受阻且预算有限的情况下，项目经理希望将原定串行开展的系统概要设计与数据库设计重叠并行进行。此做法采用的进度调整技术是（ ）。',
        options: [
          'A. 赶工',
          'B. 快速跟进',
          'C. 缩减范围',
          'D. 关键链法'
        ],
        correct_answer: 'B',
        analysis: '【解析】快速跟进将原本顺序进行的活动调整为并行进行，往往会增加返工风险但不会直接增加成本。',
        source: 'ai-generated',
        difficulty: 'medium'
      }
    ],
    null,
    2
  )
}

async function handleImportQuestions() {
  importFeedback.value = ''
  importing.value = true
  try {
    const list = JSON.parse(importJsonText.value)
    if (!Array.isArray(list)) {
      throw new Error('导入内容必须为 JSON 数组格式')
    }
    const res: any = await adminApi.importQuestions(list)
    importSuccess.value = true
    importFeedback.value = `导入成功！${res.message}`
    importJsonText.value = ''
    await loadStats()
  } catch (err: any) {
    importSuccess.value = false
    importFeedback.value = `导入失败：${err.message}`
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  loadStats()
  loadAgentKeys()
})
</script>
