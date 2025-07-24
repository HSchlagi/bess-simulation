#!/bin/bash

# BESS Simulation - Installation auf Hetzner Server
# Ausführung: bash install_bess_on_hetzner.sh

set -e  # Exit on any error

echo "🚀 BESS Simulation Installation auf Hetzner Server"
echo "=================================================="

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktionen
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Verzeichnisse erstellen
log_info "Erstelle Verzeichnisse..."
mkdir -p /var/log/bess-simulation
mkdir -p /var/www/bess-simulation/instance/exports
chown -R www-data:www-data /var/log/bess-simulation
chown -R www-data:www-data /var/www/bess-simulation

# 2. Nginx-Konfiguration installieren
log_info "Installiere Nginx-Konfiguration..."
cp nginx_bess_config.conf /etc/nginx/sites-available/bess.instanet.at
ln -sf /etc/nginx/sites-available/bess.instanet.at /etc/nginx/sites-enabled/

# 3. Systemd Service installieren
log_info "Installiere Systemd Service..."
cp bess-simulation.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable bess-simulation

# 4. Nginx-Konfiguration testen
log_info "Teste Nginx-Konfiguration..."
nginx -t

if [ $? -eq 0 ]; then
    log_success "Nginx-Konfiguration ist gültig"
else
    log_error "Nginx-Konfiguration ist ungültig"
    exit 1
fi

# 5. Nginx neu laden
log_info "Lade Nginx neu..."
systemctl reload nginx

# 6. BESS Simulation Service starten
log_info "Starte BESS Simulation Service..."
systemctl start bess-simulation

# 7. Status prüfen
log_info "Prüfe Service-Status..."
sleep 3
systemctl status bess-simulation --no-pager

# 8. SSL-Zertifikat mit Let's Encrypt
log_info "Installiere SSL-Zertifikat..."
if command -v certbot &> /dev/null; then
    certbot --nginx -d bess.instanet.at --non-interactive --agree-tos --email admin@instanet.at
    log_success "SSL-Zertifikat installiert"
else
    log_warning "Certbot nicht gefunden. SSL-Zertifikat muss manuell installiert werden."
    log_info "Führe aus: apt install certbot python3-certbot-nginx"
    log_info "Dann: certbot --nginx -d bess.instanet.at"
fi

# 9. Firewall konfigurieren
log_info "Konfiguriere Firewall..."
ufw allow 'Nginx Full'
ufw allow ssh
ufw --force enable

# 10. Finale Prüfung
log_info "Führe finale Prüfung durch..."

# Service-Status
if systemctl is-active --quiet bess-simulation; then
    log_success "BESS Simulation Service läuft"
else
    log_error "BESS Simulation Service läuft nicht"
fi

# Nginx-Status
if systemctl is-active --quiet nginx; then
    log_success "Nginx läuft"
else
    log_error "Nginx läuft nicht"
fi

# Port-Prüfung
if netstat -tlnp | grep :8000 > /dev/null; then
    log_success "Gunicorn läuft auf Port 8000"
else
    log_error "Gunicorn läuft nicht auf Port 8000"
fi

echo ""
echo "🎉 Installation abgeschlossen!"
echo "=============================="
echo ""
echo "🌐 BESS Simulation ist verfügbar unter:"
echo "   https://bess.instanet.at"
echo ""
echo "📋 Nützliche Befehle:"
echo "   Service-Status:     systemctl status bess-simulation"
echo "   Service neustarten: systemctl restart bess-simulation"
echo "   Logs anzeigen:      journalctl -u bess-simulation -f"
echo "   Nginx neuladen:     systemctl reload nginx"
echo ""
echo "🔧 Troubleshooting:"
echo "   Nginx-Logs:         tail -f /var/log/nginx/bess.instanet.at.error.log"
echo "   App-Logs:           tail -f /var/log/bess-simulation/error.log"
echo "   Datenbank:          sqlite3 /var/www/bess-simulation/instance/bess.db"
echo ""
log_success "Installation erfolgreich abgeschlossen!" 