import axios from 'axios'
import { resolveApiBase } from '@/version'

const api = axios.create({
  baseURL: resolveApiBase(),
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  config.baseURL = resolveApiBase()
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function isAuthRequest(url?: string) {
  return !!url && /\/auth\/(login|register)(\?|$)/.test(url)
}

function goHashLogin() {
  if (window.location.hash.startsWith('#/login')) return
  window.location.hash = '#/login'
}

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const url = String(error.config?.url || '')
    if (error.response && error.response.status === 401 && !isAuthRequest(url)) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      goHashLogin()
    }
    const data = error.response?.data
    let message = error.message || '请求失败'
    if (typeof data === 'string' && data.trim()) {
      message = data
    } else if (data && typeof data === 'object' && !(data instanceof Blob) && data.detail) {
      message = Array.isArray(data.detail) ? data.detail[0]?.msg || '请求失败' : data.detail
    }
    return Promise.reject(new Error(typeof message === 'string' ? message : '请求失败'))
  }
)

export default api

// API Methods
export const authApi = {
  login: (data: any) => api.post('/auth/login', data),
  register: (data: any) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
  changePassword: (data: any) => api.post('/auth/change-password', data),
}

export const questionApi = {
  getChapters: (subject?: string) => api.get('/questions/chapters', { params: { subject } }),
  getKnowledgePoints: (chapter?: string, subject?: string) =>
    api.get('/questions/knowledge-points', { params: { chapter, subject } }),
  list: (params: any) => api.get('/questions/list', { params }),
  getDetail: (id: string) => api.get(`/questions/${id}`),
}

export const practiceApi = {
  submit: (data: { question_id: string; user_answer: string }) => api.post('/practice/submit', data),
}

export const examApi = {
  generate: (data: { subject: string; question_count: number; chapter?: string }) =>
    api.post('/exam/generate', data),
  submit: (data: { subject: string; time_spent: number; answers: Record<string, string> }) =>
    api.post('/exam/submit', data),
  history: () => api.get('/exam/history'),
}

export const wrongBookApi = {
  listWrong: (params?: any) => api.get('/wrong-book/wrong-questions', { params }),
  toggleMaster: (id: string, mastered: boolean) =>
    api.post(`/wrong-book/wrong-questions/${id}/master`, null, { params: { mastered } }),
  deleteWrong: (id: string) => api.delete(`/wrong-book/wrong-questions/${id}`),
  listFavorites: () => api.get('/wrong-book/favorites'),
  toggleFavorite: (questionId: string) => api.post(`/wrong-book/favorites/${questionId}`),
  getStatistics: () => api.get('/wrong-book/statistics'),
}

export const adminApi = {
  getStats: () => api.get('/admin/stats'),
  importQuestions: (questions: any[]) => api.post('/admin/import-questions', questions),
  importCsv: (formData: FormData) =>
    api.post('/admin/import-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  listAgentKeys: () => api.get('/admin/agent-keys'),
  createAgentKey: (name: string) => api.post('/admin/agent-keys', { name }),
  toggleAgentKey: (id: string) => api.post(`/admin/agent-keys/${id}/toggle`),
  deleteAgentKey: (id: string) => api.delete(`/admin/agent-keys/${id}`),
}

export const masteryApi = {
  getMe: () => api.get('/mastery/me'),
  weakDrill: (count: number = 10) => api.post('/mastery/weak-drill', { count }),
}

export const aiApi = {
  getQuota: () => api.get('/ai/quota'),
  createJob: (data: { question_id?: string; action_type: string; user_prompt?: string; user_context?: any }) =>
    api.post('/ai/jobs', data),
  getJob: (jobId: string) => api.get(`/ai/jobs/${jobId}`),
}

export const materialsApi = {
  list: (params?: any) => api.get('/materials', { params }),
  getStats: () => api.get('/materials/manifest/stats'),
  getFileBlob: (id: string, inline = true, onProgress?: (ratio: number) => void) =>
    api.get(`/materials/${id}/file`, {
      params: { inline },
      responseType: 'blob',
      timeout: 180000,
      onDownloadProgress: (ev) => {
        if (!onProgress) return
        if (ev.total) onProgress(ev.loaded / ev.total)
      },
    }) as Promise<Blob>,
  upload: (formData: FormData) =>
    api.post('/materials', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  delete: (id: string) => api.delete(`/materials/${id}`),
  convertToQuestions: (id: string) => api.post(`/materials/${id}/convert-questions`),
}

export const planApi = {
  getMe: () => api.get('/plan/me'),
  setConfig: (data: { exam_date: string; daily_minutes: number }) => api.post('/plan/config', data),
  toggleTask: (taskId: string) => api.post(`/plan/tasks/${taskId}/toggle`),
}

export const appApi = {
  checkUpdate: (params: { client_version?: string; client_version_code?: number; platform?: string }) =>
    api.get('/app/check-update', { params }),
  getLatestInfo: () => api.get('/app/latest-info'),
}

export const learnApi = {
  getChapters: () => api.get<any, any[]>('/learn/chapters'),
  listPoints: (params?: any) => api.get<any, any>('/learn/points', { params }),
  getPointDetail: (id: string) => api.get<any, any>(`/learn/points/${id}`),
  updatePointStatus: (id: string, status: string) => api.post<any, any>(`/learn/points/${id}/status`, { status }),
  getPointPractice: (id: string, limit: number = 5) => api.get<any, any>(`/learn/points/${id}/practice`, { params: { limit } }),
  getProgress: () => api.get<any, any>('/learn/progress'),
  listGlossary: (params?: any) => api.get<any, any>('/learn/glossary', { params }),
  getGlossaryDetail: (id: string) => api.get<any, any>(`/learn/glossary/${id}`),
  updateGlossaryStatus: (id: string, data: { known?: string; favorited?: boolean }) =>
    api.post<any, any>(`/learn/glossary/${id}/status`, data),
  generateQuiz: (tag?: string, count: number = 10) =>
    api.post<any, any[]>('/learn/glossary/quiz', null, { params: { tag, count } }),
  submitQuiz: (answers: Array<{ term_id: string; selected_option: string }>) =>
    api.post<any, any>('/learn/glossary/quiz/submit', { answers }),
  importPoints: (points: any[]) => api.post<any, any>('/admin/learn/points/import', points),
  importGlossary: (terms: any[]) => api.post<any, any>('/admin/learn/glossary/import', terms),
}

