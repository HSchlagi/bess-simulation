#!/usr/bin/env python3
"""
Deployment-Skript für Hetzner Server
Bereitet die Datenbank und alle Dateien für das Deployment vor
"""

import os
import shutil
import sqlite3
from datetime import datetime
import subprocess

def create_deployment_package():
    """Erstellt ein Deployment-Paket für Hetzner"""
    print("🚀 Erstelle Deployment-Paket für Hetzner...")
    
    # 1. Aktuelle Datenbank sichern
    print("📊 Sichere aktuelle Datenbank...")
    backup_file = f"instance/bess_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2("instance/bess.db", backup_file)
    print(f"✅ Datenbank gesichert: {backup_file}")
    
    # 2. Datenbank optimieren (VACUUM)
    print("🔧 Optimiere Datenbank...")
    try:
        conn = sqlite3.connect("instance/bess.db")
        conn.execute("VACUUM")
        conn.execute("ANALYZE")
        conn.close()
        print("✅ Datenbank optimiert")
    except Exception as e:
        print(f"⚠️ Datenbank-Optimierung fehlgeschlagen: {e}")
    
    # 3. Deployment-Dateien erstellen
    print("📦 Erstelle Deployment-Dateien...")
    
    # .gitignore für Deployment
    with open(".gitignore_deployment", "w", encoding='utf-8') as f:
        f.write("""# Deployment-spezifische Ignore-Datei
instance/
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git/
.mypy_cache/
.pytest_cache/
.hypothesis/
""")
    
    # Deployment-Requirements
    with open("requirements_deployment.txt", "w", encoding='utf-8') as f:
        f.write("""Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Flask-WTF==1.1.1
WTForms==3.0.1
Werkzeug==2.3.7
SQLAlchemy==2.0.21
python-dotenv==1.0.0
requests==2.31.0
pandas==2.0.3
numpy==1.24.3
matplotlib==3.7.2
plotly==5.15.0
supabase==1.0.3
gunicorn==21.2.0
""")
    
    # Deployment-Konfiguration
    with open("config_deployment.py", "w", encoding='utf-8') as f:
        f.write("""# Deployment-Konfiguration für Hetzner
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/bess.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Supabase-Konfiguration (falls benötigt)
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Debug-Modus deaktivieren für Produktion
    DEBUG = False
    
    # Logging-Konfiguration
    LOG_LEVEL = 'INFO'
""")
    
    # WSGI-Datei für Gunicorn
    with open("wsgi_deployment.py", "w", encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
WSGI-Entry-Point für Gunicorn auf Hetzner
\"\"\"

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
""")
    
    # Systemd Service-Datei
    with open("bess-simulation.service", "w", encoding='utf-8') as f:
        f.write("""[Unit]
Description=BESS Simulation Web Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/bess-simulation
Environment="PATH=/var/www/bess-simulation/venv/bin"
ExecStart=/var/www/bess-simulation/venv/bin/gunicorn --workers 3 --bind unix:bess-simulation.sock -m 007 wsgi_deployment:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
""")
    
    # Nginx-Konfiguration
    with open("nginx_bess_deployment.conf", "w", encoding='utf-8') as f:
        f.write("""server {
    listen 80;
    server_name your-domain.com;  # Ersetzen Sie durch Ihre Domain
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/bess-simulation/bess-simulation.sock;
    }
    
    location /static {
        alias /var/www/bess-simulation/app/static;
    }
    
    # Gzip-Kompression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
}
""")
    
    # Deployment-Skript
    with open("deploy_hetzner.sh", "w", encoding='utf-8') as f:
        f.write("""#!/bin/bash
# Deployment-Skript für Hetzner Server

echo "🚀 Starte BESS-Simulation Deployment auf Hetzner..."

# 1. System-Updates
echo "📦 System-Updates..."
sudo apt update && sudo apt upgrade -y

# 2. Python und Dependencies installieren
echo "🐍 Python Setup..."
sudo apt install -y python3 python3-pip python3-venv nginx

# 3. Verzeichnis erstellen
echo "📁 Verzeichnis erstellen..."
sudo mkdir -p /var/www/bess-simulation
sudo chown -R $USER:$USER /var/www/bess-simulation

# 4. Projekt klonen/kopieren
echo "📋 Projekt kopieren..."
# git clone https://github.com/HSchlagi/bess-simulation.git /var/www/bess-simulation
# ODER: Dateien manuell kopieren

# 5. Virtual Environment erstellen
echo "🔧 Virtual Environment..."
cd /var/www/bess-simulation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_deployment.txt

# 6. Datenbank initialisieren
echo "🗄️ Datenbank Setup..."
python init_db.py

# 7. Berechtigungen setzen
echo "🔐 Berechtigungen..."
sudo chown -R www-data:www-data /var/www/bess-simulation
sudo chmod -R 755 /var/www/bess-simulation

# 8. Systemd Service einrichten
echo "⚙️ Systemd Service..."
sudo cp bess-simulation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bess-simulation
sudo systemctl start bess-simulation

# 9. Nginx konfigurieren
echo "🌐 Nginx Setup..."
sudo cp nginx_bess_deployment.conf /etc/nginx/sites-available/bess-simulation
sudo ln -s /etc/nginx/sites-available/bess-simulation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 10. Firewall konfigurieren
echo "🔥 Firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh

echo "✅ Deployment abgeschlossen!"
echo "🌐 BESS-Simulation ist verfügbar unter: http://your-domain.com"
echo "📊 Status prüfen: sudo systemctl status bess-simulation"
""")
    
    print("✅ Deployment-Dateien erstellt:")
    print("  📄 .gitignore_deployment")
    print("  📄 requirements_deployment.txt")
    print("  📄 config_deployment.py")
    print("  📄 wsgi_deployment.py")
    print("  📄 bess-simulation.service")
    print("  📄 nginx_bess_deployment.conf")
    print("  📄 deploy_hetzner.sh")
    
    # 4. Deployment-Checkliste erstellen
    with open("DEPLOYMENT_CHECKLIST.md", "w", encoding='utf-8') as f:
        f.write("""# 🚀 Hetzner Deployment Checkliste

## Vor dem Deployment

### 1. Lokale Vorbereitung ✅
- [x] Datenbank gesichert
- [x] Datenbank optimiert (VACUUM)
- [x] Deployment-Dateien erstellt
- [x] Git Repository aktualisiert

### 2. Hetzner Server Vorbereitung
- [ ] Server-Zugang einrichten
- [ ] Domain/Subdomain konfigurieren
- [ ] SSL-Zertifikat vorbereiten (Let's Encrypt)

### 3. Umgebungsvariablen
```bash
# Auf Hetzner Server setzen:
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="sqlite:///instance/bess.db"
export SUPABASE_URL="your-supabase-url"  # Falls verwendet
export SUPABASE_KEY="your-supabase-key"  # Falls verwendet
```

## Deployment-Schritte

### 1. Projekt übertragen
```bash
# Option A: Git Clone
git clone https://github.com/HSchlagi/bess-simulation.git /var/www/bess-simulation

# Option B: Dateien manuell kopieren
scp -r ./* user@hetzner-server:/var/www/bess-simulation/
```

### 2. Deployment ausführen
```bash
cd /var/www/bess-simulation
chmod +x deploy_hetzner.sh
./deploy_hetzner.sh
```

### 3. Datenbank migrieren
```bash
# Use Cases zu projektabhängig migrieren
python migrate_use_cases_to_project_based.py

# Fehlende created_at Werte setzen
python fix_created_at_dates.py
```

### 4. Konfiguration anpassen
- [ ] Domain in nginx_bess_deployment.conf anpassen
- [ ] SSL-Zertifikat einrichten
- [ ] Umgebungsvariablen setzen

## Nach dem Deployment

### 1. Tests durchführen
- [ ] Website erreichbar
- [ ] Login funktioniert
- [ ] Projekte anzeigen
- [ ] Use Case Manager funktioniert
- [ ] Datenbank-Operationen funktionieren

### 2. Monitoring einrichten
- [ ] Logs überwachen: `sudo journalctl -u bess-simulation`
- [ ] Nginx-Logs: `sudo tail -f /var/log/nginx/access.log`
- [ ] Datenbank-Größe überwachen

### 3. Backup-Strategie
- [ ] Automatische Datenbank-Backups einrichten
- [ ] Log-Rotation konfigurieren
- [ ] Monitoring-Alerts einrichten

## Troubleshooting

### Häufige Probleme
1. **Permission Denied**: `sudo chown -R www-data:www-data /var/www/bess-simulation`
2. **Port bereits belegt**: `sudo netstat -tlnp | grep :80`
3. **Datenbank-Fehler**: `python check_database_structure.py`

### Logs prüfen
```bash
sudo systemctl status bess-simulation
sudo journalctl -u bess-simulation -f
sudo tail -f /var/log/nginx/error.log
```

## Sicherheit

### Wichtige Sicherheitsmaßnahmen
- [ ] Firewall konfiguriert
- [ ] SSH-Zugang gesichert
- [ ] Regelmäßige Updates
- [ ] Datenbank-Backups
- [ ] SSL-Zertifikat aktiv

---
**Erstellt:** """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
**Version:** BESS-Simulation v2.0 (Multi-User + Use Case Manager)
""")
    
    print("✅ Deployment-Checkliste erstellt: DEPLOYMENT_CHECKLIST.md")
    
    return True

def main():
    """Hauptfunktion"""
    print("🎯 BESS-Simulation Hetzner Deployment Vorbereitung")
    print("=" * 50)
    
    try:
        create_deployment_package()
        print("\n✅ Deployment-Paket erfolgreich erstellt!")
        print("\n📋 Nächste Schritte:")
        print("1. Alle Dateien auf Hetzner übertragen")
        print("2. DEPLOYMENT_CHECKLIST.md durchgehen")
        print("3. deploy_hetzner.sh ausführen")
        print("4. Datenbank-Migrationen durchführen")
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Deployment-Pakets: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
