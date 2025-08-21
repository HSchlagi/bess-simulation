# 🔄 BESS Backup-Automatisierung Anleitung

## 📋 Übersicht

Diese Anleitung erklärt, wie Sie das automatische Backup-System für die BESS-Simulation einrichten und verwenden.

## 🚀 Schnellstart

### 1. Manuelles Backup erstellen

```powershell
# Tägliches Backup
python backup_automation.py

# Oder mit PowerShell
.\backup_automation.ps1

# Oder mit Batch-Script
backup_daily.bat
```

### 2. Backup-Statistiken anzeigen

```powershell
.\backup_automation.ps1 -ShowStats
```

### 3. Verfügbare Backups auflisten

```powershell
.\backup_automation.ps1 -ListBackups
```

## ⚙️ Konfiguration

### Backup-Konfiguration anpassen

Die Backup-Konfiguration wird in `backup_config.json` gespeichert:

```json
{
  "retention": {
    "daily": 7,      // 7 tägliche Backups behalten
    "weekly": 4,     // 4 wöchentliche Backups behalten
    "monthly": 12    // 12 monatliche Backups behalten
  },
  "compression": true,
  "email_notifications": false,
  "email_config": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "",
    "password": "",
    "to_email": ""
  }
}
```

### E-Mail-Benachrichtigungen einrichten

1. Öffnen Sie `backup_config.json`
2. Setzen Sie `email_notifications` auf `true`
3. Füllen Sie die E-Mail-Konfiguration aus:

```json
{
  "email_notifications": true,
  "email_config": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "ihre-email@gmail.com",
    "password": "ihr-app-passwort",
    "to_email": "admin@firma.com"
  }
}
```

**Hinweis:** Für Gmail müssen Sie ein App-Passwort verwenden.

## 🔄 Automatische Backups einrichten

### Windows Task Scheduler

1. **Task Scheduler öffnen:**
   - Windows + R → `taskschd.msc`

2. **Neuen Task erstellen:**
   - "Create Basic Task" → "Daily"
   - Name: "BESS Daily Backup"
   - Start time: 02:00 (nachts)

3. **Action konfigurieren:**
   - Program: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\Pfad\zu\backup_automation.ps1"`

4. **Erweiterte Einstellungen:**
   - "Run whether user is logged on or not"
   - "Run with highest privileges"

### PowerShell Scheduled Job

```powershell
# Tägliches Backup um 02:00 Uhr
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$PWD\backup_automation.ps1`""
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "BESS Daily Backup" -Action $action -Trigger $trigger -RunLevel Highest
```

### Wöchentliche und monatliche Backups

```powershell
# Wöchentliches Backup (Sonntag 03:00)
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$PWD\backup_automation.ps1`" -BackupType weekly"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am
Register-ScheduledTask -TaskName "BESS Weekly Backup" -Action $action -Trigger $trigger -RunLevel Highest

# Monatliches Backup (1. des Monats 04:00)
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$PWD\backup_automation.ps1`" -BackupType monthly"
$trigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 4 -DaysOfWeek Sunday -At 4am
Register-ScheduledTask -TaskName "BESS Monthly Backup" -Action $action -Trigger $trigger -RunLevel Highest
```

## 📊 Monitoring und Wartung

### Backup-Statistiken prüfen

```powershell
# Statistiken anzeigen
.\backup_automation.ps1 -ShowStats

# Log-Datei prüfen
Get-Content backup.log -Tail 50
```

### Backup-Test durchführen

```powershell
# Wiederherstellungstest
.\backup_automation.ps1 -TestRestore
```

### Alte Backups bereinigen

Das System löscht automatisch alte Backups basierend auf der Retention-Policy:

- **Täglich:** 7 Backups behalten
- **Wöchentlich:** 4 Backups behalten  
- **Monatlich:** 12 Backups behalten

## 🔧 Fehlerbehebung

### Häufige Probleme

1. **Python nicht gefunden:**
   ```
   Python nicht gefunden. Bitte installieren Sie Python.
   ```
   **Lösung:** Python installieren und PATH-Variable setzen

2. **Datenbank nicht gefunden:**
   ```
   Datenbank nicht gefunden: instance/bess.db
   ```
   **Lösung:** Stellen Sie sicher, dass die BESS-Simulation läuft und die Datenbank existiert

3. **Berechtigungsfehler:**
   ```
   Fehler beim Erstellen des Backups: Permission denied
   ```
   **Lösung:** PowerShell als Administrator ausführen

4. **E-Mail-Fehler:**
   ```
   Fehler beim Senden der E-Mail-Benachrichtigung
   ```
   **Lösung:** E-Mail-Konfiguration prüfen, App-Passwort für Gmail verwenden

### Log-Dateien

- **backup.log:** Haupt-Log-Datei
- **backup_automation.log:** PowerShell-Log-Datei
- **backup_stats.json:** Backup-Statistiken

## 📁 Backup-Verzeichnisstruktur

```
backups/
├── bess_daily_2025-01-21_02-00-00.sql.gz
├── bess_daily_2025-01-20_02-00-00.sql.gz
├── bess_weekly_2025-01-19_03-00-00.sql.gz
└── bess_monthly_2025-01-01_04-00-00.sql.gz
```

## 🔒 Sicherheitshinweise

1. **Backup-Verzeichnis sichern:** Stellen Sie sicher, dass das `backups/` Verzeichnis sicher ist
2. **E-Mail-Passwörter:** Verwenden Sie App-Passwörter für E-Mail-Benachrichtigungen
3. **Regelmäßige Tests:** Führen Sie regelmäßig Wiederherstellungstests durch
4. **Offsite-Backups:** Kopieren Sie wichtige Backups an einen externen Standort

## 📞 Support

Bei Problemen mit dem Backup-System:

1. Prüfen Sie die Log-Dateien
2. Führen Sie manuelle Backups durch
3. Testen Sie die Wiederherstellung
4. Kontaktieren Sie den Systemadministrator

---

**Letzte Aktualisierung:** 21. Januar 2025  
**Version:** 1.0  
**Autor:** BESS-Simulation Team
