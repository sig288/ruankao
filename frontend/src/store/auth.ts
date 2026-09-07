import { defineStore } from 'pinia'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
    username: (state) => state.user?.username || '考生',
  },
  actions: {
    async login(credentials: { username: string; password: string }) {
      const res: any = await authApi.login(credentials)
      this.token = res.access_token
      this.user = res.user
      localStorage.setItem('token', res.access_token)
      localStorage.setItem('user', JSON.stringify(res.user))
      return res
    },
    async register(credentials: { username: string; password: string }) {
      const res: any = await authApi.register(credentials)
      this.token = res.access_token
      this.user = res.user
      localStorage.setItem('token', res.access_token)
      localStorage.setItem('user', JSON.stringify(res.user))
      return res
    },
    async fetchMe() {
      if (!this.token) return
      try {
        const user: any = await authApi.me()
        this.user = user
        localStorage.setItem('user', JSON.stringify(user))
      } catch (err) {
        this.logout()
      }
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})
