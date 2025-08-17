#!/bin/bash
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
sudo mkdir -p /opt/bess-simulation
sudo chown -R $USER:$USER /opt/bess-simulation

# 4. Projekt klonen/kopieren
echo "📋 Projekt kopieren..."
# git clone https://github.com/HSchlagi/bess-simulation.git /opt/bess-simulation
# ODER: Dateien manuell kopieren

# 5. Virtual Environment erstellen
echo "🔧 Virtual Environment..."
cd /opt/bess-simulation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_deployment.txt

# 6. Datenbank initialisieren
echo "🗄️ Datenbank Setup..."
python init_db.py

# 7. Berechtigungen setzen
echo "🔐 Berechtigungen..."
sudo chown -R www-data:www-data /opt/bess-simulation
sudo chmod -R 755 /opt/bess-simulation

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
