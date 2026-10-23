import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(async () => {
  const plugins: unknown[] = [react()]

  // ponytail: optional Workbox — build still works without vite-plugin-pwa
  try {
    const { VitePWA } = await import('vite-plugin-pwa')
    plugins.unshift(
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['vite.svg'],
        manifest: false, // we ship public/manifest.json manually
        workbox: { globPatterns: ['**/*.{js,css,html,svg,png,woff2}'] },
      }),
    )
  } catch {
    // not installed — src/pwa.ts falls back to manual /sw.js
  }

  return {
    plugins: plugins as never[],
    resolve: { alias: { '@': path.resolve(__dirname, './src') } },
    server: { port: 5173, proxy: { '/api': 'http://localhost:8000' } },
  }
})
