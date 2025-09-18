#!/bin/bash

# BESS-Simulation Hetzner Update Script
# Datum: $(date +%Y-%m-%d)

echo "🚀 BESS-Simulation Hetzner Update"
echo "=================================="

# Service stoppen
echo "⏹️  Stoppe BESS-Service..."
sudo systemctl stop bess

# Backup der aktuellen Installation
echo "💾 Erstelle Backup der aktuellen Installation..."
sudo cp -r /opt/bess-simulation /opt/bess-simulation_backup_$(date +%Y%m%d_%H%M%S)

# Git Pull
echo "📥 Lade neueste Änderungen von GitHub..."
cd /opt/bess-simulation
sudo git pull origin main

# Datenbank aktualisieren
echo "🗄️  Aktualisiere Datenbank..."
sudo cp instance/bess_hetzner_transfer_20250918_210338.db instance/bess.db
sudo chown www-data:www-data instance/bess.db
sudo chmod 644 instance/bess.db

# Abhängigkeiten aktualisieren
echo "📦 Aktualisiere Python-Abhängigkeiten..."
sudo -H pip3 install -r requirements.txt

# Berechtigungen setzen
echo "🔐 Setze Berechtigungen..."
sudo chown -R www-data:www-data /opt/bess-simulation
sudo chmod -R 755 /opt/bess-simulation
sudo chmod 644 /opt/bess-simulation/instance/bess.db

# Service starten
echo "▶️  Starte BESS-Service..."
sudo systemctl start bess

# Status prüfen
echo "✅ Prüfe Service-Status..."
sudo systemctl status bess --no-pager

echo ""
echo "🎉 Update erfolgreich abgeschlossen!"
echo "🌐 BESS-Simulation ist verfügbar unter: https://bess.instanet.at"