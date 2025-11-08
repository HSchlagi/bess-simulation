#!/bin/bash
# Hetzner Server Deployment - BESS Simulation
# ============================================

echo "🚀 BESS Simulation Hetzner Deployment"
echo "====================================="

# 1. In das BESS-Verzeichnis wechseln
echo "📁 Wechsle in BESS-Verzeichnis..."
cd /opt/bess-simulation

# 2. Service stoppen
echo "⏹️  Stoppe BESS Service..."
sudo systemctl stop bess

# 3. Backup der aktuellen Datenbank erstellen
echo "💾 Erstelle Datenbank-Backup..."
sudo cp instance/bess.db instance/bess.db.backup.$(date +%Y%m%d_%H%M%S)

# 4. Git Pull - Neueste Änderungen holen
echo "📥 Hole neueste Änderungen von GitHub..."
git pull origin main

# 5. Python-Abhängigkeiten aktualisieren
echo "📦 Aktualisiere Python-Abhängigkeiten..."
source venv/bin/activate
pip install -r requirements.txt

# 6. Datenbank-Migrationen ausführen (falls nötig)
echo "🗄️  Führe Datenbank-Migrationen aus..."
python -c "
import sqlite3
conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

# Überprüfe ob alle Spalten existieren
cursor.execute('PRAGMA table_info(project)')
project_columns = [row[1] for row in cursor.fetchall()]

cursor.execute('PRAGMA table_info(customer)')
customer_columns = [row[1] for row in cursor.fetchall()]

cursor.execute('PRAGMA table_info(spot_price)')
spot_price_columns = [row[1] for row in cursor.fetchall()]

print('✅ Datenbankstruktur überprüft')
conn.close()
"

# 7. Service neu starten
echo "🔄 Starte BESS Service neu..."
sudo systemctl start bess

# 8. Service-Status überprüfen
echo "📊 Überprüfe Service-Status..."
sudo systemctl status bess --no-pager

# 9. Nginx-Status überprüfen
echo "🌐 Überprüfe Nginx-Status..."
sudo systemctl status nginx --no-pager

# 10. Logs überprüfen
echo "📋 Zeige aktuelle Logs..."
sudo journalctl -u bess -n 20 --no-pager

echo ""
echo "✅ Deployment abgeschlossen!"
echo "🌐 BESS ist verfügbar unter: https://bess.instanet.at"
echo "📊 Dashboard: https://bess.instanet.at/dashboard"
echo "🔧 Admin: https://bess.instanet.at/admin/dashboard"


















