// ponytail: manual SW fallback; swap to vite-plugin-pwa + Workbox precache when offline-first needed
export function registerPWA() {
  if (!('serviceWorker' in navigator)) return

  // Try Workbox's virtual module when vite-plugin-pwa is installed; otherwise manual fallback.
  // Variable import + @vite-ignore so Vite doesn't hard-resolve the virtual id at build time.
  const virtualId = 'virtual:pwa-register'
  import(/* @vite-ignore */ virtualId)
    .then((mod: { registerSW: (opts: unknown) => void }) => {
      mod.registerSW({
        immediate: true,
        onNeedRefresh() {},
        onOfflineReady() {},
      })
    })
    .catch(() => {
      // Manual fallback: register a no-op SW that enables installability
      navigator.serviceWorker.register('/sw.js').catch(() => {})
    })
}
