#!/bin/bash
# APG Cron Job für täglichen Datenimport
# Alternative zu systemd Service

# Projekt-Verzeichnis
PROJECT_DIR="/opt/bess"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/apg_scheduler_linux.py"
LOG_FILE="/var/log/bess/apg_cron.log"

# Log-Funktion
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Starte Import
log "Starte APG-Datenimport..."

# Wechsle ins Projekt-Verzeichnis
cd "$PROJECT_DIR"

# Führe Import aus
if "$PYTHON_PATH" -c "
from apg_scheduler_linux import APGSchedulerLinux
scheduler = APGSchedulerLinux()
scheduler.import_daily_awattar_data()
scheduler.get_database_stats()
"; then
    log "APG-Datenimport erfolgreich abgeschlossen"
else
    log "FEHLER: APG-Datenimport fehlgeschlagen"
    exit 1
fi

log "APG-Datenimport beendet"






