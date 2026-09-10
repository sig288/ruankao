<template>
  <div class="max-w-4xl mx-auto p-4 md:p-6 space-y-4">
    <!-- Header with Admin Role Badge -->
    <div class="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-xs flex items-center justify-between">
      <div>
        <h2 class="text-base font-bold text-slate-900">系统管理中心</h2>
        <p class="text-xs text-slate-400 mt-0.5">学员用户管理、全站统一 DeepSeek AI 调度、题库与外部 Agent 密钥</p>
      </div>
      <span class="px-2.5 py-1 bg-amber-50 text-amber-700 text-xs font-bold rounded-lg border border-amber-200">
        管理员权限
      </span>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex items-center space-x-1.5 overflow-x-auto pb-1 border-b border-slate-200/80">
      <button
        v-for="t in tabs"
        :key="t.key"
        @click="activeTab = t.key"
        class="px-3.5 py-2 text-xs font-semibold rounded-xl transition whitespace-nowrap"
        :class="activeTab === t.key ? 'bg-[#007AFF] text-white shadow-xs' : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200/60'"
      >
        {{ t.name }}
      </button>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 1: 概览与用量 -->
    <!-- ========================================================================= -->
    <div v-if="activeTab === 'overview'" class="space-y-4">
      <!-- Stats Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
        <div class="bg-white p-3.5 rounded-2xl border border-slate-200 shadow-xs">
          <div class="text-xl font-bold font-mono text-slate-800">{{ stats.total_questions }}</div>
          <div class="text-xs text-slate-400 mt-0.5 font-medium">题库总题量</div>
        </div>
        <div class="bg-white p-3.5 rounded-2xl border border-slate-200 shadow-xs">
          <div class="text-xl font-bold font-mono text-blue-600">{{ stats.total_users }}</div>
          <div class="text-xs text-slate-400 mt-0.5 font-medium">学员总数</div>
        </div>
        <div class="bg-white p-3.5 rounded-2xl border border-slate-200 shadow-xs">
          <div class="text-xl font-bold font-mono text-[#007AFF]">{{ stats.today_ai_jobs ?? 0 }}</div>
          <div class="text-xs text-slate-400 mt-0.5 font-medium">今日 AI 伴学调用</div>
        </div>
        <div class="bg-white p-3.5 rounded-2xl border border-slate-200 shadow-xs">
          <div class="text-xl font-bold font-mono text-emerald-600">{{ stats.total_ai_jobs ?? 0 }}</div>
          <div class="text-xs text-slate-400 mt-0.5 font-medium">历史 AI 累计调用</div>
        </div>
      </div>

      <!-- AI Usage Overview Card -->
      <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 class="text-sm font-bold text-slate-800">全站 AI 近 7 日调用走势</h3>
          <button @click="loadAiUsage" class="text-xs text-[#007AFF] hover:underline font-medium">刷新</button>
        </div>

        <div v-if="aiUsageData?.trend_7d?.length" class="grid grid-cols-7 gap-2 text-center pt-2">
          <div
            v-for="item in aiUsageData.trend_7d"
            :key="item.date"
            class="p-2.5 rounded-xl bg-slate-50 border border-slate-100"
          >
            <div class="text-xs font-mono font-bold text-blue-600">{{ item.count }}</div>
            <div class="text-[10px] text-slate-400 mt-1 font-mono">{{ item.date.slice(5) }}</div>
          </div>
        </div>

        <!-- Top Users Table -->
        <div v-if="aiUsageData?.top_users?.length" class="pt-3 border-t border-slate-100 space-y-2">
          <h4 class="text-xs font-bold text-slate-700">高频调用学员 Top 5（近 7 日）</h4>
          <div class="space-y-1.5">
            <div
              v-for="(u, idx) in aiUsageData.top_users"
              :key="u.user_id"
              class="flex items-center justify-between text-xs px-3 py-2 rounded-xl bg-slate-50 border border-slate-100"
            >
              <div class="flex items-center space-x-2">
                <span class="w-5 h-5 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-[10px]">
                  {{ idx + 1 }}
                </span>
                <span class="font-bold text-slate-800">{{ u.username }}</span>
              </div>
              <span class="font-mono text-blue-600 font-semibold">{{ u.count }} 次</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 2: 学员用户管理 (Proposal D2) -->
    <!-- ========================================================================= -->
    <div v-if="activeTab === 'users'" class="space-y-4">
      <!-- Toolbar: Search, Filters & Create User -->
      <div class="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-2.5">
        <div class="flex flex-wrap items-center gap-2 flex-1">
          <!-- Search input -->
          <input
            v-model="userFilter.search"
            @keyup.enter="loadUsers"
            type="text"
            placeholder="搜索用户名..."
            class="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 w-44"
          />

          <!-- Active Filter -->
          <select
            v-model="userFilter.is_active"
            @change="loadUsers"
            class="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none"
          >
            <option :value="undefined">全部状态</option>
            <option :value="true">正常启用</option>
            <option :value="false">已禁用</option>
          </select>

          <!-- AI Status Filter -->
          <select
            v-model="userFilter.ai_enabled"
            @change="loadUsers"
            class="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none"
          >
            <option :value="undefined">全部 AI 开关</option>
            <option :value="true">AI 已开通</option>
            <option :value="false">AI 未开通</option>
          </select>

          <button
            @click="loadUsers"
            class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl transition"
          >
            查询
          </button>
        </div>

        <button
          @click="openCreateUserModal"
          class="px-4 py-1.5 bg-[#007AFF] hover:bg-blue-600 text-white text-xs font-bold rounded-xl shadow-xs transition active:scale-95"
        >
          + 新建学员
        </button>
      </div>

      <!-- User List Table / Cards -->
      <div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div v-if="usersLoading" class="py-12 text-center text-xs text-slate-400">
          正在加载学员列表...
        </div>
        <div v-else-if="users.length === 0" class="py-12 text-center text-xs text-slate-400">
          未查询到符合条件的学员
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider text-[10px]">
              <tr>
                <th class="px-4 py-3">用户名 / 角色</th>
                <th class="px-3 py-3">账号状态</th>
                <th class="px-3 py-3">AI 开关</th>
                <th class="px-3 py-3">日额度</th>
                <th class="px-3 py-3">今日 AI</th>
                <th class="px-3 py-3">注册 / 最近登录</th>
                <th class="px-4 py-3 text-right">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="u in users" :key="u.id" class="hover:bg-slate-50/80 transition">
                <td class="px-4 py-3">
                  <div class="font-bold text-slate-800 flex items-center space-x-1.5">
                    <span>{{ u.username }}</span>
                    <span
                      v-if="u.role === 'admin'"
                      class="px-1.5 py-0.2 bg-amber-50 text-amber-700 border border-amber-200 text-[9px] rounded font-bold"
                    >
                      管理员
                    </span>
                  </div>
                  <div v-if="u.note" class="text-[10px] text-slate-400 mt-0.5 truncate max-w-xs">{{ u.note }}</div>
                </td>

                <!-- Active Toggle -->
                <td class="px-3 py-3">
                  <button
                    @click="handleToggleActive(u)"
                    class="px-2 py-0.5 rounded-full text-[10px] font-bold border transition active:scale-95"
                    :class="u.is_active ? 'bg-emerald-50 text-[#34C759] border-emerald-200' : 'bg-rose-50 text-[#FF3B30] border-rose-200'"
                  >
                    {{ u.is_active ? '正常' : '已禁用' }}
                  </button>
                </td>

                <!-- AI Switch Toggle -->
                <td class="px-3 py-3">
                  <button
                    @click="handleToggleAi(u)"
                    class="px-2 py-0.5 rounded-full text-[10px] font-bold border transition active:scale-95"
                    :class="u.ai_enabled ? 'bg-blue-50 text-[#007AFF] border-blue-200' : 'bg-slate-100 text-slate-500 border-slate-200'"
                  >
                    {{ u.ai_enabled ? '已开通' : '已关闭' }}
                  </button>
                </td>

                <!-- Quota -->
                <td class="px-3 py-3 font-mono">
                  <span v-if="u.ai_daily_quota !== null && u.ai_daily_quota !== undefined" class="text-blue-600 font-semibold">
                    {{ u.ai_daily_quota }} 次/天
                  </span>
                  <span v-else class="text-slate-400">
                    默认 (30)
                  </span>
                </td>

                <!-- Today Usage -->
                <td class="px-3 py-3 font-mono font-semibold text-slate-700">
                  {{ u.today_ai_usage }} 次
                </td>

                <!-- Timestamps -->
                <td class="px-3 py-3 text-[10px] text-slate-400 space-y-0.5">
                  <div>注册：{{ formatDate(u.created_at) }}</div>
                  <div>登录：{{ u.last_login_at ? formatDate(u.last_login_at) : '从未' }}</div>
                </td>

                <!-- Actions -->
                <td class="px-4 py-3 text-right space-x-2">
                  <button
                    @click="openEditQuotaModal(u)"
                    class="text-xs text-[#007AFF] hover:underline font-medium"
                  >
                    配额
                  </button>
                  <button
                    @click="openResetPasswordModal(u)"
                    class="text-xs text-slate-600 hover:underline font-medium"
                  >
                    重置密码
                  </button>
                  <button
                    @click="openUserAiUsageModal(u)"
                    class="text-xs text-indigo-600 hover:underline font-medium"
                  >
                    近7日
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 3: DeepSeek AI 全局配置 (Proposal D3) -->
    <!-- ========================================================================= -->
    <div v-if="activeTab === 'ai_config'" class="space-y-4">
      <!-- Core DeepSeek Config Card -->
      <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
              <span>全站一把 DeepSeek Key 统一调度</span>
              <span
                class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                :class="aiSettings.global_enabled ? 'bg-emerald-50 text-[#34C759] border border-emerald-200' : 'bg-rose-50 text-[#FF3B30] border border-rose-200'"
              >
                {{ aiSettings.global_enabled ? '服务正常运行' : '全站维护停用' }}
              </span>
            </h3>
            <p class="text-xs text-slate-400 mt-1">
              后台只需在此配置一段官方 API Key，全站学员端即可无感调用 DeepSeek 官方大模型，Key 永不出端。
            </p>
          </div>

          <button
            @click="handleTestConnectivity"
            :disabled="testingConnectivity"
            class="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs transition disabled:opacity-50 flex items-center space-x-1.5"
          >
            <span v-if="testingConnectivity" class="animate-spin text-sm">⏳</span>
            <span>{{ testingConnectivity ? '测试中...' : '⚡ 一键连通性测试' }}</span>
          </button>
        </div>

        <!-- Connectivity Test Result Banner -->
        <div
          v-if="testResult"
          class="p-3 rounded-xl text-xs flex items-center justify-between font-medium"
          :class="testResult.success ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'"
        >
          <div class="flex items-center space-x-2">
            <span>{{ testResult.success ? '✓' : '✗' }}</span>
            <span>{{ testResult.message }}</span>
          </div>
          <span v-if="testResult.latency_ms" class="font-mono text-[11px] font-bold">
            延迟: {{ testResult.latency_ms }} ms
          </span>
        </div>

        <!-- Form fields -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- API Key -->
          <div class="space-y-1 md:col-span-2">
            <label class="block text-xs font-bold text-slate-700">
              DeepSeek API Key (服务端私密存储，前端脱敏)
            </label>
            <div class="flex items-center space-x-2">
              <input
                v-model="aiSettingsForm.api_key"
                type="text"
                :placeholder="aiSettings.api_key || '请输入以 sk- 开头的 DeepSeek API Key'"
                class="flex-1 px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                v-if="aiSettings.api_key"
                @click="aiSettingsForm.api_key = ''"
                class="px-3 py-2 bg-slate-100 text-slate-600 rounded-xl text-xs hover:bg-slate-200"
              >
                重填
              </button>
            </div>
            <p class="text-[11px] text-slate-400">留空或输入包含 *** 时将保持服务端已有密钥不变。</p>
          </div>

          <!-- Base URL -->
          <div class="space-y-1">
            <label class="block text-xs font-bold text-slate-700">API 基础地址 (Base URL)</label>
            <input
              v-model="aiSettingsForm.base_url"
              type="text"
              placeholder="https://api.deepseek.com"
              class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-[10px] text-slate-400">官方默认：https://api.deepseek.com</p>
          </div>

          <!-- Default Model -->
          <div class="space-y-1">
            <label class="block text-xs font-bold text-slate-700">默认大模型 (Model)</label>
            <select
              v-model="aiSettingsForm.model"
              class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="deepseek-chat">deepseek-chat (DeepSeek-V3 默认推荐)</option>
              <option value="deepseek-reasoner">deepseek-reasoner (DeepSeek-R1 深度推理)</option>
            </select>
            <p class="text-[10px] text-slate-400">出厂默认为 deepseek-chat，速度快、解释清晰</p>
          </div>

          <!-- Default Daily Quota -->
          <div class="space-y-1">
            <label class="block text-xs font-bold text-slate-700">全局学员默认每日额度 (次)</label>
            <input
              v-model.number="aiSettingsForm.default_daily_quota"
              type="number"
              min="1"
              max="500"
              class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
            />
          </div>

          <!-- Global Kill Switch -->
          <div class="space-y-1">
            <label class="block text-xs font-bold text-slate-700">全站 AI 总开关 (Kill Switch)</label>
            <div class="flex items-center space-x-3 pt-1">
              <label class="flex items-center space-x-2 cursor-pointer text-xs">
                <input
                  v-model="aiSettingsForm.global_enabled"
                  type="checkbox"
                  class="rounded text-[#007AFF] focus:ring-blue-500 w-4 h-4"
                />
                <span class="font-semibold" :class="aiSettingsForm.global_enabled ? 'text-emerald-600' : 'text-rose-600'">
                  {{ aiSettingsForm.global_enabled ? '开启全站 AI 伴学' : '一键停用全员 AI 伴学 (紧急避险)' }}
                </span>
              </label>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
          <span class="text-[11px] text-slate-400">
            最近更新时间：{{ aiSettings.updated_at ? formatDate(aiSettings.updated_at) : '出厂默认' }}
          </span>
          <button
            @click="handleSaveAiSettings"
            :disabled="savingAiSettings"
            class="px-5 py-2.5 bg-[#007AFF] hover:bg-blue-600 text-white font-bold rounded-xl text-xs shadow-xs transition active:scale-95 disabled:opacity-50"
          >
            {{ savingAiSettings ? '正在保存...' : '保存 AI 全局配置' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 4: 外部 Agent Key 管理 (Existing) -->
    <!-- ========================================================================= -->
    <div v-if="activeTab === 'agent_keys'" class="space-y-4">
      <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
        <div>
          <h3 class="text-sm font-bold text-slate-800">外部 Agent 错题 API Key 管理</h3>
          <p class="text-xs text-slate-400 mt-0.5">供外部助教机器人或自动化脚本调用，与用户 JWT 登录完全隔离</p>
        </div>

        <!-- Add Key Form -->
        <div class="flex space-x-2">
          <input
            v-model="newKeyName"
            type="text"
            placeholder="例如：微信服务号Agent / 飞书助教"
            class="flex-1 px-3.5 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            @click="handleCreateKey"
            :disabled="!newKeyName.trim() || creatingKey"
            class="px-4 py-2 bg-[#007AFF] hover:bg-blue-600 text-white rounded-xl text-xs font-bold shadow-xs transition disabled:opacity-50"
          >
            生成新 Key
          </button>
        </div>

        <!-- Keys List -->
        <div class="space-y-2.5 pt-1">
          <div
            v-for="k in agentKeys"
            :key="k.id"
            class="p-3.5 bg-slate-50 border border-slate-200/80 rounded-xl text-xs space-y-2"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <span class="font-bold text-slate-800">{{ k.name }}</span>
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="k.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'"
                >
                  {{ k.is_active ? '有效' : '已停用' }}
                </span>
              </div>
              <div class="flex items-center space-x-2">
                <button
                  @click="handleToggleKey(k.id)"
                  class="text-xs text-blue-600 hover:underline font-medium"
                >
                  {{ k.is_active ? '停用' : '启用' }}
                </button>
                <button
                  @click="handleDeleteKey(k.id)"
                  class="text-xs text-rose-500 hover:underline font-medium"
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
                class="flex-1 px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-mono text-slate-700 select-all"
              />
              <button
                @click="copyKey(k.key)"
                class="px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg text-xs font-medium hover:bg-slate-100"
              >
                复制
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 5: 题库与考点批量导入 (Existing) -->
    <!-- ========================================================================= -->
    <div v-if="activeTab === 'import'" class="space-y-4">
      <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-bold text-slate-800">批量导入题库 (JSON)</h3>
          <button
            @click="prefillSampleJson"
            class="text-xs text-[#007AFF] hover:underline font-medium"
          >
            填入示例模版
          </button>
        </div>

        <textarea
          v-model="importJsonText"
          rows="7"
          placeholder="请粘贴符合题库 JSON Schema 的题目数组..."
          class="w-full p-3.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
        ></textarea>

        <div v-if="importFeedback" class="text-xs font-bold" :class="importSuccess ? 'text-emerald-600' : 'text-rose-600'">
          {{ importFeedback }}
        </div>

        <button
          @click="handleImportQuestions"
          :disabled="importing || !importJsonText.trim()"
          class="w-full py-3 bg-slate-900 hover:bg-black text-white font-bold rounded-xl text-xs shadow-xs transition disabled:opacity-50"
        >
          {{ importing ? '正在校验并导入...' : '执行批量导入' }}
        </button>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- MODALS: Create User / Reset Pwd / Edit Quota / 7d Usage -->
    <!-- ========================================================================= -->

    <!-- Modal 1: Create User -->
    <div v-if="showCreateUserModal" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-5 max-w-sm w-full space-y-4 shadow-xl">
        <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
          <h3 class="text-sm font-bold text-slate-800">新建学员账号</h3>
          <button @click="showCreateUserModal = false" class="text-slate-400 hover:text-slate-600 text-sm">✕</button>
        </div>

        <div class="space-y-3 text-xs">
          <div>
            <label class="block font-bold text-slate-700 mb-1">用户名 *</label>
            <input
              v-model="createUserForm.username"
              type="text"
              placeholder="请输入用户名"
              class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="block font-bold text-slate-700 mb-1">初始密码 (留空随机生成)</label>
            <input
              v-model="createUserForm.password"
              type="text"
              placeholder="默认随机，至少6位"
              class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="block font-bold text-slate-700 mb-1">管理员备注</label>
            <input
              v-model="createUserForm.note"
              type="text"
              placeholder="例如：2026秋季备考班"
              class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none"
            />
          </div>

          <div class="flex items-center space-x-2 pt-1">
            <input
              v-model="createUserForm.ai_enabled"
              id="m_ai_en"
              type="checkbox"
              class="rounded text-[#007AFF] w-4 h-4"
            />
            <label for="m_ai_en" class="font-medium text-slate-700">直接开通 AI 伴学权限</label>
          </div>
        </div>

        <div class="flex space-x-2 pt-2">
          <button
            @click="showCreateUserModal = false"
            class="flex-1 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs transition"
          >
            取消
          </button>
          <button
            @click="handleSubmitCreateUser"
            class="flex-1 py-2 bg-[#007AFF] hover:bg-blue-600 text-white font-bold rounded-xl text-xs shadow-xs transition"
          >
            确认创建
          </button>
        </div>
      </div>
    </div>

    <!-- Modal 2: Reset Password -->
    <div v-if="showResetPwdModal" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-5 max-w-sm w-full space-y-4 shadow-xl">
        <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
          <h3 class="text-sm font-bold text-slate-800">重置密码 · {{ targetUser?.username }}</h3>
          <button @click="showResetPwdModal = false" class="text-slate-400 hover:text-slate-600 text-sm">✕</button>
        </div>

        <div class="space-y-2 text-xs">
          <label class="block font-bold text-slate-700">输入新密码 (至少 6 位)</label>
          <input
            v-model="resetPwdInput"
            type="text"
            placeholder="请输入新密码"
            class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
          />
        </div>

        <div class="flex space-x-2 pt-2">
          <button
            @click="showResetPwdModal = false"
            class="flex-1 py-2 bg-slate-100 text-slate-700 font-semibold rounded-xl text-xs"
          >
            取消
          </button>
          <button
            @click="handleSubmitResetPwd"
            class="flex-1 py-2 bg-[#007AFF] text-white font-bold rounded-xl text-xs"
          >
            确认重置
          </button>
        </div>
      </div>
    </div>

    <!-- Modal 3: Edit AI Quota & Switch -->
    <div v-if="showEditQuotaModal" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-5 max-w-sm w-full space-y-4 shadow-xl">
        <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
          <h3 class="text-sm font-bold text-slate-800">配置 AI 权限 · {{ targetUser?.username }}</h3>
          <button @click="showEditQuotaModal = false" class="text-slate-400 hover:text-slate-600 text-sm">✕</button>
        </div>

        <div class="space-y-3 text-xs">
          <div class="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
            <span class="font-bold text-slate-700">是否允许该学员调用 AI</span>
            <input
              v-model="editQuotaForm.ai_enabled"
              type="checkbox"
              class="rounded text-[#007AFF] w-5 h-5"
            />
          </div>

          <div>
            <label class="block font-bold text-slate-700 mb-1">每日配额上限 (次)</label>
            <input
              v-model.number="editQuotaForm.ai_daily_quota"
              type="number"
              min="0"
              max="500"
              placeholder="留空则跟随全局默认(30)"
              class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none font-mono"
            />
            <p class="text-[10px] text-slate-400 mt-1">设为空或 0 时继承系统全局默认额度。</p>
          </div>
        </div>

        <div class="flex space-x-2 pt-2">
          <button
            @click="showEditQuotaModal = false"
            class="flex-1 py-2 bg-slate-100 text-slate-700 font-semibold rounded-xl text-xs"
          >
            取消
          </button>
          <button
            @click="handleSubmitEditQuota"
            class="flex-1 py-2 bg-[#007AFF] text-white font-bold rounded-xl text-xs"
          >
            保存配额
          </button>
        </div>
      </div>
    </div>

    <!-- Modal 4: User 7-day Usage Details -->
    <div v-if="showUserUsageModal" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-5 max-w-md w-full space-y-4 shadow-xl">
        <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
          <h3 class="text-sm font-bold text-slate-800">近 7 日 AI 调用统计 · {{ targetUser?.username }}</h3>
          <button @click="showUserUsageModal = false" class="text-slate-400 hover:text-slate-600 text-sm">✕</button>
        </div>

        <div v-if="userUsageHistory?.history?.length" class="space-y-2">
          <div
            v-for="item in userUsageHistory.history"
            :key="item.date"
            class="flex items-center justify-between text-xs px-3 py-2 rounded-xl bg-slate-50 border border-slate-100"
          >
            <span class="font-mono text-slate-600">{{ item.date }}</span>
            <span class="font-mono font-bold text-blue-600">{{ item.count }} 次</span>
          </div>
        </div>
        <div v-else class="py-8 text-center text-xs text-slate-400">
          该学员暂无 AI 调用记录
        </div>

        <button
          @click="showUserUsageModal = false"
          class="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs transition"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { adminApi } from '@/api'

const tabs = [
  { key: 'overview', name: '概览与用量' },
  { key: 'users', name: '学员用户管理' },
  { key: 'ai_config', name: 'DeepSeek AI 全局配置' },
  { key: 'agent_keys', name: '外部 Agent Key' },
  { key: 'import', name: '批量导入题库' },
]
const activeTab = ref('overview')

// Overview Stats
const stats = ref<any>({
  total_questions: 0,
  basic_questions: 0,
  case_questions: 0,
  total_users: 0,
  today_ai_jobs: 0,
  total_ai_jobs: 0,
})
const aiUsageData = ref<any>(null)

// Users State
const users = ref<any[]>([])
const usersLoading = ref(false)
const userFilter = reactive({
  search: '',
  is_active: undefined as boolean | undefined,
  ai_enabled: undefined as boolean | undefined,
})

// Modals State
const showCreateUserModal = ref(false)
const createUserForm = reactive({
  username: '',
  password: '',
  role: 'user',
  note: '',
  ai_enabled: false,
  ai_daily_quota: null as number | null,
})

const showResetPwdModal = ref(false)
const resetPwdInput = ref('')
const targetUser = ref<any>(null)

const showEditQuotaModal = ref(false)
const editQuotaForm = reactive({
  ai_enabled: false,
  ai_daily_quota: null as number | null,
})

const showUserUsageModal = ref(false)
const userUsageHistory = ref<any>(null)

// AI Settings State (Proposal D3)
const aiSettings = ref<any>({})
const aiSettingsForm = reactive({
  api_key: '',
  base_url: 'https://api.deepseek.com',
  model: 'deepseek-chat',
  default_daily_quota: 30,
  global_enabled: true,
})
const savingAiSettings = ref(false)
const testingConnectivity = ref(false)
const testResult = ref<any>(null)

// Agent Keys & Import State
const agentKeys = ref<any[]>([])
const newKeyName = ref('')
const creatingKey = ref(false)
const importJsonText = ref('')
const importing = ref(false)
const importFeedback = ref('')
const importSuccess = ref(true)

// ==========================================
// Data Loaders
// ==========================================

async function loadStats() {
  try {
    const res: any = await adminApi.getStats()
    stats.value = res
  } catch (err) {
    console.error('Failed to load stats', err)
  }
}

async function loadAiUsage() {
  try {
    const res: any = await adminApi.getAiUsageStats()
    aiUsageData.value = res
  } catch (err) {
    console.error('Failed to load AI usage stats', err)
  }
}

async function loadUsers() {
  usersLoading.value = true
  try {
    const params: any = {}
    if (userFilter.search.trim()) params.search = userFilter.search.trim()
    if (userFilter.is_active !== undefined) params.is_active = userFilter.is_active
    if (userFilter.ai_enabled !== undefined) params.ai_enabled = userFilter.ai_enabled

    const res: any = await adminApi.listUsers(params)
    users.value = res
  } catch (err) {
    console.error('Failed to load users', err)
  } finally {
    usersLoading.value = false
  }
}

async function loadAiSettings() {
  try {
    const res: any = await adminApi.getAiSettings()
    aiSettings.value = res
    aiSettingsForm.base_url = res.base_url || 'https://api.deepseek.com'
    aiSettingsForm.model = res.model || 'deepseek-chat'
    aiSettingsForm.default_daily_quota = res.default_daily_quota || 30
    aiSettingsForm.global_enabled = res.global_enabled !== false
  } catch (err) {
    console.error('Failed to load AI settings', err)
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

// ==========================================
// User Management Actions (D2)
// ==========================================

function openCreateUserModal() {
  createUserForm.username = ''
  createUserForm.password = ''
  createUserForm.role = 'user'
  createUserForm.note = ''
  createUserForm.ai_enabled = false
  createUserForm.ai_daily_quota = null
  showCreateUserModal.value = true
}

async function handleSubmitCreateUser() {
  if (!createUserForm.username.trim()) {
    alert('请输入用户名')
    return
  }
  try {
    await adminApi.createUser({
      username: createUserForm.username.trim(),
      password: createUserForm.password.trim() || undefined,
      role: createUserForm.role,
      note: createUserForm.note.trim() || undefined,
      ai_enabled: createUserForm.ai_enabled,
      ai_daily_quota: createUserForm.ai_daily_quota || undefined,
    })
    alert('学员创建成功！')
    showCreateUserModal.value = false
    await loadUsers()
    await loadStats()
  } catch (err: any) {
    alert(`创建失败：${err.message}`)
  }
}

async function handleToggleActive(u: any) {
  const next = !u.is_active
  if (!confirm(`确定要${next ? '启用' : '禁用'}学员账号「${u.username}」吗？`)) return
  try {
    await adminApi.updateUser(u.id, { is_active: next })
    u.is_active = next
  } catch (err: any) {
    alert(`操作失败：${err.message}`)
  }
}

async function handleToggleAi(u: any) {
  const next = !u.ai_enabled
  try {
    await adminApi.updateUserAi(u.id, {
      ai_enabled: next,
      ai_daily_quota: u.ai_daily_quota,
    })
    u.ai_enabled = next
  } catch (err: any) {
    alert(`操作失败：${err.message}`)
  }
}

function openResetPasswordModal(u: any) {
  targetUser.value = u
  resetPwdInput.value = ''
  showResetPwdModal.value = true
}

async function handleSubmitResetPwd() {
  if (!resetPwdInput.value || resetPwdInput.value.length < 6) {
    alert('新密码长度不能少于 6 位')
    return
  }
  try {
    await adminApi.resetPassword(targetUser.value.id, resetPwdInput.value)
    alert(`用户 ${targetUser.value.username} 密码已重置成功！`)
    showResetPwdModal.value = false
  } catch (err: any) {
    alert(`重置失败：${err.message}`)
  }
}

function openEditQuotaModal(u: any) {
  targetUser.value = u
  editQuotaForm.ai_enabled = u.ai_enabled
  editQuotaForm.ai_daily_quota = u.ai_daily_quota
  showEditQuotaModal.value = true
}

async function handleSubmitEditQuota() {
  try {
    await adminApi.updateUserAi(targetUser.value.id, {
      ai_enabled: editQuotaForm.ai_enabled,
      ai_daily_quota: editQuotaForm.ai_daily_quota || null,
    })
    targetUser.value.ai_enabled = editQuotaForm.ai_enabled
    targetUser.value.ai_daily_quota = editQuotaForm.ai_daily_quota || null
    alert('配额保存成功！')
    showEditQuotaModal.value = false
  } catch (err: any) {
    alert(`保存失败：${err.message}`)
  }
}

async function openUserAiUsageModal(u: any) {
  targetUser.value = u
  try {
    const res: any = await adminApi.getUserAiUsage(u.id)
    userUsageHistory.value = res
    showUserUsageModal.value = true
  } catch (err: any) {
    alert(`查询失败：${err.message}`)
  }
}

// ==========================================
// AI Settings & Connectivity Actions (D3)
// ==========================================

async function handleTestConnectivity() {
  testingConnectivity.value = true
  testResult.value = null
  try {
    const res: any = await adminApi.testAiConnectivity()
    testResult.value = res
  } catch (err: any) {
    testResult.value = {
      success: false,
      message: `请求失败: ${err.message}`,
    }
  } finally {
    testingConnectivity.value = false
  }
}

async function handleSaveAiSettings() {
  savingAiSettings.value = true
  try {
    const payload: any = {
      base_url: aiSettingsForm.base_url,
      model: aiSettingsForm.model,
      default_daily_quota: aiSettingsForm.default_daily_quota,
      global_enabled: aiSettingsForm.global_enabled,
    }
    if (aiSettingsForm.api_key && !aiSettingsForm.api_key.includes('***')) {
      payload.api_key = aiSettingsForm.api_key.trim()
    }
    const res: any = await adminApi.updateAiSettings(payload)
    aiSettings.value = res
    aiSettingsForm.api_key = ''
    alert('DeepSeek AI 配置已保存并实时生效！')
  } catch (err: any) {
    alert(`保存失败：${err.message}`)
  } finally {
    savingAiSettings.value = false
  }
}

// ==========================================
// Agent Key & Import Actions
// ==========================================

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

function prefillSampleJson() {
  importJsonText.value = JSON.stringify(
    [
      {
        subject: 'basic',
        chapter: '项目进度管理',
        knowledge: '进度压缩与快速跟进',
        stem: '在进度受阻且预算有限的情况下，项目经理希望将原定串行开展的系统概要设计与数据库设计重叠并行进行。此做法采用的进度调整技术是（ ）。',
        options: ['A. 赶工', 'B. 快速跟进', 'C. 缩减范围', 'D. 关键链法'],
        correct_answer: 'B',
        analysis: '【解析】快速跟进将原本顺序进行的活动调整为并行进行，往往会增加返工风险但不会直接增加成本。',
        source: 'ai-generated',
        difficulty: 'medium',
      },
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

function formatDate(dtStr: string) {
  if (!dtStr) return ''
  const d = new Date(dtStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

onMounted(() => {
  loadStats()
  loadAiUsage()
  loadUsers()
  loadAiSettings()
  loadAgentKeys()
})
</script>
