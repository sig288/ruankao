export const APP_VERSION = '3.2.1'
export const APP_VERSION_CODE = 321
export const H5_BUILD = '20260908b'
export const LIVE_H5_URL = 'https://122.51.95.218/ruankao/'
export const LIVE_API_BASE = 'https://122.51.95.218/api/v1'
export const APPLIED_H5_CODE_KEY = 'rk_applied_h5_code'

export function isNativeApp() {
  const cap = (window as any).Capacitor
  return Boolean(
    cap?.isNativePlatform?.()
    || cap?.isNativePlatform === true
    || window.location.protocol === 'capacitor:'
    || window.location.protocol === 'ionic:'
    || document.documentElement.classList.contains('is-native')
    || /;\s*wv\)/i.test(navigator.userAgent)
  )
}

export function resolveApiBase() {
  const custom = localStorage.getItem('custom_api_base')
  if (custom && custom.trim()) return custom.trim().replace(/\/$/, '')
  const envBase = (import.meta as any).env?.VITE_API_BASE
  if (envBase) return envBase
  if (isNativeApp() || liveH5Origin()) return LIVE_API_BASE
  return '/api/v1'
}

export function resolveApkUrl(downloadUrl?: string) {
  const path = downloadUrl || '/api/v1/app/download-apk'
  if (/^https?:\/\//i.test(path)) return path
  if (isNativeApp()) {
    return path.startsWith('/api/')
      ? `https://122.51.95.218${path}`
      : `${LIVE_API_BASE}${path.startsWith('/') ? path : `/${path}`}`
  }
  return path
}

export async function clearWebCaches() {
  if ('serviceWorker' in navigator) {
    const regs = await navigator.serviceWorker.getRegistrations()
    await Promise.all(regs.map((r) => r.unregister()))
  }
  if ('caches' in window) {
    const keys = await window.caches.keys()
    await Promise.all(keys.map((k) => window.caches.delete(k)))
  }
}

export function liveH5Origin(): boolean {
  return window.location.hostname === '122.51.95.218'
}

/** 3.2.1+ 热更新：永远刷新线上 H5，绝不 reload 壳内本地包。 */
export async function applyHotUpdate(latestCode: number) {
  localStorage.setItem(APPLIED_H5_CODE_KEY, String(latestCode))
  await clearWebCaches()
  const base = (isNativeApp() && !liveH5Origin()) ? LIVE_H5_URL : window.location.href
  const url = new URL(base, window.location.origin)
  url.searchParams.set('_rk', String(Date.now()))
  window.location.replace(url.toString())
}
