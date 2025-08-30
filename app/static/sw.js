// Service Worker für BESS Simulation PWA
const CACHE_NAME = 'bess-simulation-v1.0';
const urlsToCache = [
  '/',
  '/dashboard',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/img/bess_bat.jpg',
  '/static/favicon.ico',
  '/static/favicon-32x32.png',
  '/static/favicon-48x48.png',
  '/static/apple-touch-icon.png',
  'https://cdn.tailwindcss.com',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js'
];

// Service Worker Installation
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installation gestartet');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Cache geöffnet');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('Service Worker: Installation abgeschlossen');
        return self.skipWaiting();
      })
  );
});

// Service Worker Aktivierung
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Aktivierung gestartet');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Alten Cache löschen:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker: Aktivierung abgeschlossen');
      return self.clients.claim();
    })
  );
});

// Fetch Event Handler
self.addEventListener('fetch', (event) => {
  // API-Aufrufe nicht cachen
  if (event.request.url.includes('/api/')) {
    return;
  }
  
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Cache Hit - return response
        if (response) {
          return response;
        }
        
        // Kein Cache Hit - Netzwerk-Request
        return fetch(event.request)
          .then((response) => {
            // Prüfe ob gültige Response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // Response klonen
            const responseToCache = response.clone();
            
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });
            
            return response;
          })
          .catch(() => {
            // Offline Fallback für HTML-Seiten
            if (event.request.headers.get('accept').includes('text/html')) {
              return caches.match('/');
            }
          });
      })
  );
});

// Background Sync für Offline-Daten
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    console.log('Service Worker: Background Sync gestartet');
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  // Hier können Offline-Daten synchronisiert werden
  return Promise.resolve();
}

// Push Notifications
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push Notification erhalten');
  
  const options = {
    body: event.data ? event.data.text() : 'Neue BESS Simulation Benachrichtigung',
    icon: '/static/favicon-48x48.png',
    badge: '/static/favicon-32x32.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Öffnen',
        icon: '/static/favicon-32x32.png'
      },
      {
        action: 'close',
        title: 'Schließen',
        icon: '/static/favicon-32x32.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('BESS Simulation', options)
  );
});

// Notification Click Handler
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification Click');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/dashboard')
    );
  }
});
