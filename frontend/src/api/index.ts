import axios from 'axios'

const API_BASE = (import.meta as any).env?.VITE_API_BASE || '/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
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
