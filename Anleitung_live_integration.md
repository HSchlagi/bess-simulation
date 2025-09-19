# 🚀 Live BESS Integration Anleitung

## 📋 Übersicht

Diese Anleitung beschreibt die vollständige Integration von Live-Daten aus echten BESS-Speichersystemen in die BESS-Simulation. Das System unterstützt sowohl MQTT-basierte als auch HTTP-API-basierte Datenquellen.

## 🏗️ Systemarchitektur

```
[BESS-Speicher] → [MQTT Broker] → [MQTT Bridge] → [Flask App]
                     ↓
[FastAPI Service] → [SQLite DB] → [Flask App]
```

### Komponenten:
- **MQTT Broker (Mosquitto):** Empfängt Live-Daten von BESS-Speichern
- **MQTT Bridge:** Verbindet MQTT mit Flask-App
- **FastAPI Service:** RESTful API für Datenverarbeitung
- **SQLite Database:** Speichert Telemetrie-Daten
- **Flask App:** Hauptanwendung mit Live-Dashboards

## 🔧 Installation & Setup

### 1. Abhängigkeiten installieren

```bash
# MQTT-Abhängigkeiten
pip install paho-mqtt

# FastAPI-Abhängigkeiten (bereits in requirements.txt)
pip install fastapi uvicorn sqlalchemy

# Docker (für Live-System)
# Windows: Docker Desktop installieren
# Linux: docker-compose installieren
```

### 2. Live-System starten

```bash
# Ins Live-Verzeichnis wechseln
cd live

# Docker-Services starten
docker-compose up -d

# Status prüfen
docker-compose ps
```

### 3. Konfiguration

#### Umgebungsvariablen setzen:

```bash
# FastAPI Service
export LIVE_BESS_API_URL=http://localhost:8080
export LIVE_BESS_API_TOKEN=changeme_token_123

# MQTT Bridge
export USE_MQTT_BRIDGE=true
export MQTT_BROKER_HOST=localhost
export MQTT_BROKER_PORT=1883
export MQTT_USERNAME=bessuser
export MQTT_PASSWORD=besspass
export MQTT_BASE_TOPIC=bess

# Datenbank
export LIVE_BESS_DB_PATH=live/data/bess.db
```

#### Konfigurationsdatei erstellen:

```bash
# .env Datei im Hauptverzeichnis erstellen
cat > .env << EOF
LIVE_BESS_API_URL=http://localhost:8080
LIVE_BESS_API_TOKEN=changeme_token_123
USE_MQTT_BRIDGE=true
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=bessuser
MQTT_PASSWORD=besspass
MQTT_BASE_TOPIC=bess
LIVE_BESS_DB_PATH=live/data/bess.db
EOF
```

## 📡 MQTT Integration

### MQTT Broker Konfiguration

Die MQTT-Konfiguration befindet sich in `live/mosquitto/mosquitto.conf`:

```conf
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
listener 1883
allow_anonymous false
password_file /mosquitto/config/passwd
```

### MQTT Topics

Das System verwendet folgende Topic-Struktur:

```
bess/{site}/{device}/telemetry
```

**Beispiele:**
- `bess/site1/bess1/telemetry`
- `bess/site1/bess2/telemetry`
- `bess/site2/bess1/telemetry`

### Datenformat

MQTT-Nachrichten müssen folgendes JSON-Format haben:

```json
{
  "ts": "2025-01-01T00:00:00Z",
  "site": "site1",
  "device": "bess1",
  "soc": 57.1,
  "p": -120.0,
  "p_ch": 0.0,
  "p_dis": 120.0,
  "v_dc": 780.5,
  "i_dc": 160.2,
  "t_cell_max": 31.5,
  "soh": 98.6,
  "alarms": []
}
```

### Feldbeschreibungen:

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `ts` | string | Zeitstempel (ISO 8601) |
| `site` | string | Standort-ID |
| `device` | string | Geräte-ID |
| `soc` | float | State of Charge (%) |
| `p` | float | Gesamtleistung (kW, negativ = Laden) |
| `p_ch` | float | Ladeleistung (kW) |
| `p_dis` | float | Entladeleistung (kW) |
| `v_dc` | float | DC-Spannung (V) |
| `i_dc` | float | DC-Strom (A) |
| `t_cell_max` | float | Max. Zelltemperatur (°C) |
| `soh` | float | State of Health (%) |
| `alarms` | array | Alarm-Liste |

## 🔌 FastAPI Service

### Service starten

```bash
cd live
docker-compose up fastapi -d
```

### API Endpoints

#### 1. Daten einreichen
```http
POST /api/ingest
Authorization: Bearer changeme_token_123
Content-Type: application/json

{
  "ts": "2025-01-01T00:00:00Z",
  "site": "site1",
  "device": "bess1",
  "soc": 57.1,
  "p": -120.0,
  "p_ch": 0.0,
  "p_dis": 120.0,
  "v_dc": 780.5,
  "i_dc": 160.2,
  "t_cell_max": 31.5,
  "soh": 98.6,
  "alarms": []
}
```

#### 2. Neueste Daten abrufen
```http
GET /api/last?limit=10
Authorization: Bearer changeme_token_123
```

#### 3. System-Status prüfen
```http
GET /healthz
Authorization: Bearer changeme_token_123
```

## 🖥️ Flask Integration

### Verfügbare Routen

| Route | Beschreibung |
|-------|--------------|
| `/live-data` | Standard Dashboard |
| `/live-data/advanced` | Advanced Dashboard mit Auto-Refresh |
| `/api/live-data/status` | System-Status |
| `/api/live-data/latest` | Neueste Live-Daten |
| `/api/live-data/chart` | Chart-Daten |
| `/api/live-data/summary` | Geräte-Zusammenfassung |

### Menü-Integration

Die Live-Integration wurde automatisch in das Hauptmenü integriert:

```
Daten
├── Spot-Preise
├── Lastprofile
├── Wetterdaten
├── Live BESS Daten          ← NEU
└── Live Dashboard (Advanced) ← NEU
```

## 🧪 Testing

### 1. Test-Daten generieren

```bash
cd live
python examples/mqtt_sample_publisher.py
```

### 2. System-Status prüfen

```bash
# FastAPI Health Check
curl -H "Authorization: Bearer changeme_token_123" \
     http://localhost:8080/healthz

# Flask API Status
curl -H "Authorization: Bearer changeme_token_123" \
     http://localhost:5000/api/live-data/status
```

### 3. Dashboard testen

1. Flask-App starten: `python run.py`
2. Browser öffnen: `http://localhost:5000`
3. Einloggen und zu "Daten" → "Live BESS Daten" navigieren

## 🔧 Konfiguration für echte BESS-Systeme

### MQTT-Verbindung zu echtem BESS

1. **BESS-Konfiguration:**
   ```json
   {
     "mqtt_broker": "IHR_SERVER_IP",
     "mqtt_port": 1883,
     "mqtt_username": "bessuser",
     "mqtt_password": "besspass",
     "mqtt_topic": "bess/{site}/{device}/telemetry"
   }
   ```

2. **Netzwerk-Konfiguration:**
   ```bash
   # Firewall-Regel für MQTT
   sudo ufw allow 1883/tcp
   
   # Port-Forwarding (falls nötig)
   # Router: 1883 → Server: 1883
   ```

3. **SSL/TLS (Produktiv):**
   ```conf
   # mosquitto.conf
   listener 8883
   cafile /mosquitto/certs/ca.crt
   certfile /mosquitto/certs/server.crt
   keyfile /mosquitto/certs/server.key
   require_certificate false
   ```

### HTTP-API Integration

Falls Ihr BESS-System eine HTTP-API hat:

1. **API-Adapter erstellen:**
   ```python
   # app/bess_api_adapter.py
   import requests
   from .live_data_service import live_bess_service
   
   class BESSAPIAdapter:
       def __init__(self, api_url, api_key):
           self.api_url = api_url
           self.api_key = api_key
           
       def get_live_data(self):
           # Ihre BESS-API aufrufen
           response = requests.get(
               f"{self.api_url}/telemetry",
               headers={"Authorization": f"Bearer {self.api_key}"}
           )
           return response.json()
   ```

2. **Service erweitern:**
   ```python
   # In app/live_data_service.py
   def get_bess_api_data(self):
       adapter = BESSAPIAdapter(
           os.getenv('BESS_API_URL'),
           os.getenv('BESS_API_KEY')
       )
       return adapter.get_live_data()
   ```

## 📊 Monitoring & Debugging

### Logs prüfen

```bash
# Docker-Logs
docker-compose logs -f fastapi
docker-compose logs -f mosquitto

# Flask-Logs
tail -f logs/app.log

# MQTT-Bridge Logs
grep "MQTT" logs/app.log
```

### System-Status Dashboard

Das Advanced Dashboard zeigt:
- **Verbindungsstatus:** MQTT und FastAPI
- **Letzte Daten:** Zeitstempel der neuesten Nachricht
- **Geräte-Status:** Alle verbundenen BESS-Geräte
- **Alarm-Status:** Aktive Alarme

### Performance-Monitoring

```bash
# Datenbank-Größe prüfen
ls -lh live/data/bess.db

# API-Response-Zeit testen
time curl -H "Authorization: Bearer changeme_token_123" \
          http://localhost:8080/api/last?limit=1
```

## 🚨 Troubleshooting

### Häufige Probleme

#### 1. MQTT-Verbindung fehlgeschlagen
```bash
# Broker-Status prüfen
docker-compose ps mosquitto

# Logs prüfen
docker-compose logs mosquitto

# Manuell testen
mosquitto_pub -h localhost -t "test/topic" -m "test message"
```

#### 2. FastAPI nicht erreichbar
```bash
# Service-Status
docker-compose ps fastapi

# Port prüfen
netstat -tlnp | grep 8080

# Logs prüfen
docker-compose logs fastapi
```

#### 3. Keine Live-Daten im Dashboard
```bash
# Flask-Logs prüfen
grep "Live" logs/app.log

# API-Test
curl http://localhost:5000/api/live-data/status

# MQTT-Bridge-Status
grep "MQTT_Bridge" logs/app.log
```

#### 4. Datenformat-Fehler
```bash
# JSON-Validierung
python -m json.tool < data_sample.json

# Schema-Validierung
python -c "
import json
from app.live_data_service import TelemetryModel
data = json.load(open('data_sample.json'))
TelemetryModel(**data)
"
```

### Debug-Modus aktivieren

```bash
# Flask Debug-Modus
export FLASK_DEBUG=1

# MQTT-Debug-Logs
export MQTT_DEBUG=1

# FastAPI Debug-Modus
export FASTAPI_DEBUG=1
```

## 🔒 Sicherheit

### Produktions-Setup

1. **Sichere Passwörter:**
   ```bash
   # Passwort-Generator
   openssl rand -base64 32
   ```

2. **SSL/TLS aktivieren:**
   ```bash
   # Let's Encrypt Zertifikat
   certbot certonly --standalone -d yourdomain.com
   ```

3. **Firewall-Konfiguration:**
   ```bash
   # Nur notwendige Ports öffnen
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw allow 22/tcp   # SSH
   sudo ufw deny 1883/tcp  # MQTT (nur intern)
   ```

4. **API-Token rotieren:**
   ```bash
   # Neues Token generieren
   export LIVE_BESS_API_TOKEN=$(openssl rand -base64 32)
   ```

## 📈 Skalierung

### Mehrere BESS-Systeme

```python
# app/live_data_service.py
def get_all_devices(self):
    """Alle BESS-Geräte abrufen"""
    devices = []
    for site in self.get_sites():
        for device in self.get_devices(site):
            devices.append({
                'site': site,
                'device': device,
                'status': self.get_device_status(site, device)
            })
    return devices
```

### Load Balancing

```yaml
# docker-compose.yml
version: '3.8'
services:
  fastapi:
    deploy:
      replicas: 3
    ports:
      - "8080-8082:8080"
```

### Datenbank-Optimierung

```sql
-- Indizes für bessere Performance
CREATE INDEX idx_telemetry_timestamp ON telemetry(ts);
CREATE INDEX idx_telemetry_site_device ON telemetry(site, device);
CREATE INDEX idx_telemetry_recent ON telemetry(ts DESC);
```

## 🎯 BESS-Projekt-Zuordnung

### Übersicht

Die BESS-Projekt-Zuordnung ermöglicht es, mehrere Live-BESS-Systeme mit bestehenden Simulation-Projekten zu verknüpfen. Dies ermöglicht:

- **Multi-Projekt-Monitoring:** Verschiedene BESS-Systeme verschiedenen Projekten zuordnen
- **Automatische Synchronisation:** Live-Daten automatisch in Projekte integrieren
- **Technische Parameter:** BESS-spezifische Konfiguration pro Projekt
- **Zentrale Verwaltung:** Alle Zuordnungen über Admin-Interface verwalten

### Zugriff auf BESS-Zuordnung

#### 1. Über das Hauptmenü:
```
Admin-Dashboard → BESS-Zuordnung
```

#### 2. Direkte URL:
```
http://localhost:5000/admin/bess-mappings
```

### Neue BESS-Zuordnung erstellen

#### Schritt-für-Schritt Anleitung:

**1. Admin-Dashboard öffnen:**
- Klicken Sie auf **"Admin-Dashboard"** in der oberen Navigationsleiste
- Wählen Sie **"BESS-Zuordnung"** aus dem Dropdown-Menü

**2. "Neue Zuordnung" klicken:**
- Klicken Sie auf den **"+ Neue Zuordnung"** Button
- Das Zuordnungsformular wird geöffnet

**3. Projekt auswählen:**
- **Projekt:** Wählen Sie das gewünschte Projekt aus dem Dropdown
- Nur aktive Projekte werden angezeigt

**4. BESS-System konfigurieren:**
- **Site:** Standort-ID des BESS (z.B. "site1", "standort_a")
- **Device:** Geräte-ID des BESS (z.B. "bess1", "speicher_01")
- **BESS-Name:** Beschreibender Name (z.B. "Hauptspeicher Standort A")

**5. Technische Parameter eingeben:**
- **Standort:** Physische Adresse oder Beschreibung
- **Hersteller:** BESS-Hersteller (z.B. "Tesla", "Samsung")
- **Modell:** BESS-Modell (z.B. "Powerpack 2", "SDI E3")
- **Nennleistung (kW):** Maximale Lade-/Entladeleistung
- **Nennenergie (kWh):** Gesamtspeicherkapazität
- **Max. SOC (%):** Oberer SOC-Limit (Standard: 100%)
- **Min. SOC (%):** Unterer SOC-Limit (Standard: 0%)

**6. Synchronisation konfigurieren:**
- **Auto-Sync aktivieren:** Automatische Datensynchronisation
- **Sync-Intervall (Minuten):** Häufigkeit der Synchronisation (Standard: 5 Min)
- **Beschreibung:** Zusätzliche Notizen zur Zuordnung

**7. Speichern:**
- Klicken Sie auf **"Zuordnung erstellen"**
- Die Zuordnung wird in der Datenbank gespeichert

### BESS-Zuordnung bearbeiten

**1. Zuordnung auswählen:**
- Klicken Sie auf die gewünschte Zuordnung in der Liste
- Oder verwenden Sie den **"Bearbeiten"** Button

**2. Parameter ändern:**
- Alle Felder können nachträglich geändert werden
- Technische Parameter werden sofort aktualisiert

**3. Speichern:**
- Klicken Sie auf **"Änderungen speichern"**

### BESS-Zuordnung löschen

**1. Zuordnung auswählen:**
- Klicken Sie auf die gewünschte Zuordnung
- Klicken Sie auf **"Löschen"**

**2. Bestätigen:**
- Bestätigen Sie die Löschung
- **Achtung:** Alle zugehörigen Telemetrie-Daten werden ebenfalls gelöscht

### Projekt-spezifische Live-Daten

#### Zugriff über Projektliste:

**1. Projekte öffnen:**
- Navigieren Sie zu **"Projekte"** im Hauptmenü
- Klicken Sie auf ein Projekt

**2. Live-Daten auswählen:**
- Klicken Sie auf das **Drei-Punkte-Menü** (⋮) des Projekts
- Wählen Sie **"Live BESS Daten"**

#### Direkte URL:
```
http://localhost:5000/live-data/project/[PROJEKT-ID]
```

#### Dashboard-Features:

**1. Projekt-Informationen:**
- Projektname und -beschreibung
- Anzahl zugeordneter BESS-Systeme
- Letzte Synchronisation

**2. BESS-Systeme:**
- Liste aller zugeordneten BESS-Systeme
- Status jedes Systems (Online/Offline)
- Technische Parameter

**3. Live-Telemetrie:**
- Aktuelle SOC-Werte
- Lade-/Entladeleistung
- Temperatur-Status
- Alarm-Status

**4. Synchronisation:**
- Manuelle Synchronisation starten
- Auto-Sync-Status
- Letzte Datenaktualisierung

### MQTT-Topic-Generierung

Das System generiert automatisch MQTT-Topics basierend auf der Zuordnung:

```
bess/{site}/{device}/telemetry
```

**Beispiele:**
- Projekt "Hinterstoder": `bess/hinterstoder/bess1/telemetry`
- Projekt "Wien": `bess/wien/speicher_01/telemetry`
- Projekt "Salzburg": `bess/salzburg/main_bess/telemetry`

### API-Endpunkte für Zuordnungen

#### 1. Alle Zuordnungen abrufen:
```http
GET /api/admin/bess-mappings
Authorization: Bearer [TOKEN]
```

#### 2. Projekt-spezifische Zuordnungen:
```http
GET /api/admin/bess-mappings?project_id=1
Authorization: Bearer [TOKEN]
```

#### 3. Neue Zuordnung erstellen:
```http
POST /api/admin/bess-mappings
Authorization: Bearer [TOKEN]
Content-Type: application/json

{
  "project_id": 1,
  "site": "site1",
  "device": "bess1",
  "bess_name": "Hauptspeicher",
  "location": "Standort A",
  "manufacturer": "Tesla",
  "model": "Powerpack 2",
  "rated_power_kw": 250.0,
  "rated_energy_kwh": 500.0,
  "auto_sync": true,
  "sync_interval_minutes": 5
}
```

#### 4. Zuordnung aktualisieren:
```http
PUT /api/admin/bess-mappings/[ID]
Authorization: Bearer [TOKEN]
Content-Type: application/json

{
  "bess_name": "Neuer Name",
  "auto_sync": false
}
```

#### 5. Zuordnung löschen:
```http
DELETE /api/admin/bess-mappings/[ID]
Authorization: Bearer [TOKEN]
```

### Datenbank-Schema

#### BESSProjectMapping Tabelle:
```sql
CREATE TABLE bess_project_mapping (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    site VARCHAR(50) NOT NULL,
    device VARCHAR(50) NOT NULL,
    bess_name VARCHAR(100),
    is_active BOOLEAN DEFAULT 1,
    auto_sync BOOLEAN DEFAULT 1,
    sync_interval_minutes INTEGER DEFAULT 5,
    description TEXT,
    location VARCHAR(200),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    rated_power_kw FLOAT,
    rated_energy_kwh FLOAT,
    max_soc_percent FLOAT DEFAULT 100.0,
    min_soc_percent FLOAT DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_sync DATETIME,
    UNIQUE(site, device)
);
```

#### BESSTelemetryData Tabelle:
```sql
CREATE TABLE bess_telemetry_data (
    id INTEGER PRIMARY KEY,
    bess_mapping_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    soc_percent FLOAT,
    power_kw FLOAT,
    power_charge_kw FLOAT,
    power_discharge_kw FLOAT,
    voltage_dc_v FLOAT,
    current_dc_a FLOAT,
    temperature_max_c FLOAT,
    soh_percent FLOAT,
    alarms TEXT,
    data_quality VARCHAR(20) DEFAULT 'good',
    source VARCHAR(20) DEFAULT 'mqtt',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Best Practices

#### 1. Namenskonventionen:
- **Site:** Verwenden Sie konsistente Standort-IDs (z.B. "hinterstoder", "wien_zentrum")
- **Device:** Eindeutige Geräte-IDs (z.B. "bess_01", "speicher_haupt")
- **BESS-Name:** Beschreibende Namen für bessere Übersicht

#### 2. Technische Parameter:
- **Nennleistung:** Reale maximale Lade-/Entladeleistung
- **Nennenergie:** Reale Gesamtspeicherkapazität
- **SOC-Limits:** Hersteller-spezifische Limits beachten

#### 3. Synchronisation:
- **Auto-Sync:** Aktivieren für kontinuierliche Überwachung
- **Sync-Intervall:** An Datenqualität anpassen (1-15 Minuten)
- **Manuelle Sync:** Bei Bedarf für sofortige Aktualisierung

#### 4. Monitoring:
- **Regelmäßige Überprüfung:** BESS-Status regelmäßig kontrollieren
- **Alarm-Überwachung:** Alarm-Status im Dashboard verfolgen
- **Datenqualität:** Auf "data_quality" Status achten

### Troubleshooting BESS-Zuordnung

#### 1. Keine Zuordnungen sichtbar:
```bash
# Datenbank prüfen
sqlite3 instance/bess.db "SELECT COUNT(*) FROM bess_project_mapping;"

# Migration ausführen
python migrate_bess_project_mapping.py
```

#### 2. Zuordnung kann nicht erstellt werden:
```bash
# Eindeutigkeit prüfen
sqlite3 instance/bess.db "SELECT site, device FROM bess_project_mapping;"

# Projekt-ID prüfen
sqlite3 instance/bess.db "SELECT id, name FROM project;"
```

#### 3. Auto-Sync funktioniert nicht:
```bash
# MQTT-Verbindung prüfen
grep "MQTT" logs/app.log

# FastAPI-Status prüfen
curl -H "Authorization: Bearer changeme_token_123" \
     http://localhost:8080/healthz
```

#### 4. Projekt-spezifische Daten fehlen:
```bash
# Zuordnung prüfen
sqlite3 instance/bess.db "SELECT * FROM bess_project_mapping WHERE project_id=1;"

# Telemetrie-Daten prüfen
sqlite3 instance/bess.db "SELECT COUNT(*) FROM bess_telemetry_data WHERE bess_mapping_id=1;"
```

## 📞 Support

### Logs sammeln für Support

```bash
# Vollständiges Log-Paket erstellen
tar -czf bess_logs_$(date +%Y%m%d).tar.gz \
    logs/ \
    live/data/ \
    live/logs/ \
    docker-compose.yml \
    .env
```

### Kontakt

Bei Problemen oder Fragen:
1. Logs prüfen (siehe Troubleshooting)
2. System-Status Dashboard verwenden
3. Dokumentation durchgehen
4. Support-Team kontaktieren

---

**Letzte Aktualisierung:** 14. Januar 2025  
**Version:** 1.0  
**Autor:** BESS-Simulation Team
