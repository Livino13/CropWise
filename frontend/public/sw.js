// Minimal service worker — makes the app installable; real caching via Workbox when vite-plugin-pwa is added.
self.addEventListener('install', (e) => self.skipWaiting())
self.addEventListener('activate', (e) => self.clients.claim())
self.addEventListener('fetch', (e) => {})
