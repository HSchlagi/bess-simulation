#!/usr/bin/env python3
"""
BESS-Simulation Server
Hauptanwendung für die Battery Energy Storage System Simulation
"""

from app import create_app
from flask_socketio import SocketIO

if __name__ == '__main__':
    app = create_app()
    
    # WebSocket-Integration für Benachrichtigungen
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # WebSocket-Events registrieren
    from app.notification_routes import register_notification_socketio
    register_notification_socketio(socketio)
    
    print("🚀 BESS-Simulation Server wird gestartet...")
    print("📊 Dashboard: http://127.0.0.1:5050/dashboard")
    print("🔧 Admin-Panel: http://127.0.0.1:5050/admin/dashboard")
    print("📤 Export-Zentrum: http://127.0.0.1:5050/export/")
    print("🔔 Benachrichtigungen: http://127.0.0.1:5050/notifications")
    print("=" * 50)
    
    # Server mit WebSocket-Support starten
    socketio.run(app, debug=True, host='127.0.0.1', port=5050)
