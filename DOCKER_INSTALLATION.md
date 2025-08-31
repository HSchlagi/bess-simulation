# 🐳 Docker Installation für Windows

## 📋 Voraussetzungen

- Windows 10/11 (64-bit)
- Mindestens 4GB RAM
- Virtualisierung aktiviert (Hyper-V, WSL2)

## 🚀 Installation

### 1. Docker Desktop herunterladen
- Gehen Sie zu: https://www.docker.com/products/docker-desktop/
- Klicken Sie auf "Download for Windows"
- Laden Sie die neueste Version herunter

### 2. Docker Desktop installieren
- Führen Sie die heruntergeladene `.exe` Datei aus
- Folgen Sie dem Installationsassistenten
- Aktivieren Sie "Use WSL 2 instead of Hyper-V" (empfohlen)
- Klicken Sie auf "OK" und warten Sie auf den Neustart

### 3. System neu starten
- Nach der Installation wird ein Neustart empfohlen
- Starten Sie Ihren Computer neu

### 4. Docker Desktop starten
- Starten Sie Docker Desktop aus dem Startmenü
- Warten Sie, bis der Docker-Engine-Status "Running" anzeigt
- Das Docker-Symbol in der Taskleiste sollte grün sein

## ✅ Installation testen

Öffnen Sie PowerShell und führen Sie aus:

```powershell
# Docker-Version prüfen
docker --version

# Docker Compose-Version prüfen
docker-compose --version

# Test-Container starten
docker run hello-world
```

## 🔧 Konfiguration

### WSL2 aktivieren (falls nicht aktiviert)
```powershell
# Als Administrator ausführen
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# WSL2 herunterladen und installieren
# https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi

# WSL2 als Standard setzen
wsl --set-default-version 2
```

### Docker Desktop Einstellungen
1. **Resources:** Mindestens 2GB RAM für BESS-Simulation
2. **File Sharing:** C:\ und D:\ freigeben
3. **Advanced:** WSL2 aktivieren

## 🚀 BESS-Simulation starten

Nach der Installation:

```powershell
# Zum Projektverzeichnis wechseln
cd D:\Daten-Heinz\BESS-Simulation

# Docker-Container starten
.\docker-start.ps1

# Oder manuell
docker-compose up -d
```

## 🔍 Troubleshooting

### Docker startet nicht
- **Hyper-V aktivieren:** Windows-Features → Hyper-V aktivieren
- **WSL2 installieren:** Microsoft Store → Ubuntu installieren
- **Antivirus:** Docker-Verzeichnisse ausschließen

### Port 5000 belegt
```powershell
# Ports prüfen
netstat -an | findstr :5000

# Anderen Port verwenden
docker-compose up -d -p 5001:5000
```

### WSL2 Fehler
```powershell
# WSL-Status prüfen
wsl --list --verbose

# WSL neu starten
wsl --shutdown
wsl --start
```

## 📊 Systemanforderungen

### Minimum
- **RAM:** 4GB
- **CPU:** 2 Kerne
- **Speicher:** 10GB freier Platz

### Empfohlen
- **RAM:** 8GB
- **CPU:** 4 Kerne
- **Speicher:** 20GB freier Platz

## 🔒 Sicherheit

- Docker läuft mit eingeschränkten Berechtigungen
- Container sind isoliert
- Volumes sind sicher eingebunden
- Netzwerk ist isoliert

## 📞 Support

Bei Problemen:
1. **Docker-Logs:** Docker Desktop → Troubleshoot → Logs
2. **WSL-Logs:** `wsl --shutdown && wsl --start`
3. **System-Logs:** Event Viewer → Windows Logs → Application

---

**Version:** 1.0  
**Letzte Aktualisierung:** 31. August 2025  
**Status:** ✅ Installationsanleitung erstellt
