# 🚀 BESS Simulation - Installation auf bestehendem Hetzner Server

## **Aktuelle Situation:**
- **Server:** 46.62.157.171 (Hetzner)
- **Bestehende App:** Flask-Tailwind in `/root/Flask-Tailwind`
- **Neue App:** BESS Simulation

## **1. Server verbinden**
```bash
ssh root@46.62.157.171
```

## **2. Bestehende App sichern**
```bash
# Backup der bestehenden App erstellen
cd /root
cp -r Flask-Tailwind Flask-Tailwind_backup_$(date +%Y%m%d)
echo "✅ Backup erstellt: Flask-Tailwind_backup_$(date +%Y%m%d)"
```

## **3. System-Voraussetzungen prüfen**
```bash
# Python-Version prüfen
python3 --version

# Falls Python 3.11 nicht vorhanden:
add-apt-repository ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3.11-dev build-essential

# Nginx prüfen (sollte bereits installiert sein)
nginx -v
```

## **4. BESS Simulation installieren**
```bash
# In separates Verzeichnis installieren
cd /var/www
git clone https://github.com/HSchlagi/bess-simulation.git
cd bess-simulation
chown -R www-data:www-data /var/www/bess-simulation

# Python-Umgebung erstellen
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Datenbank initialisieren
python init_db.py
```

## **5. Gunicorn Service für BESS Simulation**
```bash
# Gunicorn installieren
pip install gunicorn

# Service-Datei erstellen
cat > /etc/systemd/system/bess-simulation.service << EOF
[Unit]
Description=BESS Simulation Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/bess-simulation
Environment="PATH=/var/www/bess-simulation/venv/bin"
ExecStart=/var/www/bess-simulation/venv/bin/gunicorn --workers 3 --bind unix:bess-simulation.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
EOF

# Service starten
systemctl daemon-reload
systemctl start bess-simulation
systemctl enable bess-simulation
```

## **6. Nginx-Konfiguration anpassen**
```bash
# Bestehende Nginx-Konfiguration sichern
cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default_backup

# Neue Konfiguration für beide Apps
cat > /etc/nginx/sites-available/both-apps << EOF
server {
    listen 80;
    server_name _;

    # BESS Simulation (Hauptanwendung)
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/bess-simulation/bess-simulation.sock;
    }

    # Flask-Tailwind (unter /flask-tailwind)
    location /flask-tailwind {
        include proxy_params;
        proxy_pass http://unix:/root/Flask-Tailwind/app.sock;
        proxy_set_header X-Script-Name /flask-tailwind;
    }

    # Statische Dateien
    location /static {
        alias /var/www/bess-simulation/static;
    }

    location /instance {
        alias /var/www/bess-simulation/instance;
    }
}
EOF

# Konfiguration aktivieren
ln -sf /etc/nginx/sites-available/both-apps /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

## **7. Services testen**
```bash
# Status prüfen
systemctl status bess-simulation
systemctl status nginx

# Anwendungen testen
curl http://localhost
curl http://localhost/flask-tailwind
```

## **8. URLs nach Installation:**
- **BESS Simulation:** `http://46.62.157.171`
- **Flask-Tailwind:** `http://46.62.157.171/flask-tailwind`

## **9. Backup-Strategie**
```bash
# Automatisches Backup-Skript
cat > /var/www/bess-simulation/backup_both.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups"

# BESS Simulation Backup
cp /var/www/bess-simulation/instance/bess.db $BACKUP_DIR/bess_$DATE.db

# Flask-Tailwind Backup
cp /root/Flask-Tailwind/leitungsberechnung.sqlite $BACKUP_DIR/flask-tailwind_$DATE.db

# Code-Backups
tar -czf $BACKUP_DIR/bess-simulation_$DATE.tar.gz /var/www/bess-simulation
tar -czf $BACKUP_DIR/flask-tailwind_$DATE.tar.gz /root/Flask-Tailwind

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
EOF

chmod +x /var/www/bess-simulation/backup_both.sh

# Cron-Job für tägliches Backup
echo "0 2 * * * /var/www/bess-simulation/backup_both.sh" | crontab -
```

## **10. Troubleshooting**

### **Bestehende Flask-Tailwind App stoppen:**
```bash
# Falls die bestehende App läuft, stoppen
pkill -f "python.*Flask-Tailwind"
```

### **Ports prüfen:**
```bash
netstat -tlnp | grep :80
netstat -tlnp | grep :5000
```

### **Logs prüfen:**
```bash
journalctl -u bess-simulation -f
tail -f /var/log/nginx/error.log
```

## **11. Rollback (falls nötig)**
```bash
# BESS Simulation entfernen
systemctl stop bess-simulation
systemctl disable bess-simulation
rm /etc/systemd/system/bess-simulation.service

# Nginx zurücksetzen
cp /etc/nginx/sites-available/default_backup /etc/nginx/sites-available/default
systemctl reload nginx

# Flask-Tailwind wiederherstellen
# (Backup verwenden falls nötig)
```

## **✅ Vorteile dieser Lösung:**
- ✅ **Beide Apps laufen parallel**
- ✅ **Keine Konflikte**
- ✅ **Einfacher Rollback möglich**
- ✅ **Backup beider Apps**
- ✅ **Klare URL-Struktur** 