// Service Worker for caching strategies
const CACHE_NAME = 'pfinni-cache-v1'
const DYNAMIC_CACHE_NAME = 'pfinni-dynamic-v1'

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/favicon.ico',
]

// Cache strategies
const cacheStrategies = {
  // Cache first for static assets
  cacheFirst: async (request) => {
    const cache = await caches.open(CACHE_NAME)
    const cachedResponse = await cache.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  },

  // Network first for API calls
  networkFirst: async (request) => {
    try {
      const networkResponse = await fetch(request)
      if (networkResponse.ok) {
        const cache = await caches.open(DYNAMIC_CACHE_NAME)
        cache.put(request, networkResponse.clone())
      }
      return networkResponse
    } catch (error) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME)
      const cachedResponse = await cache.match(request)
      if (cachedResponse) {
        return cachedResponse
      }
      throw error
    }
  },

  // Stale while revalidate for images
  staleWhileRevalidate: async (request) => {
    const cache = await caches.open(CACHE_NAME)
    const cachedResponse = await cache.match(request)
    
    const networkResponsePromise = fetch(request).then(response => {
      if (response.ok) {
        cache.put(request, response.clone())
      }
      return response
    })

    return cachedResponse || networkResponsePromise
  }
}

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS)
    })
  )
  self.skipWaiting()
})

// Activate event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME && name !== DYNAMIC_CACHE_NAME)
          .map(name => caches.delete(name))
      )
    })
  )
  self.clients.claim()
})

// Fetch event
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return
  }

  // Skip webpack hot updates
  if (url.pathname.includes('webpack')) {
    return
  }

  // API calls - network first
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(cacheStrategies.networkFirst(request))
    return
  }

  // Images - stale while revalidate
  if (request.destination === 'image') {
    event.respondWith(cacheStrategies.staleWhileRevalidate(request))
    return
  }

  // Static assets - cache first
  if (
    request.destination === 'style' ||
    request.destination === 'script' ||
    request.destination === 'font'
  ) {
    event.respondWith(cacheStrategies.cacheFirst(request))
    return
  }

  // Default - network first
  event.respondWith(cacheStrategies.networkFirst(request))
})

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-patient-data') {
    event.waitUntil(syncPatientData())
  }
})

async function syncPatientData() {
  // Implement offline data sync logic here
  console.log('Syncing patient data...')
}