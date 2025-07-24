# 🚀 BESS Simulation - Installation als Subdomain

## **Aktuelle Infrastruktur:**
- **Hauptdomain:** `instanet.at`
- **Bestehende App:** `https://leitungsberechnung.instanet.at/` (Leitungsberechnung)
- **Neue App:** `https://bess.instanet.at/` (BESS Simulation)

## **1. DNS-Konfiguration (bei Domain-Provider)**
```bash
# Neue A-Record für BESS Subdomain hinzufügen:
# Name: bess
# Type: A
# Value: 46.62.157.171 (Hetzner Server IP)
# TTL: 300
```

## **2. Server verbinden**
```bash
ssh root@46.62.157.171
```

## **3. BESS Simulation installieren**
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

## **4. Gunicorn Service für BESS Simulation**
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
ExecStart=/var/www/bess-simulation/venv/bin/gunicorn --workers 3 --bind unix:/var/www/bess-simulation/bess-simulation.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
EOF

# Service starten
systemctl daemon-reload
systemctl start bess-simulation
systemctl enable bess-simulation
```

## **5. Nginx-Konfiguration für Subdomain**
```bash
# Neue Nginx-Konfiguration für BESS Subdomain
cat > /etc/nginx/sites-available/bess.instanet.at << EOF
server {
    listen 80;
    server_name bess.instanet.at;

    # Weiterleitung auf HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bess.instanet.at;

    # SSL-Zertifikat (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/bess.instanet.at/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bess.instanet.at/privkey.pem;

    # SSL-Konfiguration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Sicherheits-Header
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # BESS Simulation Application
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/bess-simulation/bess-simulation.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Statische Dateien
    location /static {
        alias /var/www/bess-simulation/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Datenbank-Dateien (geschützt)
    location /instance {
        deny all;
        return 404;
    }

    # Gzip-Kompression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript;
}
EOF

# Konfiguration aktivieren
ln -sf /etc/nginx/sites-available/bess.instanet.at /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## **6. SSL-Zertifikat mit Let's Encrypt**
```bash
# Certbot installieren (falls nicht vorhanden)
apt install -y certbot python3-certbot-nginx

# SSL-Zertifikat für BESS Subdomain erstellen
certbot --nginx -d bess.instanet.at --non-interactive --agree-tos --email your-email@instanet.at

# Automatische Erneuerung testen
certbot renew --dry-run
```

## **7. Firewall-Konfiguration**
```bash
# UFW Firewall konfigurieren
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw --force enable

# Status prüfen
ufw status
```

## **8. Monitoring und Logs**
```bash
# Log-Rotation für BESS Simulation
cat > /etc/logrotate.d/bess-simulation << EOF
/var/www/bess-simulation/*.log {
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
EOF

# Log-Verzeichnis erstellen
mkdir -p /var/log/bess-simulation
chown www-data:www-data /var/log/bess-simulation
```

## **9. Backup-Strategie**
```bash
# Automatisches Backup-Skript für beide Apps
cat > /var/www/bess-simulation/backup_all_apps.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups"

# Backup-Verzeichnis erstellen
mkdir -p $BACKUP_DIR

# BESS Simulation Backup
if [ -f "/var/www/bess-simulation/instance/bess.db" ]; then
    cp /var/www/bess-simulation/instance/bess.db $BACKUP_DIR/bess_$DATE.db
    echo "✅ BESS Simulation DB backed up"
fi

# Leitungsberechnung Backup (falls vorhanden)
if [ -f "/root/Flask-Tailwind/leitungsberechnung.sqlite" ]; then
    cp /root/Flask-Tailwind/leitungsberechnung.sqlite $BACKUP_DIR/leitungsberechnung_$DATE.db
    echo "✅ Leitungsberechnung DB backed up"
fi

# Code-Backups
tar -czf $BACKUP_DIR/bess-simulation_$DATE.tar.gz /var/www/bess-simulation
tar -czf $BACKUP_DIR/leitungsberechnung_$DATE.tar.gz /root/Flask-Tailwind

# Nginx-Konfigurationen
tar -czf $BACKUP_DIR/nginx-configs_$DATE.tar.gz /etc/nginx/sites-available /etc/nginx/sites-enabled

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "✅ Backup completed: $DATE"
EOF

chmod +x /var/www/bess-simulation/backup_all_apps.sh

# Cron-Job für tägliches Backup
echo "0 2 * * * /var/www/bess-simulation/backup_all_apps.sh" | crontab -
```

## **10. Services testen**
```bash
# Status aller Services prüfen
systemctl status bess-simulation
systemctl status nginx
systemctl status certbot.timer

# Anwendungen testen
curl -I https://bess.instanet.at
curl -I https://leitungsberechnung.instanet.at
```

## **11. URLs nach Installation:**
- **BESS Simulation:** `https://bess.instanet.at`
- **Leitungsberechnung:** `https://leitungsberechnung.instanet.at`

## **12. Troubleshooting**

### **SSL-Zertifikat erneuern:**
```bash
certbot renew
systemctl reload nginx
```

### **Logs prüfen:**
```bash
# BESS Simulation Logs
journalctl -u bess-simulation -f

# Nginx Logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# SSL-Zertifikat Status
certbot certificates
```

### **Service neu starten:**
```bash
systemctl restart bess-simulation
systemctl restart nginx
```

## **13. Rollback (falls nötig)**
```bash
# BESS Simulation entfernen
systemctl stop bess-simulation
systemctl disable bess-simulation
rm /etc/systemd/system/bess-simulation.service

# Nginx-Konfiguration entfernen
rm /etc/nginx/sites-enabled/bess.instanet.at
systemctl reload nginx

# SSL-Zertifikat entfernen
certbot delete --cert-name bess.instanet.at
```

## **✅ Vorteile dieser Lösung:**
- ✅ **Separate Subdomains** für klare Trennung
- ✅ **SSL-Zertifikate** für beide Anwendungen
- ✅ **Keine Konflikte** zwischen den Apps
- ✅ **Professionelle URL-Struktur**
- ✅ **Einfache Wartung** und Updates
- ✅ **Automatische Backups** beider Apps
- ✅ **Monitoring** und Logging 