#!/usr/bin/env python3
"""
BESS-Simulation Server
Hauptanwendung für die Battery Energy Storage System Simulation
"""

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("🚀 BESS-Simulation Server wird gestartet...")
    print("📊 Dashboard: http://127.0.0.1:5000/dashboard")
    print("🔧 Admin-Panel: http://127.0.0.1:5000/admin/dashboard")
    print("📤 Export-Zentrum: http://127.0.0.1:5000/export/")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5000)
