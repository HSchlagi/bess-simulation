#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfacher Server-Start für BESS-Simulation
"""

import os
import sys

# Windows-Konsole auf UTF-8 setzen
if sys.platform == 'win32':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # UTF-8
    except:
        pass
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    print("=" * 60)
    print("BESS-Simulation Server wird gestartet...")
    print("Dashboard: http://127.0.0.1:5050/dashboard")
    print("Admin: http://127.0.0.1:5050/admin/dashboard")
    print("=" * 60)
    print("Server läuft... Drücken Sie Ctrl+C zum Beenden")
    print("=" * 60)
    
    # Einfacher Flask-Server ohne WebSocket
    app.run(debug=True, host='127.0.0.1', port=5050, use_reloader=False)








