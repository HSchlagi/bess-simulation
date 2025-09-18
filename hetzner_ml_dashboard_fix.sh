#!/bin/bash

# Hetzner Update Script für ML-Dashboard Preisprognose Fix
# Datum: $(date)

echo "🚀 Starte Hetzner Update für ML-Dashboard Preisprognose Fix..."

# 1. Service stoppen
echo "⏹️ Stoppe BESS Service..."
sudo systemctl stop bess

# 2. Backup erstellen
echo "💾 Erstelle Backup..."
sudo cp /opt/bess/instance/bess.db /opt/bess/backups/bess_backup_$(date +%Y%m%d_%H%M%S).db

# 3. Git Pull
echo "📥 Lade Updates von Git..."
cd /opt/bess
sudo git pull origin main

# 4. Python Dependencies prüfen
echo "🐍 Prüfe Python Dependencies..."
sudo pip3 install -r requirements.txt

# 5. Service neu starten
echo "▶️ Starte BESS Service neu..."
sudo systemctl start bess

# 6. Service Status prüfen
echo "🔍 Prüfe Service Status..."
sudo systemctl status bess --no-pager

# 7. Logs prüfen
echo "📋 Zeige letzte Logs..."
sudo journalctl -u bess --no-pager -n 20

echo "✅ Hetzner Update abgeschlossen!"
echo ""
echo "🔮 ML-Dashboard Preisprognose sollte jetzt funktionieren:"
echo "   - Wählen Sie ein Projekt aus"
echo "   - Klicken Sie auf 'Daten laden'"
echo "   - Klicken Sie auf 'Prognose starten'"
echo ""
echo "📊 Die Preisprognose verwendet jetzt echte APG-Daten aus der Datenbank"
echo "   anstatt Demo-Daten."
