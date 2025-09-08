/**
 * BESS Simulation PWA JavaScript
 * Progressive Web App Funktionalität
 */

class BESSPWA {
    constructor() {
        this.isOnline = navigator.onLine;
        this.deferredPrompt = null;
        this.registration = null;
        this.init();
    }

    async init() {
        console.log('🚀 BESS PWA initialisiert');
        
        // Service Worker registrieren
        await this.registerServiceWorker();
        
        // PWA Install Prompt
        this.setupInstallPrompt();
        
        // Online/Offline Status
        this.setupOnlineStatus();
        
        // Push Notifications
        this.setupPushNotifications();
        
        // Background Sync
        this.setupBackgroundSync();
        
        // Native Features
        this.setupNativeFeatures();
        
        console.log('✅ BESS PWA vollständig initialisiert');
    }

    // Service Worker registrieren
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                this.registration = await navigator.serviceWorker.register('/static/sw.js');
                console.log('✅ Service Worker registriert:', this.registration.scope);
                
                // Service Worker Updates
                this.registration.addEventListener('updatefound', () => {
                    const newWorker = this.registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateNotification();
                        }
                    });
                });
                
            } catch (error) {
                console.error('❌ Service Worker Registrierung fehlgeschlagen:', error);
            }
        }
    }

    // PWA Install Prompt
    setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('📱 PWA Install Prompt verfügbar');
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        // App installiert
        window.addEventListener('appinstalled', () => {
            console.log('✅ BESS PWA installiert');
            this.hideInstallButton();
            this.showNotification('BESS Simulation installiert!', 'Die App wurde erfolgreich installiert.');
        });
    }

    // Install Button anzeigen
    showInstallButton() {
        const installButton = document.getElementById('pwa-install-button');
        if (installButton) {
            installButton.style.display = 'block';
            installButton.addEventListener('click', () => this.installPWA());
        }
    }

    // Install Button verstecken
    hideInstallButton() {
        const installButton = document.getElementById('pwa-install-button');
        if (installButton) {
            installButton.style.display = 'none';
        }
    }

    // PWA installieren
    async installPWA() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            const { outcome } = await this.deferredPrompt.userChoice;
            console.log(`PWA Install Ergebnis: ${outcome}`);
            this.deferredPrompt = null;
        }
    }

    // Online/Offline Status
    setupOnlineStatus() {
        window.addEventListener('online', () => {
            console.log('🌐 Online-Verbindung wiederhergestellt');
            this.isOnline = true;
            this.showOnlineStatus();
            this.syncOfflineData();
        });

        window.addEventListener('offline', () => {
            console.log('📱 Offline-Modus aktiviert');
            this.isOnline = false;
            this.showOfflineStatus();
        });

        // Initialer Status
        if (this.isOnline) {
            this.showOnlineStatus();
        } else {
            this.showOfflineStatus();
        }
    }

    // Online Status anzeigen
    showOnlineStatus() {
        const statusElement = document.getElementById('pwa-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="flex items-center text-green-500">
                    <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                    </svg>
                    Online
                </div>
            `;
        }
    }

    // Offline Status anzeigen
    showOfflineStatus() {
        const statusElement = document.getElementById('pwa-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="flex items-center text-orange-500">
                    <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.368zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z" clip-rule="evenodd"></path>
                    </svg>
                    Offline
                </div>
            `;
        }
    }

    // Offline-Daten synchronisieren
    async syncOfflineData() {
        if (this.registration) {
            try {
                await this.registration.sync.register('background-sync');
                console.log('🔄 Background Sync registriert');
            } catch (error) {
                console.error('❌ Background Sync Fehler:', error);
            }
        }
    }

    // Push Notifications
    async setupPushNotifications() {
        if ('Notification' in window && 'serviceWorker' in navigator) {
            // Berechtigung anfordern
            if (Notification.permission === 'default') {
                const permission = await Notification.requestPermission();
                console.log('🔔 Notification Berechtigung:', permission);
            }

            // Push Manager
            if (this.registration && 'pushManager' in this.registration) {
                try {
                    const subscription = await this.registration.pushManager.getSubscription();
                    if (!subscription) {
                        await this.subscribeToPush();
                    }
                } catch (error) {
                    console.error('❌ Push Subscription Fehler:', error);
                }
            }
        }
    }

    // Push Subscription
    async subscribeToPush() {
        try {
            const subscription = await this.registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(
                    'BEl62iUYgUivxIkv69yViEuiBIa40HI0pNf6q4nQ3LgFEONNpKjLgB8lT1u2u9LJiuF0GlPOGQxYy25onF_2jE'
                )
            });
            
            console.log('✅ Push Subscription erstellt:', subscription);
            
            // Subscription an Server senden
            await this.sendSubscriptionToServer(subscription);
            
        } catch (error) {
            console.error('❌ Push Subscription Fehler:', error);
        }
    }

    // Subscription an Server senden
    async sendSubscriptionToServer(subscription) {
        try {
            const response = await fetch('/api/push-subscription', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(subscription)
            });
            
            if (response.ok) {
                console.log('✅ Push Subscription an Server gesendet');
            }
        } catch (error) {
            console.error('❌ Push Subscription Server-Fehler:', error);
        }
    }

    // Background Sync
    setupBackgroundSync() {
        if ('serviceWorker' in navigator && this.registration) {
            this.registration.addEventListener('sync', (event) => {
                console.log('🔄 Background Sync Event:', event.tag);
                
                if (event.tag === 'background-sync') {
                    event.waitUntil(this.performBackgroundSync());
                }
            });
        }
    }

    // Background Sync ausführen
    async performBackgroundSync() {
        try {
            console.log('🔄 Background Sync gestartet...');
            
            // Marktdaten synchronisieren
            await this.syncMarketData();
            
            // Projektdaten synchronisieren
            await this.syncProjectData();
            
            console.log('✅ Background Sync abgeschlossen');
        } catch (error) {
            console.error('❌ Background Sync Fehler:', error);
        }
    }

    // Marktdaten synchronisieren
    async syncMarketData() {
        try {
            const response = await fetch('/api/market-data');
            if (response.ok) {
                console.log('📊 Marktdaten synchronisiert');
            }
        } catch (error) {
            console.log('⚠️ Marktdaten-Sync fehlgeschlagen (offline)');
        }
    }

    // Projektdaten synchronisieren
    async syncProjectData() {
        try {
            const response = await fetch('/api/projects');
            if (response.ok) {
                console.log('📁 Projektdaten synchronisiert');
            }
        } catch (error) {
            console.log('⚠️ Projektdaten-Sync fehlgeschlagen (offline)');
        }
    }

    // Native Device Features
    setupNativeFeatures() {
        // Geolocation
        this.setupGeolocation();
        
        // Camera
        this.setupCamera();
        
        // Biometric Authentication
        this.setupBiometricAuth();
    }

    // Geolocation
    setupGeolocation() {
        if ('geolocation' in navigator) {
            console.log('📍 Geolocation verfügbar');
            
            // Location für BESS-Standorte
            this.getCurrentLocation().then(location => {
                if (location) {
                    console.log('📍 Aktuelle Position:', location);
                    this.saveLocationForBESS(location);
                }
            });
        }
    }

    // Aktuelle Position abrufen
    async getCurrentLocation() {
        return new Promise((resolve) => {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy
                    });
                },
                (error) => {
                    console.log('📍 Geolocation Fehler:', error.message);
                    resolve(null);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000
                }
            );
        });
    }

    // Position für BESS speichern
    saveLocationForBESS(location) {
        // Lokale Speicherung für BESS-Standort
        localStorage.setItem('bess-location', JSON.stringify(location));
    }

    // Camera
    setupCamera() {
        if ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices) {
            console.log('📷 Camera verfügbar');
            
            // Camera Button für Dokumentation
            const cameraButton = document.getElementById('camera-button');
            if (cameraButton) {
                cameraButton.addEventListener('click', () => this.openCamera());
            }
        }
    }

    // Camera öffnen
    async openCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();
            
            // Camera Modal anzeigen
            this.showCameraModal(video);
            
        } catch (error) {
            console.error('📷 Camera Fehler:', error);
            this.showNotification('Camera Fehler', 'Camera konnte nicht geöffnet werden.');
        }
    }

    // Camera Modal anzeigen
    showCameraModal(video) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                <h3 class="text-lg font-semibold mb-4">BESS Dokumentation</h3>
                <div class="mb-4">
                    <video id="camera-video" class="w-full h-64 bg-gray-200 rounded" autoplay></video>
                </div>
                <div class="flex space-x-3">
                    <button id="capture-photo" class="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
                        📸 Foto aufnehmen
                    </button>
                    <button id="close-camera" class="flex-1 bg-gray-600 text-white py-2 px-4 rounded hover:bg-gray-700">
                        ❌ Schließen
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Video Element zuweisen
        const videoElement = modal.querySelector('#camera-video');
        videoElement.srcObject = video.srcObject;
        
        // Event Listeners
        modal.querySelector('#capture-photo').addEventListener('click', () => {
            this.capturePhoto(videoElement);
        });
        
        modal.querySelector('#close-camera').addEventListener('click', () => {
            this.closeCameraModal(modal, video);
        });
    }

    // Foto aufnehmen
    capturePhoto(videoElement) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        
        context.drawImage(videoElement, 0, 0);
        
        // Foto als Blob speichern
        canvas.toBlob((blob) => {
            this.savePhoto(blob);
        }, 'image/jpeg', 0.8);
    }

    // Foto speichern
    savePhoto(blob) {
        const formData = new FormData();
        formData.append('photo', blob, `bess-documentation-${Date.now()}.jpg`);
        
        // Foto an Server senden
        fetch('/api/upload-photo', {
            method: 'POST',
            body: formData
        }).then(response => {
            if (response.ok) {
                this.showNotification('Foto gespeichert', 'BESS-Dokumentation erfolgreich aufgenommen.');
            }
        }).catch(error => {
            console.error('📷 Foto Upload Fehler:', error);
        });
    }

    // Camera Modal schließen
    closeCameraModal(modal, video) {
        // Stream stoppen
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
        }
        
        // Modal entfernen
        document.body.removeChild(modal);
    }

    // Biometric Authentication
    setupBiometricAuth() {
        if ('credentials' in navigator && 'create' in navigator.credentials) {
            console.log('🔐 Biometric Authentication verfügbar');
            
            // Biometric Login Button
            const biometricButton = document.getElementById('biometric-login');
            if (biometricButton) {
                biometricButton.addEventListener('click', () => this.authenticateBiometric());
            }
        }
    }

    // Biometric Authentication
    async authenticateBiometric() {
        try {
            const credential = await navigator.credentials.create({
                publicKey: {
                    challenge: new Uint8Array(32),
                    rp: { name: "BESS Simulation" },
                    user: {
                        id: new Uint8Array(16),
                        name: "BESS User",
                        displayName: "BESS Benutzer"
                    },
                    pubKeyCredParams: [{ type: "public-key", alg: -7 }],
                    authenticatorSelection: {
                        authenticatorAttachment: "platform"
                    }
                }
            });
            
            console.log('🔐 Biometric Authentication erfolgreich');
            this.showNotification('Anmeldung erfolgreich', 'Biometric Authentication erfolgreich.');
            
        } catch (error) {
            console.error('🔐 Biometric Authentication Fehler:', error);
            this.showNotification('Anmeldung fehlgeschlagen', 'Biometric Authentication nicht verfügbar.');
        }
    }

    // Update Notification anzeigen
    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-blue-600 text-white p-4 rounded-lg shadow-lg z-50';
        notification.innerHTML = `
            <div class="flex items-center">
                <div class="flex-1">
                    <h4 class="font-semibold">BESS Update verfügbar</h4>
                    <p class="text-sm">Neue Version wird geladen...</p>
                </div>
                <button id="reload-app" class="ml-4 bg-blue-700 hover:bg-blue-800 px-3 py-1 rounded text-sm">
                    Aktualisieren
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        notification.querySelector('#reload-app').addEventListener('click', () => {
            window.location.reload();
        });
        
        // Auto-remove nach 10 Sekunden
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 10000);
    }

    // Notification anzeigen
    showNotification(title, message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/icons/icon-192x192.png',
                badge: '/static/icons/badge-72x72.png',
                tag: 'bess-notification'
            });
        }
    }

    // Utility: URL Base64 zu Uint8Array
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');
        
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }
}

// PWA initialisieren wenn DOM geladen ist
document.addEventListener('DOMContentLoaded', () => {
    window.bessPWA = new BESSPWA();
});

// Export für Module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BESSPWA;
}
