import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'path'

export default defineConfig({
  base: './',
  plugins: [
    vue(),
    VitePWA({
      selfDestroying: true,
      registerType: 'prompt',
      includeAssets: ['favicon.ico', 'icon.svg'],
      manifest: {
        name: '软考中项刷题助手',
        short_name: '中项刷题',
        description: '软考中级系统集成项目管理工程师（第3版）移动端刷题助手',
        theme_color: '#16382e',
        background_color: '#16382e',
        display: 'standalone',
        orientation: 'portrait',
        icons: [
          {
            src: 'icon.svg',
            sizes: 'any',
            type: 'image/svg+xml',
            purpose: 'any maskable'
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
