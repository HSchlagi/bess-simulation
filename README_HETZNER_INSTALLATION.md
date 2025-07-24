# 🚀 BESS Simulation - Hetzner Installation

## **Voraussetzungen**
- ✅ Hetzner Server (46.62.157.171)
- ✅ DNS-Subdomain `bess.instanet.at` konfiguriert
- ✅ SSH-Zugang zum Server
- ✅ BESS Simulation Code installiert (`/var/www/bess-simulation`)

## **📋 Installation Schritt-für-Schritt**

### **1. Dateien auf Server kopieren**

Kopiere diese Dateien auf den Hetzner Server:
```bash
# Auf deinem lokalen Rechner
scp nginx_bess_config.conf root@46.62.157.171:/root/
scp bess-simulation.service root@46.62.157.171:/root/
scp install_bess_on_hetzner.sh root@46.62.157.171:/root/
```

### **2. Installation ausführen**

```bash
# Am Hetzner Server
ssh root@46.62.157.171

# Installationsskript ausführbar machen
chmod +x install_bess_on_hetzner.sh

# Installation starten
./install_bess_on_hetzner.sh
```

### **3. Manuelle Schritte (falls automatisch fehlschlägt)**

#### **A. Nginx-Konfiguration**
```bash
# Nginx-Konfiguration kopieren
cp nginx_bess_config.conf /etc/nginx/sites-available/bess.instanet.at
ln -sf /etc/nginx/sites-available/bess.instanet.at /etc/nginx/sites-enabled/

# Konfiguration testen
nginx -t

# Nginx neu laden
systemctl reload nginx
```

#### **B. Systemd Service**
```bash
# Service-Datei kopieren
cp bess-simulation.service /etc/systemd/system/

# Service aktivieren
systemctl daemon-reload
systemctl enable bess-simulation
systemctl start bess-simulation
```

#### **C. SSL-Zertifikat**
```bash
# Certbot installieren (falls nicht vorhanden)
apt install certbot python3-certbot-nginx

# SSL-Zertifikat erstellen
certbot --nginx -d bess.instanet.at --non-interactive --agree-tos --email admin@instanet.at
```

#### **D. Verzeichnisse und Berechtigungen**
```bash
# Verzeichnisse erstellen
mkdir -p /var/log/bess-simulation
mkdir -p /var/www/bess-simulation/instance/exports

# Berechtigungen setzen
chown -R www-data:www-data /var/log/bess-simulation
chown -R www-data:www-data /var/www/bess-simulation
```

## **🔧 Troubleshooting**

### **Service-Status prüfen**
```bash
# BESS Simulation Service
systemctl status bess-simulation

# Nginx Service
systemctl status nginx

# Ports prüfen
netstat -tlnp | grep :8000
netstat -tlnp | grep :80
netstat -tlnp | grep :443
```

### **Logs anzeigen**
```bash
# BESS Simulation Logs
journalctl -u bess-simulation -f

# Nginx Logs
tail -f /var/log/nginx/bess.instanet.at.error.log
tail -f /var/log/nginx/bess.instanet.at.access.log

# App-spezifische Logs
tail -f /var/log/bess-simulation/error.log
```

### **Häufige Probleme**

#### **Problem: Service startet nicht**
```bash
# Logs prüfen
journalctl -u bess-simulation -n 50

# Manueller Test
cd /var/www/bess-simulation
source venv/bin/activate
python wsgi.py
```

#### **Problem: Nginx-Fehler**
```bash
# Konfiguration testen
nginx -t

# Nginx-Logs prüfen
tail -f /var/log/nginx/error.log
```

#### **Problem: SSL-Zertifikat**
```bash
# Certbot-Status prüfen
certbot certificates

# Zertifikat erneuern
certbot renew --dry-run
```

## **🌐 Finale URLs**

Nach erfolgreicher Installation:
- **BESS Simulation:** `https://bess.instanet.at`
- **Leitungsberechnung:** `https://leitungsberechnung.instanet.at`

## **📊 Monitoring**

### **Service-Monitoring**
```bash
# Automatischer Neustart bei Fehlern
systemctl enable bess-simulation

# Status-Überwachung
watch systemctl status bess-simulation
```

### **Log-Rotation**
```bash
# Log-Rotation konfigurieren (optional)
cat > /etc/logrotate.d/bess-simulation << EOF
/var/log/bess-simulation/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
EOF
```

## **🔄 Updates**

### **Code-Update**
```bash
cd /var/www/bess-simulation
git pull origin main
systemctl restart bess-simulation
```

### **Dependency-Update**
```bash
cd /var/www/bess-simulation
source venv/bin/activate
pip install -r requirements.txt
systemctl restart bess-simulation
```

## **💾 Backup**

### **Datenbank-Backup**
```bash
# Automatisches Backup-Skript
cat > /root/backup_bess.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/bess-simulation"
mkdir -p $BACKUP_DIR

# Datenbank-Backup
cp /var/www/bess-simulation/instance/bess.db $BACKUP_DIR/bess_$DATE.db

# SQL-Dump
sqlite3 /var/www/bess-simulation/instance/bess.db .dump > $BACKUP_DIR/bess_$DATE.sql

echo "Backup erstellt: $BACKUP_DIR/bess_$DATE.*"
EOF

chmod +x /root/backup_bess.sh

# Cron-Job für tägliches Backup
echo "0 2 * * * /root/backup_bess.sh" | crontab -
```

## **🎯 Erfolgsindikatoren**

✅ **Service läuft:** `systemctl is-active bess-simulation`  
✅ **Nginx läuft:** `systemctl is-active nginx`  
✅ **SSL funktioniert:** `curl -I https://bess.instanet.at`  
✅ **App erreichbar:** Browser öffnet `https://bess.instanet.at`  
✅ **API funktioniert:** `curl https://bess.instanet.at/api/projects`  

## **📞 Support**

Bei Problemen:
1. Logs prüfen (siehe Troubleshooting)
2. Service-Status kontrollieren
3. Manuelle Tests durchführen
4. Bei DNS-Problemen: `nslookup bess.instanet.at`

---

**🎉 Installation erfolgreich!**  
Die BESS Simulation ist jetzt unter `https://bess.instanet.at` verfügbar. 