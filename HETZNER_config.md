# 🚀 HETZNER Server Konfiguration - BESS Simulation

## 📋 Übersicht
Diese Dokumentation beschreibt die vollständige Konfiguration für die Bereitstellung der BESS Simulation auf einem Hetzner Server.

**Domain:** `bess.instanet.at`  
**Repository:** https://github.com/HSchlagi/bess-simulation

---

## 🖥️ System-Anforderungen

### Hardware
- **RAM:** Mindestens 2GB (4GB empfohlen)
- **CPU:** 2 Cores (4 Cores empfohlen)
- **Speicher:** Mindestens 20GB freier Speicher
- **Netzwerk:** Stabile Internetverbindung

### Software
- **Betriebssystem:** Ubuntu 20.04 LTS oder neuer
- **Python:** 3.10+
- **Nginx:** Neueste stabile Version
- **SQLite:** 3.x (für Datenbank)

---

## 🐍 Python-Umgebung

### Installation
```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Python 3.10+ installieren
sudo apt install python3.10 python3.10-venv python3-pip python3-dev

# Virtual Environment erstellen
sudo mkdir -p /var/www/bess-simulation
sudo python3.10 -m venv /var/www/bess-simulation/venv
```

### Python-Pakete (requirements.txt)
```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
SQLAlchemy==2.0.21
Werkzeug==2.3.7
Jinja2==3.1.2
MarkupSafe==2.1.3
itsdangerous==2.1.2
click==8.1.7
blinker==1.6.3
greenlet==3.0.0
typing_extensions==4.7.1

# PDF Generation
reportlab==4.0.4
Pillow==10.0.1

# Excel Generation
openpyxl==3.1.2

# Data Processing
pandas==2.0.3
numpy==1.24.3

# HTTP Requests
requests==2.31.0

# Date/Time handling
python-dateutil==2.8.2

# Environment variables
python-dotenv==1.0.0

# Production server
gunicorn==21.2.0
```

---

## 🌐 Web-Server (Nginx)

### Installation
```bash
# Nginx installieren
sudo apt install nginx

# Nginx-Konfiguration installieren
sudo cp nginx_bess_config.conf /etc/nginx/sites-available/bess.instanet.at
sudo ln -sf /etc/nginx/sites-available/bess.instanet.at /etc/nginx/sites-enabled/

# Standard-Site deaktivieren (falls vorhanden)
sudo rm -f /etc/nginx/sites-enabled/default
```

### Nginx-Konfiguration
```nginx
# Nginx-Konfiguration für BESS Simulation (bess.instanet.at)
server {
    listen 80;
    server_name bess.instanet.at;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 80;
    server_name bess.instanet.at;
    
    # SSL-Konfiguration (wird später von Certbot automatisch eingefügt)
    # listen 443 ssl http2;
    # ssl_certificate /etc/letsencrypt/live/bess.instanet.at/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/bess.instanet.at/privkey.pem;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Root-Verzeichnis
    root /var/www/bess-simulation;
    
    # Logs
    access_log /var/log/nginx/bess.instanet.at.access.log;
    error_log /var/log/nginx/bess.instanet.at.error.log;
    
    # Gzip-Kompression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript;
    
    # Static Files (CSS, JS, Images)
    location /static/ {
        alias /var/www/bess-simulation/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Proxy zu Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # WebSocket Support (falls benötigt)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # API-Endpunkte
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS Headers für API
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
    }
    
    # Export-Downloads
    location /downloads/ {
        alias /var/www/bess-simulation/instance/exports/;
        internal;
        add_header Content-Disposition "attachment";
    }
}
```

---

## 🔧 Application Server (Gunicorn)

### Konfiguration
- **Port:** 8000
- **Workers:** 3
- **User:** www-data
- **Working Directory:** `/var/www/bess-simulation`

### Systemd Service (bess-simulation.service)
```ini
[Unit]
Description=BESS Simulation Gunicorn Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/bess-simulation
Environment="PATH=/var/www/bess-simulation/venv/bin"
Environment="FLASK_APP=wsgi.py"
Environment="FLASK_ENV=production"
ExecStart=/var/www/bess-simulation/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 --access-logfile /var/log/bess-simulation/access.log --error-logfile /var/log/bess-simulation/error.log --log-level info wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/www/bess-simulation/instance
ReadWritePaths=/var/log/bess-simulation

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

---

## 📁 Verzeichnisstruktur

```
/var/www/bess-simulation/
├── app/                    # Flask-Anwendung
│   ├── __init__.py        # App-Factory
│   ├── routes.py          # Route-Definitionen
│   ├── models.py          # Datenbank-Modelle
│   ├── forms.py           # Formulare
│   └── templates/         # HTML-Templates
│       ├── base.html
│       ├── header.html
│       ├── dashboard.html
│       └── ...
├── instance/              # Datenbank & Exports
│   ├── bess.db           # SQLite-Datenbank
│   └── exports/          # PDF/Excel-Exporte
├── static/               # Statische Dateien
│   ├── css/
│   ├── js/
│   └── images/
├── venv/                 # Python Virtual Environment
├── wsgi.py              # WSGI Entry Point
├── run.py               # Development Server
├── requirements.txt     # Python-Pakete
├── config.py           # Konfiguration
└── init_db.py          # Datenbank-Initialisierung
```

---

## 🔒 SSL-Zertifikat (Let's Encrypt)

### Installation
```bash
# Certbot installieren
sudo apt install certbot python3-certbot-nginx

# SSL-Zertifikat erstellen
sudo certbot --nginx -d bess.instanet.at --non-interactive --agree-tos --email admin@instanet.at

# Auto-Renewal testen
sudo certbot renew --dry-run
```

### Auto-Renewal
```bash
# Cron-Job für Auto-Renewal
sudo crontab -e

# Füge hinzu:
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 🛡️ Firewall-Konfiguration

### UFW Firewall
```bash
# UFW installieren (falls nicht vorhanden)
sudo apt install ufw

# Firewall-Regeln konfigurieren
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw --force enable

# Status prüfen
sudo ufw status verbose
```

---

## 📊 Logging

### Verzeichnisse erstellen
```bash
# Log-Verzeichnisse erstellen
sudo mkdir -p /var/log/bess-simulation
sudo chown -R www-data:www-data /var/log/bess-simulation
```

### Log-Dateien
```
/var/log/bess-simulation/
├── access.log           # Gunicorn Access Logs
└── error.log            # Gunicorn Error Logs

/var/log/nginx/
├── bess.instanet.at.access.log
└── bess.instanet.at.error.log
```

### Log-Rotation
```bash
# Logrotate-Konfiguration
sudo nano /etc/logrotate.d/bess-simulation

# Inhalt:
/var/log/bess-simulation/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload bess-simulation
    endscript
}
```

---

## 🚀 Deployment-Prozess

### 1. Code hochladen
```bash
# Git Repository klonen
sudo git clone https://github.com/HSchlagi/bess-simulation.git /var/www/bess-simulation
sudo chown -R www-data:www-data /var/www/bess-simulation
```

### 2. Dependencies installieren
```bash
# Virtual Environment aktivieren
cd /var/www/bess-simulation
source venv/bin/activate

# Python-Pakete installieren
pip install -r requirements.txt
```

### 3. Datenbank initialisieren
```bash
# Datenbank erstellen
python init_db.py

# Berechtigungen setzen
sudo chown www-data:www-data instance/bess.db
```

### 4. Services starten
```bash
# Systemd Service installieren
sudo cp bess-simulation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bess-simulation
sudo systemctl start bess-simulation

# Nginx neuladen
sudo systemctl reload nginx
```

---

## 🔧 Monitoring & Wartung

### Service-Status prüfen
```bash
# BESS Simulation Service
sudo systemctl status bess-simulation

# Nginx Service
sudo systemctl status nginx

# Gunicorn Prozesse
ps aux | grep gunicorn
```

### Logs anzeigen
```bash
# BESS Simulation Logs
sudo journalctl -u bess-simulation -f

# Nginx Logs
sudo tail -f /var/log/nginx/bess.instanet.at.error.log

# Gunicorn Logs
sudo tail -f /var/log/bess-simulation/error.log
```

### Performance-Monitoring
```bash
# System-Ressourcen
htop
df -h
free -h

# Netzwerk-Verbindungen
netstat -tlnp | grep :8000
netstat -tlnp | grep :80
netstat -tlnp | grep :443
```

---

## 💾 Backup-Strategie

### Automatische Backups
```bash
# Backup-Script erstellen
sudo nano /usr/local/bin/backup_bess.sh

#!/bin/bash
BACKUP_DIR="/var/backups/bess-simulation"
DATE=$(date +%Y%m%d_%H%M%S)

# Verzeichnis erstellen
mkdir -p $BACKUP_DIR

# Datenbank-Backup
sqlite3 /var/www/bess-simulation/instance/bess.db ".backup $BACKUP_DIR/bess_$DATE.db"

# Code-Backup (falls keine Git-Versionierung)
tar -czf $BACKUP_DIR/bess_code_$DATE.tar.gz /var/www/bess-simulation/

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Backup-Cron-Job
```bash
# Tägliches Backup um 2:00 Uhr
sudo crontab -e

# Füge hinzu:
0 2 * * * /usr/local/bin/backup_bess.sh
```

---

## 🛠️ Troubleshooting

### Häufige Probleme

#### 1. Service startet nicht
```bash
# Logs prüfen
sudo journalctl -u bess-simulation -n 50

# Berechtigungen prüfen
ls -la /var/www/bess-simulation/
ls -la /var/log/bess-simulation/
```

#### 2. Nginx-Fehler
```bash
# Nginx-Konfiguration testen
sudo nginx -t

# Nginx-Logs prüfen
sudo tail -f /var/log/nginx/error.log
```

#### 3. SSL-Zertifikat-Probleme
```bash
# Zertifikat-Status prüfen
sudo certbot certificates

# Zertifikat erneuern
sudo certbot renew
```

#### 4. Datenbank-Probleme
```bash
# Datenbank-Integrität prüfen
sqlite3 /var/www/bess-simulation/instance/bess.db "PRAGMA integrity_check;"

# Datenbank-Backup wiederherstellen
sqlite3 /var/www/bess-simulation/instance/bess.db ".restore backup.db"
```

---

## 📞 Support & Wartung

### Nützliche Befehle
```bash
# Service neustarten
sudo systemctl restart bess-simulation

# Nginx neuladen
sudo systemctl reload nginx

# Logs löschen
sudo journalctl --vacuum-time=7d

# System-Updates
sudo apt update && sudo apt upgrade -y
```

### Monitoring-URLs
- **Anwendung:** https://bess.instanet.at
- **Status-Seite:** https://bess.instanet.at/status
- **Health-Check:** https://bess.instanet.at/health

---

## 📝 Changelog

### Version 1.0.0 (Aktuell)
- ✅ Vollständige Hetzner-Server-Konfiguration
- ✅ Nginx + Gunicorn Setup
- ✅ SSL-Zertifikat mit Let's Encrypt
- ✅ Systemd Service-Konfiguration
- ✅ Backup-Strategie
- ✅ Monitoring & Logging
- ✅ Firewall-Konfiguration

---

**Letzte Aktualisierung:** $(date +%Y-%m-%d)  
**Verantwortlich:** BESS Simulation Team  
**Repository:** https://github.com/HSchlagi/bess-simulation 