# 🚀 BESS Simulation - Hetzner Deployment Guide

## **1. Server-Vorbereitung**

### **Hetzner Cloud Server erstellen:**
- **Location:** Frankfurt (FSN1) oder Nürnberg (NBG1)
- **Image:** Ubuntu 22.04 LTS
- **Type:** CX21 (3 vCPU, 4GB RAM) - empfohlen für Produktion
- **Network:** Standard
- **Firewall:** SSH (Port 22), HTTP (Port 80), HTTPS (Port 443)

### **SSH-Zugang einrichten:**
```bash
# SSH-Key generieren (falls noch nicht vorhanden)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Auf Hetzner hochladen und Server erstellen
# Dann verbinden:
ssh root@YOUR_SERVER_IP
```

## **2. Server-Setup**

### **System-Updates:**
```bash
apt update && apt upgrade -y
apt install -y curl wget git unzip software-properties-common
```

### **Python 3.11 installieren:**
```bash
add-apt-repository ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3.11-dev
apt install -y build-essential libssl-dev libffi-dev
```

### **Nginx installieren:**
```bash
apt install -y nginx
systemctl enable nginx
systemctl start nginx
```

### **SQLite installieren:**
```bash
apt install -y sqlite3
```

## **3. Anwendung deployen**

### **Projekt klonen:**
```bash
cd /var/www
git clone https://github.com/HSchlagi/bess-simulation.git
cd bess-simulation
chown -R www-data:www-data /var/www/bess-simulation
```

### **Python-Umgebung erstellen:**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### **Datenbank initialisieren:**
```bash
python init_db.py
```

## **4. Gunicorn konfigurieren**

### **Gunicorn installieren:**
```bash
pip install gunicorn
```

### **Gunicorn Service erstellen:**
```bash
nano /etc/systemd/system/bess-simulation.service
```

**Service-Datei Inhalt:**
```ini
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
```

### **Service starten:**
```bash
systemctl daemon-reload
systemctl start bess-simulation
systemctl enable bess-simulation
```

## **5. Nginx konfigurieren**

### **Nginx-Konfiguration erstellen:**
```bash
nano /etc/nginx/sites-available/bess-simulation
```

**Nginx-Konfiguration:**
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/bess-simulation/bess-simulation.sock;
    }

    location /static {
        alias /var/www/bess-simulation/static;
    }

    location /instance {
        alias /var/www/bess-simulation/instance;
    }
}
```

### **Site aktivieren:**
```bash
ln -s /etc/nginx/sites-available/bess-simulation /etc/nginx/sites-enabled
nginx -t
systemctl reload nginx
```

## **6. SSL/HTTPS einrichten (Optional)**

### **Certbot installieren:**
```bash
apt install -y certbot python3-certbot-nginx
```

### **SSL-Zertifikat erstellen:**
```bash
certbot --nginx -d YOUR_DOMAIN.com
```

## **7. Firewall konfigurieren**

### **UFW aktivieren:**
```bash
ufw allow ssh
ufw allow 'Nginx Full'
ufw enable
```

## **8. Monitoring & Logs**

### **Logs überwachen:**
```bash
# Gunicorn Logs
journalctl -u bess-simulation -f

# Nginx Logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### **Status prüfen:**
```bash
systemctl status bess-simulation
systemctl status nginx
```

## **9. Backup-Strategie**

### **Automatisches Backup-Skript:**
```bash
nano /var/www/bess-simulation/backup.sh
```

**Backup-Skript:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/bess-simulation"
mkdir -p $BACKUP_DIR

# Datenbank-Backup
cp /var/www/bess-simulation/instance/bess.db $BACKUP_DIR/bess_$DATE.db

# Code-Backup
tar -czf $BACKUP_DIR/code_$DATE.tar.gz /var/www/bess-simulation

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### **Cron-Job für automatisches Backup:**
```bash
chmod +x /var/www/bess-simulation/backup.sh
crontab -e
# Täglich um 2:00 Uhr
0 2 * * * /var/www/bess-simulation/backup.sh
```

## **10. Updates & Wartung**

### **Code-Update:**
```bash
cd /var/www/bess-simulation
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart bess-simulation
```

### **System-Updates:**
```bash
apt update && apt upgrade -y
```

## **11. Troubleshooting**

### **Häufige Probleme:**

**1. Permission Denied:**
```bash
chown -R www-data:www-data /var/www/bess-simulation
chmod -R 755 /var/www/bess-simulation
```

**2. Port bereits belegt:**
```bash
netstat -tlnp | grep :80
# Falls nötig, anderen Service stoppen
```

**3. Datenbank-Fehler:**
```bash
# Datenbank-Pfad prüfen
ls -la /var/www/bess-simulation/instance/
# Berechtigungen korrigieren
chown www-data:www-data /var/www/bess-simulation/instance/bess.db
```

## **12. Performance-Optimierung**

### **Gunicorn-Optimierung:**
```bash
# Mehr Workers für bessere Performance
# Workers = (2 x CPU Cores) + 1
# Für CX21 (3 vCPU): 7 Workers
```

### **Nginx-Optimierung:**
```nginx
# In nginx.conf
worker_processes auto;
worker_connections 1024;
```

## **13. Sicherheit**

### **Sicherheitsmaßnahmen:**
- Regelmäßige Updates
- Firewall aktiviert
- SSH-Key-Authentifizierung
- HTTPS erzwingen
- Backup-Strategie

### **Monitoring:**
- Log-Rotation
- Disk-Space-Überwachung
- Service-Status-Monitoring 