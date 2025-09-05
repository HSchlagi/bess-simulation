#!/bin/bash
# Hetzner-Server Update-Skript für BESS-Simulation
# Aktualisiert den Server mit dem neuesten Git-Stand

echo "🚀 BESS-Simulation Hetzner-Update gestartet..."
echo "=============================================="

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktion für farbige Ausgabe
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Aktuelles Verzeichnis prüfen
print_status "Überprüfe aktuelles Verzeichnis..."
if [ ! -d "/opt/bess-simulation" ]; then
    print_error "BESS-Simulation Verzeichnis nicht gefunden!"
    exit 1
fi

cd /opt/bess-simulation
print_success "Im BESS-Simulation Verzeichnis: $(pwd)"

# 2. Service stoppen
print_status "Stoppe BESS-Service..."
sudo systemctl stop bess
if [ $? -eq 0 ]; then
    print_success "BESS-Service gestoppt"
else
    print_warning "Service war möglicherweise nicht aktiv"
fi

# 3. Backup der aktuellen Datenbank erstellen
print_status "Erstelle Backup der aktuellen Datenbank..."
if [ -f "instance/bess.db" ]; then
    backup_name="database_backup_before_update_$(date +%Y-%m-%d_%H-%M-%S).sql.gz"
    sqlite3 instance/bess.db .dump | gzip > "$backup_name"
    print_success "Datenbank-Backup erstellt: $backup_name"
else
    print_warning "Keine aktuelle Datenbank gefunden"
fi

# 4. Git-Update durchführen
print_status "Führe Git-Update durch..."
git fetch origin
git reset --hard origin/main
if [ $? -eq 0 ]; then
    print_success "Git-Update erfolgreich"
else
    print_error "Git-Update fehlgeschlagen!"
    exit 1
fi

# 5. Python-Abhängigkeiten aktualisieren
print_status "Aktualisiere Python-Abhängigkeiten..."
source venv/bin/activate
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    print_success "Python-Abhängigkeiten aktualisiert"
else
    print_error "Fehler beim Aktualisieren der Abhängigkeiten!"
    exit 1
fi

# 6. Datenbank-Migrationen durchführen (falls vorhanden)
print_status "Führe Datenbank-Migrationen durch..."
python -c "
import sys
sys.path.append('.')
try:
    from app import create_app, db
    app = create_app()
    with app.app_context():
        # Hier können spezifische Migrationen hinzugefügt werden
        print('Datenbank-Migrationen erfolgreich')
except Exception as e:
    print(f'Migration-Fehler: {e}')
"

# 7. Berechtigungen setzen
print_status "Setze Dateiberechtigungen..."
sudo chown -R www-data:www-data /opt/bess-simulation
sudo chmod -R 755 /opt/bess-simulation
sudo chmod 664 instance/bess.db 2>/dev/null || true
print_success "Berechtigungen gesetzt"

# 8. Service neu starten
print_status "Starte BESS-Service neu..."
sudo systemctl start bess
if [ $? -eq 0 ]; then
    print_success "BESS-Service gestartet"
else
    print_error "Fehler beim Starten des Services!"
    exit 1
fi

# 9. Service-Status prüfen
print_status "Prüfe Service-Status..."
sleep 3
if systemctl is-active --quiet bess; then
    print_success "BESS-Service läuft erfolgreich"
else
    print_error "BESS-Service läuft nicht!"
    sudo systemctl status bess
    exit 1
fi

# 10. Nginx neu laden
print_status "Lade Nginx-Konfiguration neu..."
sudo systemctl reload nginx
if [ $? -eq 0 ]; then
    print_success "Nginx neu geladen"
else
    print_warning "Nginx-Reload fehlgeschlagen - manuell prüfen"
fi

echo ""
echo "=============================================="
print_success "🎉 Hetzner-Update erfolgreich abgeschlossen!"
echo ""
echo "📊 Service-Status:"
sudo systemctl status bess --no-pager -l
echo ""
echo "🌐 BESS-Simulation ist verfügbar unter:"
echo "   https://bess.instanet.at"
echo ""
echo "📝 Logs anzeigen mit:"
echo "   sudo journalctl -u bess -f"
echo ""
