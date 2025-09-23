#!/usr/bin/env python3
"""
BESS-Simulation - Docker-optimierte Version
Optimiert für Container-Umgebungen mit Redis-Caching
"""

import os
from app import create_app

def main():
    """Hauptfunktion für Docker-Container"""
    
    # Docker-spezifische Konfiguration
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5050))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    
    # App erstellen
    app = create_app()
    
    print("🐳 BESS-Simulation Docker Container wird gestartet...")
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {debug}")
    print("=" * 50)
    
    # Server starten
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

if __name__ == '__main__':
    main()
