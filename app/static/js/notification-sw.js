/**
 * BESS-Simulation: Service Worker für Push-Benachrichtigungen
 * Verarbeitet Push-Notifications und zeigt sie an
 */

const CACHE_NAME = 'bess-notifications-v1';
const NOTIFICATION_ICON = '/static/images/bess-icon.png';

// Service Worker Installation
self.addEventListener('install', event => {
    console.log('🔔 Notification Service Worker installiert');
    self.skipWaiting();
});

// Service Worker Aktivierung
self.addEventListener('activate', event => {
    console.log('🔔 Notification Service Worker aktiviert');
    event.waitUntil(self.clients.claim());
});

// Push-Events verarbeiten
self.addEventListener('push', event => {
    console.log('🔔 Push-Event empfangen:', event);
    
    let notificationData = {
        title: 'BESS-Simulation',
        body: 'Neue Benachrichtigung',
        icon: NOTIFICATION_ICON,
        badge: NOTIFICATION_ICON,
        tag: 'bess-notification',
        requireInteraction: false,
        actions: [
            {
                action: 'view',
                title: 'Anzeigen',
                icon: '/static/images/view-icon.png'
            },
            {
                action: 'dismiss',
                title: 'Verwerfen',
                icon: '/static/images/dismiss-icon.png'
            }
        ],
        data: {
            url: '/notifications',
            timestamp: Date.now()
        }
    };

    // Push-Daten verarbeiten falls vorhanden
    if (event.data) {
        try {
            const pushData = event.data.json();
            notificationData = {
                ...notificationData,
                ...pushData,
                data: {
                    ...notificationData.data,
                    ...pushData.data
                }
            };
        } catch (error) {
            console.error('🔔 Fehler beim Parsen der Push-Daten:', error);
        }
    }

    // Benachrichtigung anzeigen
    event.waitUntil(
        self.registration.showNotification(notificationData.title, notificationData)
    );
});

// Benachrichtigungs-Klicks verarbeiten
self.addEventListener('notificationclick', event => {
    console.log('🔔 Benachrichtigung geklickt:', event);
    
    event.notification.close();

    if (event.action === 'view' || !event.action) {
        // Zur Benachrichtigungs-Seite navigieren
        event.waitUntil(
            clients.matchAll({ type: 'window' }).then(clientList => {
                // Prüfen ob bereits ein Fenster geöffnet ist
                for (const client of clientList) {
                    if (client.url.includes('bess') && 'focus' in client) {
                        return client.focus();
                    }
                }
                
                // Neues Fenster öffnen
                if (clients.openWindow) {
                    const url = event.notification.data?.url || '/notifications';
                    return clients.openWindow(url);
                }
            })
        );
    } else if (event.action === 'dismiss') {
        // Benachrichtigung verwerfen - nichts zu tun
        console.log('🔔 Benachrichtigung verworfen');
    }
});

// Background Sync für Offline-Funktionalität
self.addEventListener('sync', event => {
    console.log('🔔 Background Sync Event:', event.tag);
    
    if (event.tag === 'notification-sync') {
        event.waitUntil(syncNotifications());
    }
});

// Benachrichtigungen synchronisieren
async function syncNotifications() {
    try {
        // Hier würde die Synchronisation der Benachrichtigungen stattfinden
        console.log('🔔 Synchronisiere Benachrichtigungen...');
        
        // Beispiel: Ungelesene Benachrichtigungen abrufen
        const response = await fetch('/notifications/api/unread-count');
        if (response.ok) {
            const data = await response.json();
            console.log('🔔 Ungelesene Benachrichtigungen:', data.unread_count);
        }
    } catch (error) {
        console.error('🔔 Fehler bei der Benachrichtigungs-Synchronisation:', error);
    }
}

// Message-Events für Kommunikation mit der Hauptanwendung
self.addEventListener('message', event => {
    console.log('🔔 Message Event empfangen:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: CACHE_NAME });
    }
});

// Cache-Management
self.addEventListener('fetch', event => {
    // Nur für Benachrichtigungs-APIs cachen
    if (event.request.url.includes('/notifications/api/')) {
        event.respondWith(
            caches.open(CACHE_NAME).then(cache => {
                return cache.match(event.request).then(response => {
                    if (response) {
                        // Cache-First für API-Aufrufe
                        return response;
                    }
                    
                    return fetch(event.request).then(fetchResponse => {
                        // Nur erfolgreiche Responses cachen
                        if (fetchResponse.status === 200) {
                            cache.put(event.request, fetchResponse.clone());
                        }
                        return fetchResponse;
                    });
                });
            })
        );
    }
});

// Fehlerbehandlung
self.addEventListener('error', event => {
    console.error('🔔 Service Worker Fehler:', event.error);
});

self.addEventListener('unhandledrejection', event => {
    console.error('🔔 Service Worker Unhandled Rejection:', event.reason);
});

console.log('🔔 BESS Notification Service Worker geladen');
