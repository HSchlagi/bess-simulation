#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BESS-Simulation Server
Hauptanwendung für die Battery Energy Storage System Simulation
"""

import sys
import os

# Windows-Konsole auf UTF-8 setzen
if sys.platform == 'win32':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # UTF-8
    except:
        pass
    # Zusätzlich: PYTHONIOENCODING setzen
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from flask_socketio import SocketIO

if __name__ == '__main__':
    app = create_app()
    
    # WebSocket-Integration für Benachrichtigungen
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # WebSocket-Events registrieren
    from app.notification_routes import register_notification_socketio
    register_notification_socketio(socketio)
    
    print("[START] BESS-Simulation Server wird gestartet...")
    print("[INFO] Dashboard: http://127.0.0.1:5050/dashboard")
    print("[INFO] Admin-Panel: http://127.0.0.1:5050/admin/dashboard")
    print("[INFO] Export-Zentrum: http://127.0.0.1:5050/export/")
    print("[INFO] Benachrichtigungen: http://127.0.0.1:5050/notifications")
    print("=" * 50)
    
    # Server mit WebSocket-Support starten
    socketio.run(app, debug=True, host='127.0.0.1', port=5050)
