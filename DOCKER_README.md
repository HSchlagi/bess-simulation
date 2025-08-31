# 🐳 BESS-Simulation Docker-Containerisierung

## 📋 Übersicht

Die BESS-Simulation ist jetzt vollständig containerisiert und kann sowohl lokal als auch in Produktionsumgebungen mit Docker ausgeführt werden.

## 🚀 Schnellstart

### Voraussetzungen
- Docker Desktop installiert
- Docker Compose verfügbar
- Mindestens 2GB freier RAM

### Lokale Entwicklung starten

```bash
# Mit Shell-Skript (Linux/Mac)
./docker-start.sh

# Mit PowerShell (Windows)
.\docker-start.ps1

# Oder manuell
docker-compose up -d
```

### Produktionsumgebung starten

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Container-Konfiguration

### BESS-Simulation Container
- **Port:** 5000 (intern) → 5000 (extern)
- **Umgebung:** Development/Production
- **Volumes:** Datenbank, Daten, Logs, Backups
- **Ressourcen:** 1GB RAM, 1 CPU

### Redis Container
- **Port:** 6379
- **Persistenz:** AOF (Append Only File)
- **Speicher:** 256MB mit LRU-Policy
- **Ressourcen:** 512MB RAM, 0.5 CPU

### Nginx Container (Produktion)
- **Ports:** 80, 443
- **SSL:** Unterstützt
- **Reverse Proxy:** Für BESS-Simulation

## 📁 Verzeichnisstruktur

```
BESS-Simulation/
├── Dockerfile                 # Container-Definition
├── docker-compose.yml         # Lokale Entwicklung
├── docker-compose.prod.yml    # Produktionsumgebung
├── .dockerignore             # Build-Ausschlüsse
├── run_docker.py             # Docker-optimierte run.py
├── docker-start.sh           # Linux/Mac Start-Skript
├── docker-start.ps1          # Windows Start-Skript
└── instance/                 # Datenbank (Volume)
    └── bess.db
```

## 🛠️ Nützliche Docker-Befehle

### Container verwalten
```bash
# Status anzeigen
docker-compose ps

# Logs anzeigen
docker-compose logs -f bess-simulation

# Container neu starten
docker-compose restart bess-simulation

# Container stoppen
docker-compose down
```

### Datenbank-Backup
```bash
# Datenbank sichern
docker exec bess-simulation_bess-simulation_1 python backup_database.py

# Backup-Datei kopieren
docker cp bess-simulation_bess-simulation_1:/app/backups/ ./local-backups/
```

### Performance-Monitoring
```bash
# Container-Ressourcen anzeigen
docker stats

# Container-Details
docker inspect bess-simulation_bess-simulation_1
```

## 🔍 Troubleshooting

### Container startet nicht
```bash
# Logs prüfen
docker-compose logs bess-simulation

# Container neu bauen
docker-compose build --no-cache

# Volumes löschen (Vorsicht!)
docker-compose down -v
```

### Redis-Verbindungsfehler
```bash
# Redis-Status prüfen
docker-compose exec redis redis-cli ping

# Redis-Logs anzeigen
docker-compose logs redis
```

### Port-Konflikte
```bash
# Ports prüfen
netstat -an | grep :5000

# Anderen Port verwenden
docker-compose up -d -p 5001:5000
```

## 📊 Monitoring & Logs

### Health-Check
- **Endpoint:** `/api/performance/health`
- **Intervall:** 30 Sekunden
- **Timeout:** 10 Sekunden
- **Retries:** 3

### Logs sammeln
```bash
# Alle Logs
docker-compose logs > all-logs.txt

# Nur BESS-Simulation
docker-compose logs bess-simulation > bess-logs.txt

# Live-Logs
docker-compose logs -f --tail=100
```

## 🚀 Deployment

### Lokale Entwicklung
```bash
# Entwicklungsumgebung
docker-compose up -d

# Mit Debug
FLASK_DEBUG=1 docker-compose up -d
```

### Produktionsumgebung
```bash
# Produktionsumgebung
docker-compose -f docker-compose.prod.yml up -d

# Mit SSL
docker-compose -f docker-compose.prod.yml -f docker-compose.ssl.yml up -d
```

### Hetzner-Server
```bash
# Auf Hetzner deployen
docker-compose -f docker-compose.prod.yml up -d

# Mit Nginx
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Sicherheit

### Umgebungsvariablen
- **FLASK_ENV:** production/development
- **FLASK_DEBUG:** 0/1
- **REDIS_URL:** Redis-Verbindung
- **DATABASE_URL:** Datenbank-Verbindung

### Netzwerk
- **Bridge-Netzwerk:** Isolierte Container
- **Port-Mapping:** Nur notwendige Ports
- **Volume-Berechtigungen:** Eingeschränkt

## 📈 Performance

### Caching
- **Redis:** In-Memory-Caching
- **TTL:** Konfigurierbare Timeouts
- **Policies:** LRU für Speicherverwaltung

### Ressourcen
- **Memory-Limits:** Verhindert OOM
- **CPU-Limits:** Faire Ressourcenverteilung
- **Health-Checks:** Automatische Überwachung

## 🔄 Updates

### Container aktualisieren
```bash
# Code-Änderungen
git pull origin main

# Container neu bauen
docker-compose build --no-cache

# Container neu starten
docker-compose up -d
```

### Datenbank-Migrationen
```bash
# Migrationen ausführen
docker-compose exec bess-simulation python migrate_bess_extension.py

# Datenbank-Status prüfen
docker-compose exec bess-simulation python check_database_structure.py
```

## 📞 Support

Bei Problemen mit der Docker-Containerisierung:

1. **Logs prüfen:** `docker-compose logs`
2. **Status prüfen:** `docker-compose ps`
3. **Container neu starten:** `docker-compose restart`
4. **Neu bauen:** `docker-compose build --no-cache`

---

**Version:** 1.0  
**Letzte Aktualisierung:** 31. August 2025  
**Status:** ✅ Vollständig implementiert
