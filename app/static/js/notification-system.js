/**
 * BESS-Simulation: Benachrichtigungs-System JavaScript
 * Real-time Benachrichtigungen mit WebSocket und Push-Notifications
 */

class NotificationSystem {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.unreadCount = 0;
        this.notifications = [];
        this.init();
    }

    init() {
        this.initWebSocket();
        this.initPushNotifications();
        this.initNotificationBell();
        this.loadUnreadCount();
    }

    initWebSocket() {
        // WebSocket-Verbindung initialisieren
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('🔔 Benachrichtigungs-WebSocket verbunden');
                this.isConnected = true;
                this.socket.emit('join_notifications');
            });

            this.socket.on('disconnect', () => {
                console.log('🔔 Benachrichtigungs-WebSocket getrennt');
                this.isConnected = false;
            });

            this.socket.on('notifications_update', (data) => {
                console.log('🔔 Neue Benachrichtigungen erhalten:', data);
                this.handleNewNotifications(data);
            });

            this.socket.on('joined_notifications', (data) => {
                console.log('🔔 Benachrichtigungs-Raum beigetreten:', data.room);
            });
        }
    }

    initPushNotifications() {
        // Service Worker für Push-Notifications registrieren
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            navigator.serviceWorker.register('/static/js/notification-sw.js')
                .then(registration => {
                    console.log('🔔 Service Worker registriert:', registration);
                    this.requestNotificationPermission();
                })
                .catch(error => {
                    console.error('🔔 Service Worker Registrierung fehlgeschlagen:', error);
                });
        }
    }

    async requestNotificationPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('🔔 Push-Benachrichtigungen aktiviert');
                this.subscribeToPushNotifications();
            } else {
                console.log('🔔 Push-Benachrichtigungen abgelehnt');
            }
        }
    }

    async subscribeToPushNotifications() {
        try {
            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array('BESS_VAPID_PUBLIC_KEY')
            });

            // Subscription an Server senden
            await fetch('/notifications/api/push-subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(subscription)
            });

            console.log('🔔 Push-Subscription erfolgreich');
        } catch (error) {
            console.error('🔔 Push-Subscription fehlgeschlagen:', error);
        }
    }

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

    initNotificationBell() {
        // Benachrichtigungs-Glocke in der Navigation hinzufügen
        this.createNotificationBell();
        this.updateNotificationBell();
    }

    createNotificationBell() {
        const nav = document.querySelector('nav') || document.querySelector('.navbar');
        if (nav && !document.getElementById('notificationBell')) {
            const bell = document.createElement('div');
            bell.id = 'notificationBell';
            bell.className = 'relative';
            bell.innerHTML = `
                <button onclick="notificationSystem.showNotificationCenter()" 
                        class="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg">
                    <i class="fas fa-bell text-xl"></i>
                    <span id="notificationBadge" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center hidden">0</span>
                </button>
            `;
            
            // Bell zur Navigation hinzufügen
            const navItems = nav.querySelector('.flex.items-center') || nav.querySelector('.nav-items');
            if (navItems) {
                navItems.appendChild(bell);
            }
        }
    }

    updateNotificationBell() {
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            if (this.unreadCount > 0) {
                badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
    }

    async loadUnreadCount() {
        try {
            const response = await fetch('/notifications/api/unread-count');
            const data = await response.json();
            
            if (data.success) {
                this.unreadCount = data.unread_count;
                this.updateNotificationBell();
            }
        } catch (error) {
            console.error('🔔 Fehler beim Laden der ungelesenen Anzahl:', error);
        }
    }

    handleNewNotifications(data) {
        if (data.notifications && data.notifications.length > 0) {
            this.unreadCount += data.notifications.length;
            this.updateNotificationBell();
            
            // Toast-Benachrichtigung anzeigen
            data.notifications.forEach(notification => {
                this.showToast(notification);
            });
        }
    }

    showToast(notification) {
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 z-50 bg-white border-l-4 border-blue-500 p-4 rounded-lg shadow-lg max-w-sm transform translate-x-full transition-transform duration-300';
        
        const priorityColors = {
            'high': 'border-red-500',
            'medium': 'border-yellow-500',
            'low': 'border-green-500'
        };

        const priorityIcons = {
            'high': 'fas fa-exclamation-triangle text-red-500',
            'medium': 'fas fa-info-circle text-yellow-500',
            'low': 'fas fa-check-circle text-green-500'
        };

        toast.className = toast.className.replace('border-blue-500', priorityColors[notification.priority] || 'border-blue-500');

        toast.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <i class="${priorityIcons[notification.priority] || 'fas fa-bell text-blue-500'}"></i>
                </div>
                <div class="ml-3 flex-1">
                    <h4 class="text-sm font-medium text-gray-900">${notification.title}</h4>
                    <p class="text-sm text-gray-600 mt-1">${notification.message}</p>
                    <div class="mt-2 flex space-x-2">
                        <button onclick="notificationSystem.markAsRead(${notification.id})" 
                                class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                            Als gelesen markieren
                        </button>
                        <button onclick="notificationSystem.showNotificationCenter()" 
                                class="text-gray-600 hover:text-gray-800 text-sm font-medium">
                            Alle anzeigen
                        </button>
                    </div>
                </div>
                <div class="ml-4 flex-shrink-0">
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" 
                            class="text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(toast);

        // Toast einblenden
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);

        // Toast nach 8 Sekunden ausblenden
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        }, 8000);
    }

    showNotificationCenter() {
        window.location.href = '/notifications';
    }

    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/notifications/api/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.unreadCount = Math.max(0, this.unreadCount - 1);
                this.updateNotificationBell();
            }
        } catch (error) {
            console.error('🔔 Fehler beim Markieren als gelesen:', error);
        }
    }

    // Hilfsfunktionen für andere Module
    async createNotification(type, title, message, priority = 'medium', data = {}) {
        try {
            const response = await fetch('/notifications/api/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type,
                    title,
                    message,
                    priority,
                    data,
                    channels: ['in_app', 'email']
                })
            });

            const result = await response.json();
            return result.success ? result.notification_id : null;
        } catch (error) {
            console.error('🔔 Fehler beim Erstellen der Benachrichtigung:', error);
            return null;
        }
    }

    // Spezielle Benachrichtigungs-Funktionen
    async notifySimulationComplete(projectName, results) {
        return await this.createNotification(
            'simulation_complete',
            `🎉 Simulation abgeschlossen - ${projectName}`,
            `Ihre BESS-Simulation für '${projectName}' wurde erfolgreich abgeschlossen.`,
            'high',
            {
                project_name: projectName,
                results: results,
                dashboard_url: `/dashboard?project=${results.project_id || ''}`
            }
        );
    }

    async notifySystemAlert(message, priority = 'medium') {
        return await this.createNotification(
            'system_alert',
            '⚠️ System-Alert',
            message,
            priority
        );
    }

    async notifyUserWelcome(userName) {
        return await this.createNotification(
            'user_welcome',
            '👋 Willkommen bei der BESS-Simulation!',
            `Willkommen ${userName}! Sie können jetzt BESS-Projekte erstellen und Simulationen durchführen.`,
            'medium',
            {
                user_name: userName,
                dashboard_url: '/dashboard'
            }
        );
    }
}

// Globale Instanz erstellen
window.notificationSystem = new NotificationSystem();

// Hilfsfunktionen für andere Module
window.createNotification = (type, title, message, priority, data) => {
    return window.notificationSystem.createNotification(type, title, message, priority, data);
};

window.notifySimulationComplete = (projectName, results) => {
    return window.notificationSystem.notifySimulationComplete(projectName, results);
};

window.notifySystemAlert = (message, priority) => {
    return window.notificationSystem.notifySystemAlert(message, priority);
};

window.notifyUserWelcome = (userName) => {
    return window.notificationSystem.notifyUserWelcome(userName);
};

// Periodische Aktualisierung der ungelesenen Anzahl
setInterval(() => {
    if (window.notificationSystem) {
        window.notificationSystem.loadUnreadCount();
    }
}, 30000); // alle 30 Sekunden
