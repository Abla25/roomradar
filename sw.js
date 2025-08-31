// Service Worker for RoomRadar
// Improves performance through caching and offline support

const CACHE_NAME = 'roomradar-v1.0.0';
const STATIC_CACHE = 'roomradar-static-v1.0.0';
const DYNAMIC_CACHE = 'roomradar-dynamic-v1.0.0';

// Files to cache immediately
const STATIC_FILES = [
  '/',
  '/index.html',
  '/faq.html',
  '/how-it-works.html',
  '/profile.html',
  '/assets/css/navbar.css',
  '/assets/css/footer.css',
  '/assets/css/performance.css',
  '/assets/css/cookie-banner.css',
  '/assets/navbar.html',
  '/assets/footer.html',
  '/assets/js/firebase-config.js',
  '/assets/js/lazy-loader.js',
  '/assets/js/cookie-banner.js',
  '/vector-cropped-cropped (1).svg'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
  console.log('🔄 Service Worker installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('📦 Caching static files...');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('✅ Static files cached successfully');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('❌ Error caching static files:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('✅ Service Worker activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip Firebase requests (they handle their own caching)
  if (url.hostname.includes('firebase') || url.hostname.includes('googleapis')) {
    return;
  }
  
  // Handle different types of requests
  if (request.destination === 'document' || request.destination === '') {
    // HTML pages - cache first, then network
    event.respondWith(
      caches.match(request)
        .then((response) => {
          if (response) {
            console.log('📄 Serving HTML from cache:', url.pathname);
            return response;
          }
          
          return fetch(request)
            .then((networkResponse) => {
              // Cache successful responses
              if (networkResponse.status === 200) {
                const responseClone = networkResponse.clone();
                caches.open(DYNAMIC_CACHE)
                  .then((cache) => {
                    cache.put(request, responseClone);
                  });
              }
              return networkResponse;
            });
        })
        .catch(() => {
          // Fallback for offline
          if (request.destination === 'document') {
            return caches.match('/index.html');
          }
        })
    );
  } else if (request.destination === 'style' || request.destination === 'script') {
    // CSS and JS files - cache first, then network
    event.respondWith(
      caches.match(request)
        .then((response) => {
          if (response) {
            console.log('📦 Serving asset from cache:', url.pathname);
            return response;
          }
          
          return fetch(request)
            .then((networkResponse) => {
              if (networkResponse.status === 200) {
                const responseClone = networkResponse.clone();
                caches.open(DYNAMIC_CACHE)
                  .then((cache) => {
                    cache.put(request, responseClone);
                  });
              }
              return networkResponse;
            });
        })
    );
  } else if (request.destination === 'image') {
    // Images - network first, then cache
    event.respondWith(
      fetch(request)
        .then((networkResponse) => {
          if (networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(DYNAMIC_CACHE)
              .then((cache) => {
                cache.put(request, responseClone);
              });
          }
          return networkResponse;
        })
        .catch(() => {
          return caches.match(request);
        })
    );
  }
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    console.log('🔄 Background sync triggered');
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  try {
    // Handle any pending offline actions
    console.log('✅ Background sync completed');
  } catch (error) {
    console.error('❌ Background sync failed:', error);
  }
}

// Push notifications (if needed in the future)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/vector-cropped-cropped (1).svg',
      badge: '/vector-cropped-cropped (1).svg',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: 1
      }
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

