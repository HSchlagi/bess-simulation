#!/bin/bash
# APG Scheduler Installation für Hetzner Server
# Installiert den automatischen APG-Datenimport

set -e

echo "🚀 APG Scheduler Installation für Hetzner Server"
echo "================================================"

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Log-Funktion
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Prüfe ob als root ausgeführt
if [ "$EUID" -ne 0 ]; then
    error "Bitte als root ausführen: sudo $0"
fi

# Projekt-Verzeichnis
PROJECT_DIR="/opt/bess"
SERVICE_NAME="bess-apg-scheduler"
LOG_DIR="/var/log/bess"

log "📁 Erstelle Verzeichnisse..."
mkdir -p "$LOG_DIR"
mkdir -p "$PROJECT_DIR/instance"

log "👤 Erstelle bess User (falls nicht vorhanden)..."
if ! id "bess" &>/dev/null; then
    useradd -r -s /bin/bash -d "$PROJECT_DIR" -m bess
    log "✅ bess User erstellt"
else
    log "✅ bess User bereits vorhanden"
fi

log "🔐 Setze Berechtigungen..."
chown -R bess:bess "$PROJECT_DIR"
chown -R bess:bess "$LOG_DIR"
chmod 755 "$LOG_DIR"

log "📄 Installiere systemd Service..."
cp "$SERVICE_NAME.service" "/etc/systemd/system/"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

log "⏰ Erstelle Cron Job für tägliche Ausführung..."
# Cron Job für 13:00 Uhr täglich
(crontab -u bess -l 2>/dev/null; echo "0 13 * * * /opt/bess/venv/bin/python /opt/bess/apg_scheduler_linux.py >> /var/log/bess/apg_cron.log 2>&1") | crontab -u bess -

log "🧪 Teste APG Scheduler..."
if sudo -u bess "$PROJECT_DIR/venv/bin/python" "$PROJECT_DIR/apg_scheduler_linux.py" stats; then
    log "✅ APG Scheduler Test erfolgreich"
else
    warning "⚠️ APG Scheduler Test fehlgeschlagen - prüfe Logs"
fi

log "📊 Erstelle Logrotate-Konfiguration..."
cat > /etc/logrotate.d/bess-apg-scheduler << EOF
$LOG_DIR/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 bess bess
    postrotate
        systemctl reload $SERVICE_NAME > /dev/null 2>&1 || true
    endscript
}
EOF

log "🔧 Konfiguriere Firewall (falls ufw aktiv)..."
if command -v ufw &> /dev/null && ufw status | grep -q "Status: active"; then
    ufw allow 22/tcp comment "SSH"
    ufw allow 80/tcp comment "HTTP"
    ufw allow 443/tcp comment "HTTPS"
    log "✅ Firewall konfiguriert"
fi

log "📋 Erstelle Status-Check Script..."
cat > /usr/local/bin/bess-apg-status << 'EOF'
#!/bin/bash
echo "🔍 BESS APG Scheduler Status"
echo "============================"

echo "📊 Service Status:"
systemctl status bess-apg-scheduler --no-pager -l

echo ""
echo "📈 Letzte Logs:"
journalctl -u bess-apg-scheduler -n 10 --no-pager

echo ""
echo "🗄️ Datenbank-Statistiken:"
sudo -u bess /opt/bess/venv/bin/python /opt/bess/apg_scheduler_linux.py stats

echo ""
echo "⏰ Cron Jobs:"
crontab -u bess -l | grep apg_scheduler || echo "Keine Cron Jobs gefunden"
EOF

chmod +x /usr/local/bin/bess-apg-status

log "🎯 Installation abgeschlossen!"
echo ""
echo "📋 Nächste Schritte:"
echo "1. Service starten: systemctl start $SERVICE_NAME"
echo "2. Status prüfen: bess-apg-status"
echo "3. Logs überwachen: journalctl -u $SERVICE_NAME -f"
echo "4. Manueller Test: sudo -u bess /opt/bess/venv/bin/python /opt/bess/apg_scheduler_linux.py"
echo ""
echo "⏰ Zeitplan:"
echo "- 13:00 Uhr: aWattar-Import (täglich)"
echo "- 14:00 Uhr: APG-Fallback (falls aWattar fehlschlägt)"
echo "- 15:00 Uhr: Datenbereinigung"
echo "- 16:00 Uhr: Statistiken"
echo ""
echo "📁 Wichtige Dateien:"
echo "- Service: /etc/systemd/system/$SERVICE_NAME.service"
echo "- Logs: $LOG_DIR/"
echo "- Datenbank: $PROJECT_DIR/instance/bess.db"
echo "- Status-Check: bess-apg-status"
echo ""
log "✅ APG Scheduler erfolgreich installiert!"

# Optional: Service sofort starten
read -p "🚀 Service jetzt starten? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl start "$SERVICE_NAME"
    sleep 2
    systemctl status "$SERVICE_NAME" --no-pager
    log "✅ Service gestartet!"
fi
