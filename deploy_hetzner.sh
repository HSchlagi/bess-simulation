#!/bin/bash
# Hetzner BESS-Simulation Deployment Script
# Generiert am: 2025-09-09 21:46:12

echo "🚀 Starte BESS-Simulation Deployment auf Hetzner..."

# Server stoppen
echo "⏹️ Stoppe BESS-Service..."
sudo systemctl stop bess

# Git Pull
echo "📥 Lade neueste Version..."
cd /opt/bess-simulation
git pull origin main

# Datenbank-Backup erstellen
echo "💾 Erstelle Datenbank-Backup..."
sudo cp instance/bess.db instance/bess.db.backup.$(date +%Y%m%d_%H%M%S)

# Datenbank wiederherstellen (falls Backup vorhanden)
if [ -f "backups\bess_db_hetzner_prep_2025-09-09_21-46-04.sql.gz" ]; then
    echo "📦 Stelle Datenbank aus Backup wieder her..."
    gunzip -c backups\bess_db_hetzner_prep_2025-09-09_21-46-04.sql.gz | sqlite3 instance/bess.db
fi

# Abhängigkeiten installieren
echo "📦 Installiere Abhängigkeiten..."
pip3 install -r requirements.txt

# Berechtigungen setzen
echo "🔐 Setze Berechtigungen..."
sudo chown -R www-data:www-data /opt/bess-simulation
sudo chmod -R 755 /opt/bess-simulation

# Service starten
echo "▶️ Starte BESS-Service..."
sudo systemctl start bess
sudo systemctl enable bess

# Status prüfen
echo "✅ Prüfe Service-Status..."
sudo systemctl status bess --no-pager

echo "🎉 BESS-Simulation Deployment abgeschlossen!"
echo "🌐 Verfügbar unter: https://bess.instanet.at"
