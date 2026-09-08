import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import { H5_BUILD, LIVE_H5_URL, isNativeApp } from './version'
document.documentElement.dataset.build = H5_BUILD

;(window as any).__rkOnBack = (window as any).__rkOnBack || function () {
  if (window.history.length > 1) {
    window.history.back()
    return true
  }
  return false
}

function markNativeShell(): boolean {
  const isNative = isNativeApp()
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches
    || (window.navigator as any).standalone === true
  if (isNative || isStandalone) {
    document.documentElement.classList.add('is-native')
  }
  if (window.innerWidth <= 480) {
    document.documentElement.classList.add('is-phone')
  }
  if (isNative && 'serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then((regs) => {
      regs.forEach((r) => r.unregister())
    }).catch(() => {})
  }
  // 壳内本地包无法热更新：直接跳到线上 H5（仅新包内的 JS 会执行到这里）
  if (isNative && !window.location.hostname.includes('122.51.95.218')) {
    const joiner = LIVE_H5_URL.includes('?') ? '&' : '?'
    window.location.replace(`${LIVE_H5_URL}${joiner}_rk=${Date.now()}`)
    return false
  }
  return true
}

if (markNativeShell()) {
  const app = createApp(App)
  const pinia = createPinia()
  app.use(pinia)
  app.use(router)
  app.mount('#app')
}
