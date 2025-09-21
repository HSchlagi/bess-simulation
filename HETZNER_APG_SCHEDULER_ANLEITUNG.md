# APG Scheduler Installation auf Hetzner Ubuntu Server

## 🎯 **Übersicht**

Diese Anleitung zeigt, wie Sie den APG Scheduler für automatische 2025-Daten auf Ihrem Hetzner Ubuntu Server installieren.

## 📋 **Voraussetzungen**

- Hetzner Ubuntu Server (20.04+ oder 22.04+)
- BESS-Simulation bereits installiert in `/opt/bess`
- Root-Zugriff oder sudo-Berechtigung
- Python Virtual Environment aktiv

## 🚀 **Installation**

### **Option 1: systemd Service (Empfohlen)**

```bash
# 1. Dateien auf Server kopieren
scp apg_scheduler_linux.py root@your-server:/opt/bess/
scp bess-apg-scheduler.service root@your-server:/opt/bess/
scp install_apg_scheduler_hetzner.sh root@your-server:/opt/bess/

# 2. Auf Server einloggen
ssh root@your-server

# 3. Script ausführbar machen
chmod +x /opt/bess/install_apg_scheduler_hetzner.sh

# 4. Installation ausführen
/opt/bess/install_apg_scheduler_hetzner.sh
```

### **Option 2: Cron Job (Alternative)**

```bash
# 1. Cron Job Script kopieren
scp apg_cron_job.sh root@your-server:/opt/bess/

# 2. Script ausführbar machen
chmod +x /opt/bess/apg_cron_job.sh

# 3. Cron Job hinzufügen
crontab -e

# 4. Diese Zeile hinzufügen:
0 13 * * * /opt/bess/apg_cron_job.sh

# 5. Log-Verzeichnis erstellen
mkdir -p /var/log/bess
chown bess:bess /var/log/bess
```

## ⚙️ **Konfiguration**

### **Service-Verwaltung**

```bash
# Service-Status prüfen
systemctl status bess-apg-scheduler

# Service starten
systemctl start bess-apg-scheduler

# Service stoppen
systemctl stop bess-apg-scheduler

# Service neustarten
systemctl restart bess-apg-scheduler

# Service deaktivieren
systemctl disable bess-apg-scheduler
```

### **Logs überwachen**

```bash
# Live-Logs anzeigen
journalctl -u bess-apg-scheduler -f

# Letzte 50 Einträge
journalctl -u bess-apg-scheduler -n 50

# Logs nach Datum filtern
journalctl -u bess-apg-scheduler --since "2025-09-08" --until "2025-09-09"
```

## 📅 **Zeitplan**

Der Scheduler führt folgende Jobs aus:

- **13:00 Uhr:** aWattar-Import (täglich)
- **14:00 Uhr:** APG-Import (Fallback)
- **15:00 Uhr:** Datenbereinigung (löscht alte Demo-Daten)
- **16:00 Uhr:** Statistiken

## 🔧 **Manuelle Tests**

### **Sofortiger Test-Import**

```bash
# Als bess User
sudo -u bess /opt/bess/venv/bin/python /opt/bess/apg_scheduler_linux.py
```

### **Einzelne Funktionen testen**

```bash
# Nur aWattar-Import
sudo -u bess /opt/bess/venv/bin/python -c "
from apg_scheduler_linux import APGSchedulerLinux
scheduler = APGSchedulerLinux()
scheduler.import_daily_awattar_data()
"

# Nur Statistiken
sudo -u bess /opt/bess/venv/bin/python -c "
from apg_scheduler_linux import APGSchedulerLinux
scheduler = APGSchedulerLinux()
scheduler.get_database_stats()
"
```

## 📊 **Überwachung**

### **Datenbank-Statistiken prüfen**

```bash
# SQLite-Datenbank direkt abfragen
sqlite3 /opt/bess/instance/bess.db "
SELECT 
    source, 
    COUNT(*) as count,
    AVG(price_eur_mwh) as avg_price,
    MAX(price_eur_mwh) as max_price,
    MIN(price_eur_mwh) as min_price
FROM spot_price 
GROUP BY source
ORDER BY count DESC;
"
```

### **2025-Daten prüfen**

```bash
# Anzahl 2025-Daten
sqlite3 /opt/bess/instance/bess.db "
SELECT COUNT(*) as count_2025 
FROM spot_price 
WHERE timestamp LIKE '2025%';
"
```

## 🚨 **Fehlerbehebung**

### **Service startet nicht**

```bash
# Detaillierte Fehlermeldungen
journalctl -u bess-apg-scheduler --no-pager

# Service-Konfiguration prüfen
systemctl cat bess-apg-scheduler

# Manueller Start mit Debug
sudo -u bess /opt/bess/venv/bin/python /opt/bess/apg_scheduler_linux.py
```

### **Berechtigungsprobleme**

```bash
# Besitzer korrigieren
chown -R bess:bess /opt/bess

# Log-Verzeichnis korrigieren
chown bess:bess /var/log/bess
chmod 755 /var/log/bess
```

### **Datenbank-Probleme**

```bash
# Datenbank-Berechtigungen prüfen
ls -la /opt/bess/instance/bess.db

# Datenbank reparieren
sqlite3 /opt/bess/instance/bess.db "PRAGMA integrity_check;"
```

## 📈 **Performance-Optimierung**

### **Ressourcen-Limits anpassen**

```bash
# Service-File bearbeiten
nano /etc/systemd/system/bess-apg-scheduler.service

# Memory-Limit erhöhen (falls nötig)
MemoryMax=1G

# Service neu laden
systemctl daemon-reload
systemctl restart bess-apg-scheduler
```

### **Log-Rotation konfigurieren**

```bash
# Logrotate-Konfiguration
cat > /etc/logrotate.d/bess-apg-scheduler << EOF
/var/log/bess/apg_scheduler.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 bess bess
}
EOF
```

## 🔄 **Updates**

### **Scheduler aktualisieren**

```bash
# Neue Version kopieren
scp apg_scheduler_linux.py root@your-server:/opt/bess/

# Service neustarten
systemctl restart bess-apg-scheduler

# Status prüfen
systemctl status bess-apg-scheduler
```

## 📞 **Support**

Bei Problemen:

1. **Logs prüfen:** `journalctl -u bess-apg-scheduler -f`
2. **Service-Status:** `systemctl status bess-apg-scheduler`
3. **Manueller Test:** Siehe "Manuelle Tests" oben
4. **Datenbank prüfen:** Siehe "Überwachung" oben

## ✅ **Erfolgreiche Installation**

Nach erfolgreicher Installation sollten Sie sehen:

- ✅ Service läuft: `systemctl status bess-apg-scheduler`
- ✅ Täglich neue 2025-Daten in der Datenbank
- ✅ Logs in `/var/log/bess/apg_scheduler.log`
- ✅ Automatische Bereinigung alter Daten

**Der APG Scheduler läuft jetzt automatisch auf Ihrem Hetzner Server und lädt täglich aktuelle österreichische Spot-Preise!** 🚀

















