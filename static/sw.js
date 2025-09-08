/**
 * BESS Simulation PWA Service Worker
 * Offline-Funktionalität für Simulationen und Marktdaten
 */

const CACHE_NAME = 'bess-simulation-v1.0.0';
const STATIC_CACHE = 'bess-static-v1.0.0';
const DYNAMIC_CACHE = 'bess-dynamic-v1.0.0';

// Offline-fähige Ressourcen
const STATIC_ASSETS = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/manifest.json',
  '/favicon.ico',
  '/offline.html'
];

// API-Endpunkte für Offline-Caching
const API_CACHE_PATTERNS = [
  '/api/projects',
  '/api/market-data',
  '/advanced-dispatch/api/optimize',
  '/co2/api/',
  '/simulation/api/'
];

// Install Event - Cache statische Assets
self.addEventListener('install', event => {
  console.log('🔧 BESS PWA Service Worker: Installation gestartet');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('📦 Statische Assets werden gecacht...');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('✅ Statische Assets erfolgreich gecacht');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('❌ Fehler beim Cachen statischer Assets:', error);
      })
  );
});

// Activate Event - Alte Caches bereinigen
self.addEventListener('activate', event => {
  console.log('🚀 BESS PWA Service Worker: Aktivierung gestartet');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('🗑️ Alte Cache-Version wird gelöscht:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('✅ Service Worker aktiviert');
        return self.clients.claim();
      })
  );
});

// Fetch Event - Offline-Funktionalität
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // API-Requests mit Cache-First Strategie
  if (API_CACHE_PATTERNS.some(pattern => url.pathname.includes(pattern))) {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // Statische Assets mit Cache-First Strategie
  if (request.destination === 'document' || 
      request.destination === 'script' || 
      request.destination === 'style' ||
      request.destination === 'image') {
    event.respondWith(handleStaticRequest(request));
    return;
  }

  // Alle anderen Requests mit Network-First Strategie
  event.respondWith(handleNetworkFirst(request));
});

// API-Request Handler (Cache-First für Offline-Simulationen)
async function handleApiRequest(request) {
  try {
    // Zuerst Cache prüfen
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('📱 API-Request aus Cache:', request.url);
      return cachedResponse;
    }

    // Network-Request
    const networkResponse = await fetch(request);
    
    // Erfolgreiche Response cachen
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
      console.log('💾 API-Response gecacht:', request.url);
    }

    return networkResponse;
  } catch (error) {
    console.log('🌐 Offline-Modus: API-Request fehlgeschlagen:', request.url);
    
    // Fallback für spezielle API-Endpunkte
    if (request.url.includes('/api/projects')) {
      return new Response(JSON.stringify({
        projects: [
          {
            id: 1,
            name: "BESS Hinterstoder",
            location: "Hinterstoder, Österreich",
            bess_power: 2.0,
            bess_size: 8.0,
            description: "Offline-Demo Projekt"
          }
        ]
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    if (request.url.includes('/api/market-data')) {
      return new Response(JSON.stringify({
        spot_prices: generateOfflineMarketData(),
        message: "Offline-Marktdaten (Demo)"
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Generischer Offline-Fallback
    return new Response(JSON.stringify({
      error: "Offline-Modus",
      message: "Keine Internetverbindung. Verwende gecachte Daten.",
      offline: true
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Statische Asset Handler (Cache-First)
async function handleStaticRequest(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.log('🌐 Offline-Modus: Statische Asset nicht verfügbar:', request.url);
    
    // Offline-Fallback für HTML-Seiten
    if (request.destination === 'document') {
      return caches.match('/offline.html');
    }
    
    throw error;
  }
}

// Network-First Handler
async function handleNetworkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// Background Sync für automatische Synchronisation
self.addEventListener('sync', event => {
  console.log('🔄 Background Sync Event:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

// Background Sync Implementation
async function doBackgroundSync() {
  try {
    console.log('🔄 Background Sync gestartet...');
    
    // Marktdaten synchronisieren
    await syncMarketData();
    
    // Projektdaten synchronisieren
    await syncProjectData();
    
    console.log('✅ Background Sync abgeschlossen');
  } catch (error) {
    console.error('❌ Background Sync Fehler:', error);
  }
}

// Marktdaten synchronisieren
async function syncMarketData() {
  try {
    const response = await fetch('/api/market-data');
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      await cache.put('/api/market-data', response);
      console.log('📊 Marktdaten synchronisiert');
    }
  } catch (error) {
    console.log('⚠️ Marktdaten-Sync fehlgeschlagen (offline)');
  }
}

// Projektdaten synchronisieren
async function syncProjectData() {
  try {
    const response = await fetch('/api/projects');
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      await cache.put('/api/projects', response);
      console.log('📁 Projektdaten synchronisiert');
    }
  } catch (error) {
    console.log('⚠️ Projektdaten-Sync fehlgeschlagen (offline)');
  }
}

// Push-Notifications
self.addEventListener('push', event => {
  console.log('🔔 Push-Notification empfangen');
  
  const options = {
    body: event.data ? event.data.text() : 'Neue BESS-Simulation verfügbar',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Simulation öffnen',
        icon: '/static/icons/action-explore.png'
      },
      {
        action: 'close',
        title: 'Schließen',
        icon: '/static/icons/action-close.png'
      }
    ],
    tag: 'bess-notification',
    renotify: true,
    requireInteraction: true
  };

  event.waitUntil(
    self.registration.showNotification('BESS Simulation', options)
  );
});

// Notification Click Handler
self.addEventListener('notificationclick', event => {
  console.log('🔔 Notification geklickt:', event.action);
  
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/advanced-dispatch/')
    );
  } else if (event.action === 'close') {
    // Notification schließen
    return;
  } else {
    // Standard: App öffnen
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Offline-Marktdaten Generator
function generateOfflineMarketData() {
  const now = new Date();
  const prices = [];
  
  for (let i = 0; i < 24; i++) {
    const hour = new Date(now.getTime() + i * 60 * 60 * 1000);
    const basePrice = 80 + Math.sin(i * Math.PI / 12) * 20;
    const randomVariation = (Math.random() - 0.5) * 10;
    
    prices.push({
      timestamp: hour.toISOString(),
      price: Math.max(0, basePrice + randomVariation),
      market: 'offline-demo'
    });
  }
  
  return prices;
}

// Message Handler für Kommunikation mit Main Thread
self.addEventListener('message', event => {
  console.log('📨 Service Worker Message:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});

console.log('🚀 BESS PWA Service Worker geladen');
