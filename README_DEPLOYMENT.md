# 🚀 BESS Simulation - Quick Deployment Guide

## **Schnellstart für Hetzner Server**

### **1. Server erstellen**
- **Hetzner Cloud Console** → **Add Server**
- **Image:** Ubuntu 22.04 LTS
- **Type:** CX21 (3 vCPU, 4GB RAM)
- **Location:** Frankfurt (FSN1)
- **SSH Key:** Deinen öffentlichen SSH-Key hochladen

### **2. Server verbinden**
```bash
ssh root@YOUR_SERVER_IP
```

### **3. Automatisches Setup**
```bash
# System vorbereiten
apt update && apt upgrade -y
apt install -y curl wget git unzip software-properties-common

# Python 3.11 installieren
add-apt-repository ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3.11-dev build-essential

# Nginx installieren
apt install -y nginx
systemctl enable nginx
systemctl start nginx

# Projekt klonen
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

### **4. Gunicorn Service**
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

### **5. Nginx konfigurieren**
```bash
# Nginx-Konfiguration erstellen
cat > /etc/nginx/sites-available/bess-simulation << EOF
server {
    listen 80;
    server_name _;

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
EOF

# Site aktivieren
ln -s /etc/nginx/sites-available/bess-simulation /etc/nginx/sites-enabled
rm /etc/nginx/sites-enabled/default  # Default site entfernen
nginx -t
systemctl reload nginx
```

### **6. Firewall aktivieren**
```bash
ufw allow ssh
ufw allow 'Nginx Full'
ufw enable
```

### **7. Testen**
```bash
# Status prüfen
systemctl status bess-simulation
systemctl status nginx

# Anwendung testen
curl http://localhost
```

## **🎉 Fertig!**

Die BESS Simulation läuft jetzt unter:
**http://YOUR_SERVER_IP**

## **📋 Nützliche Befehle**

### **Logs anzeigen:**
```bash
journalctl -u bess-simulation -f
tail -f /var/log/nginx/access.log
```

### **Service neu starten:**
```bash
systemctl restart bess-simulation
systemctl reload nginx
```

### **Updates deployen:**
```bash
cd /var/www/bess-simulation
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart bess-simulation
```

## **🔧 Troubleshooting**

### **Permission Denied:**
```bash
chown -R www-data:www-data /var/www/bess-simulation
chmod -R 755 /var/www/bess-simulation
```

### **Service startet nicht:**
```bash
journalctl -u bess-simulation --no-pager -n 50
```

### **Nginx Fehler:**
```bash
nginx -t
tail -f /var/log/nginx/error.log
```

## **📞 Support**

Bei Problemen:
1. Logs prüfen: `journalctl -u bess-simulation -f`
2. Service-Status: `systemctl status bess-simulation`
3. Nginx-Status: `systemctl status nginx`
4. Firewall: `ufw status` 