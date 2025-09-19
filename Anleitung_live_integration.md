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
