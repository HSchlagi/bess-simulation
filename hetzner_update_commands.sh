#!/bin/bash

# BESS-Simulation Hetzner Update Commands
# Führen Sie diese Befehle auf dem Hetzner-Server aus

echo "🚀 BESS-Simulation Hetzner Update"
echo "=================================="

# 1. Service stoppen
echo "⏹️  Stoppe BESS-Service..."
sudo systemctl stop bess

# 2. Backup der aktuellen Installation
echo "💾 Erstelle Backup der aktuellen Installation..."
sudo cp -r /opt/bess-simulation /opt/bess-simulation_backup_$(date +%Y%m%d_%H%M%S)

# 3. Git Pull - Neueste Änderungen von GitHub
echo "📥 Lade neueste Änderungen von GitHub..."
cd /opt/bess-simulation
sudo git pull origin main

# 4. Datenbank aktualisieren (falls neue Transfer-Datei vorhanden)
echo "🗄️  Prüfe Datenbank-Update..."
if [ -f "instance/bess_hetzner_transfer_20250918_210338.db" ]; then
    echo "✅ Aktualisiere Datenbank mit neuer Transfer-Datei..."
    sudo cp instance/bess_hetzner_transfer_20250918_210338.db instance/bess.db
    sudo chown www-data:www-data instance/bess.db
    sudo chmod 644 instance/bess.db
else
    echo "ℹ️  Keine neue Datenbank-Transfer-Datei gefunden, behalte aktuelle DB"
fi

# 5. Abhängigkeiten aktualisieren
echo "📦 Aktualisiere Python-Abhängigkeiten..."
sudo -H pip3 install -r requirements.txt

# 6. Berechtigungen setzen
echo "🔐 Setze Berechtigungen..."
sudo chown -R www-data:www-data /opt/bess-simulation
sudo chmod -R 755 /opt/bess-simulation
sudo chmod 644 /opt/bess-simulation/instance/bess.db

# 7. Service starten
echo "▶️  Starte BESS-Service..."
sudo systemctl start bess

# 8. Status prüfen
echo "✅ Prüfe Service-Status..."
sudo systemctl status bess --no-pager

echo ""
echo "🎉 Update erfolgreich abgeschlossen!"
echo "🌐 BESS-Simulation ist verfügbar unter: https://bess.instanet.at"
echo ""
echo "📋 Nächste Schritte:"
echo "   - Testen Sie die Anwendung im Browser"
echo "   - Prüfen Sie die Logs: sudo journalctl -u bess -f"

























