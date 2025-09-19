# Live BESS Integration - Anleitung

## 📋 Übersicht

Die Live BESS Integration ermöglicht es, echte BESS-Speicherdaten in die BESS-Simulation zu integrieren. Das System unterstützt sowohl FastAPI-basierte als auch direkte MQTT-Verbindungen.

## 🚀 Phase 1 - Grundintegration (Abgeschlossen)

### ✅ Implementierte Features

1. **Live-Daten Service** (`app/live_data_service.py`)
   - FastAPI Integration für Live-Daten
   - MQTT Bridge Support (optional)
   - Automatische Fallback-Mechanismen
   - Datenkonvertierung und -normalisierung

2. **Live-Daten Dashboard** (`app/templates/live_data_dashboard.html`)
   - System-Status Anzeige
   - Real-time Charts (SOC, Leistung, Spannung, Temperatur)
   - Statistiken und Geräteinformationen
   - Responsive Design mit Tailwind CSS

3. **API Endpoints**
   - `/live-data` - Hauptdashboard
   - `/api/live-data/status` - System-Status
   - `/api/live-data/latest` - Neueste Daten
   - `/api/live-data/summary` - Gerätezusammenfassung
   - `/api/live-data/chart` - Chart-Daten

## 🚀 Phase 2 - Erweiterte Features (Abgeschlossen)

### ✅ Implementierte Features

1. **MQTT Bridge** (`app/mqtt_bridge.py`)
   - Direkte MQTT-Verbindung zu BESS-Systemen
   - Automatische Datenbank-Speicherung
   - Real-time Datenverarbeitung
   - Callback-System für Live-Updates

2. **Erweiterte Dashboard** (`app/templates/live_data_dashboard_advanced.html`)
   - Real-time Updates mit WebSocket
   - Auto-Refresh Konfiguration
   - Alarm-Management
   - Erweiterte Chart-Funktionen
   - Geräte-Tabelle mit Live-Daten

3. **Konfigurationssystem**
   - Umgebungsvariablen für flexible Konfiguration
   - MQTT/FastAPI Fallback-System
   - Konfigurationsdatei (`live_integration_config.env`)

## 🔧 Installation und Konfiguration

### 1. Abhängigkeiten installieren

```bash
pip install paho-mqtt
```

### 2. Umgebungsvariablen konfigurieren

Erstellen Sie eine `.env` Datei oder setzen Sie die folgenden Variablen:

```bash
# FastAPI Service (Standard)
LIVE_BESS_API_URL=http://localhost:8080
LIVE_BESS_API_TOKEN=changeme_token_123

# MQTT Bridge (Optional)
USE_MQTT_BRIDGE=false
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=bessuser
MQTT_PASSWORD=besspass
MQTT_BASE_TOPIC=bess

# Datenbank
LIVE_BESS_DB_PATH=live/data/bess.db
```

### 3. Live-BESS System starten

```bash
# Im live/ Verzeichnis
cd live
docker-compose up -d
```

### 4. MQTT-Integration aktivieren (Optional)

```bash
# Umgebungsvariable setzen
export USE_MQTT_BRIDGE=true

# Server neu starten
python run.py
```

## 📊 Verwendung

### Standard Dashboard

1. Navigieren Sie zu **Daten > Live BESS Daten**
2. Das Dashboard zeigt:
   - System-Verbindungsstatus
   - Aktuelle BESS-Parameter
   - Real-time Charts
   - Statistiken

### Erweiterte Dashboard

1. Navigieren Sie zu **Daten > Live Dashboard (Advanced)**
2. Features:
   - Auto-Refresh (10s - 5min)
   - WebSocket Real-time Updates
   - Alarm-Management
   - Erweiterte Chart-Konfiguration
   - Geräte-Tabelle

## 🔌 Datenformat

### MQTT Topic Structure
```
bess/{site}/{device}/telemetry
```

### JSON Datenformat
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

## 🚨 Alarm-Konfiguration

Das System überwacht automatisch:

- **SOC**: Niedrig (< 20%), Hoch (> 90%)
- **Temperatur**: Hoch (> 45°C)
- **Spannung**: Abnormale Werte (< 700V oder > 800V)

Alarme werden im Advanced Dashboard angezeigt.

## 📈 API Verwendung

### System-Status abrufen
```bash
curl -H "Authorization: Bearer your_token" \
     http://localhost:5000/api/live-data/status
```

### Neueste Daten abrufen
```bash
curl -H "Authorization: Bearer your_token" \
     http://localhost:5000/api/live-data/latest?limit=10
```

### Chart-Daten abrufen
```bash
curl -H "Authorization: Bearer your_token" \
     http://localhost:5000/api/live-data/chart?hours=24
```

## 🔧 Troubleshooting

### MQTT-Verbindung fehlgeschlagen
1. Prüfen Sie MQTT-Broker Status: `docker ps`
2. Überprüfen Sie Credentials in `.env`
3. Testen Sie MQTT-Verbindung: `python live/examples/mqtt_sample_publisher.py`

### FastAPI nicht erreichbar
1. Prüfen Sie FastAPI-Service: `curl http://localhost:8080/healthz`
2. Überprüfen Sie API-Token in Konfiguration
3. Prüfen Sie Firewall-Einstellungen

### Keine Daten im Dashboard
1. Prüfen Sie Logs: `tail -f logs/bess_simulation.log`
2. Testen Sie API-Endpoints direkt
3. Überprüfen Sie Datenbank: `sqlite3 live/data/bess.db "SELECT COUNT(*) FROM live_bess_telemetry;"`

## 🔄 Erweiterte Konfiguration

### MQTT SSL/TLS aktivieren

1. Zertifikate in `live/mosquitto/certs/` ablegen
2. `live/mosquitto/mosquitto.conf` anpassen:
```conf
listener 8883
cafile /mosquitto/config/certs/ca.crt
certfile /mosquitto/config/certs/server.crt
keyfile /mosquitto/config/certs/server.key
```

3. Docker-Compose Port ändern: `8883:8883`

### Performance-Optimierung

1. **Datenbank-Indexierung**: Automatisch konfiguriert
2. **Chart-Updates**: Reduzieren Sie Update-Intervall bei großen Datenmengen
3. **Memory-Management**: Begrenzen Sie `limit` Parameter in API-Calls

## 📝 Logs und Monitoring

### Log-Level anpassen
```bash
export LOG_LEVEL=DEBUG
export LOG_MQTT_MESSAGES=true
```

### Performance-Monitoring
```bash
# Datenbank-Größe prüfen
du -h live/data/bess.db

# Anzahl Datensätze
sqlite3 live/data/bess.db "SELECT COUNT(*) FROM live_bess_telemetry;"

# Neueste Datensätze
sqlite3 live/data/bess.db "SELECT * FROM live_bess_telemetry ORDER BY created_at DESC LIMIT 5;"
```

## 🎯 Nächste Schritte (Phase 3)

Geplante Erweiterungen:
- [ ] Export-Funktionen (CSV, Excel, PDF)
- [ ] Historische Datenanalyse
- [ ] Predictive Analytics
- [ ] Multi-Site Management
- [ ] Benachrichtigungs-System (Email, SMS)
- [ ] REST API für externe Systeme
- [ ] Grafana Integration
- [ ] Mobile App Support

## 📞 Support

Bei Problemen oder Fragen:
1. Prüfen Sie die Logs in `logs/bess_simulation.log`
2. Testen Sie die API-Endpoints direkt
3. Überprüfen Sie die Konfiguration
4. Konsultieren Sie diese Dokumentation

---

**Status**: Phase 2 abgeschlossen ✅  
**Version**: 1.0  
**Letzte Aktualisierung**: 19. September 2025
